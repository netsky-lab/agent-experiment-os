from typing import Any

from sqlalchemy.orm import Session

from experiment_os.domain.schemas import BriefRequest, RunEventInput, RunStartInput
from experiment_os.repositories.briefs import BriefRepository
from experiment_os.services.agent_presentation import AgentWorkContextPresenter
from experiment_os.services.agent_graph import AgentDependencyGraphPresenter
from experiment_os.services.briefs import BriefCompiler
from experiment_os.services.dependencies import DependencyResolver
from experiment_os.services.runs import RunRecorder
from experiment_os.services.serialization import brief_to_dict


class AgentWorkProtocol:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._briefs = BriefRepository(session)
        self._recorder = RunRecorder(session)

    def start(
        self,
        *,
        request: BriefRequest,
        run: RunStartInput | None = None,
        dependency_depth: int = 2,
    ) -> dict[str, Any]:
        brief = BriefCompiler(self._session).compile(request)
        dependencies = DependencyResolver(self._session).resolve(
            brief["required_pages"],
            depth=dependency_depth,
            token_budget=request.token_budget,
        )
        agent_graph = AgentDependencyGraphPresenter().present(
            required_pages=brief["required_pages"],
            recommended_pages=brief["recommended_pages"],
            dependency_graph=dependencies.model_dump(),
        )
        run_record = self._recorder.start_run(run) if run else None
        if run_record:
            self._recorder.record_event(
                RunEventInput(
                    run_id=run_record["run_id"],
                    event_type="brief_loaded",
                    payload={
                        "brief_id": brief["brief_id"],
                        "required_pages": brief["required_pages"],
                        "recommended_pages": brief["recommended_pages"],
                    },
                )
            )
            self._recorder.record_event(
                RunEventInput(
                    run_id=run_record["run_id"],
                    event_type="dependency_resolved",
                    payload={
                        "root_pages": dependencies.root_pages,
                        "dependency_pages": [page["id"] for page in dependencies.pages],
                    },
                )
            )

        agent_work_context = AgentWorkContextPresenter().present(
            request=request,
            brief=brief,
            dependencies=dependencies.model_dump(),
            agent_dependency_graph=agent_graph,
            run=run_record,
        )

        return {
            "protocol": "experiment_os.pre_work.v1",
            "brief": brief,
            "dependencies": dependencies.model_dump(),
            "agent_dependency_graph": agent_graph,
            "agent_work_context": agent_work_context,
            "run": run_record,
            "next_actions": agent_work_context["tool_sequence"],
        }

    def agent_graph_for_brief(self, brief_id: str, *, dependency_depth: int = 2) -> dict[str, Any]:
        brief = self._briefs.get(brief_id)
        if brief is None:
            raise ValueError(f"Unknown brief_id: {brief_id}")
        data = brief_to_dict(brief)
        dependencies = DependencyResolver(self._session).resolve(
            data["required_pages"],
            depth=dependency_depth,
            token_budget=data["token_budget"],
        )
        return AgentDependencyGraphPresenter().present(
            required_pages=data["required_pages"],
            recommended_pages=data["recommended_pages"],
            dependency_graph=dependencies.model_dump(),
        )

    def agent_work_context_for_brief(
        self,
        brief_id: str,
        *,
        dependency_depth: int = 2,
    ) -> dict[str, Any]:
        brief = self._briefs.get(brief_id)
        if brief is None:
            raise ValueError(f"Unknown brief_id: {brief_id}")
        data = brief_to_dict(brief)
        request = BriefRequest(
            task=data["task"],
            repo=data["repo"],
            libraries=data["libraries"],
            agent=data["agent"],
            model=data["model"],
            toolchain=data["toolchain"],
            token_budget=data["token_budget"],
        )
        dependencies = DependencyResolver(self._session).resolve(
            data["required_pages"],
            depth=dependency_depth,
            token_budget=data["token_budget"],
        )
        agent_graph = AgentDependencyGraphPresenter().present(
            required_pages=data["required_pages"],
            recommended_pages=data["recommended_pages"],
            dependency_graph=dependencies.model_dump(),
        )
        return AgentWorkContextPresenter().present(
            request=request,
            brief=data,
            dependencies=dependencies.model_dump(),
            agent_dependency_graph=agent_graph,
            run=None,
        )
