import json
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from experiment_os.artifacts import ArtifactStore
from experiment_os.domain.schemas import BriefRequest, RunArtifactInput, RunEventInput
from experiment_os.repositories.runs import RunRepository
from experiment_os.services.agent_graph import AgentDependencyGraphPresenter
from experiment_os.services.agent_presentation import AgentWorkContextPresenter
from experiment_os.services.briefs import BriefCompiler
from experiment_os.services.dependencies import DependencyResolver
from experiment_os.services.runs import RunRecorder
from experiment_os.services.serialization import run_to_dict


@dataclass(frozen=True)
class AgentPreWorkResult:
    prompt: str
    env: dict[str, str] = field(default_factory=dict)
    brief_id: str | None = None
    context_artifact_path: str | None = None


class AgentPreWorkGate:
    """Adapter-side protocol gate that loads Experiment OS context before agent execution."""

    def __init__(self, session: Session, artifacts: ArtifactStore | None = None) -> None:
        self._session = session
        self._runs = RunRepository(session)
        self._recorder = RunRecorder(session)
        self._artifacts = artifacts or ArtifactStore()

    def prepare(
        self,
        *,
        run_id: str,
        request: BriefRequest,
        base_prompt: str | None,
        dependency_depth: int = 2,
    ) -> AgentPreWorkResult:
        run = self._runs.get_run(run_id)
        if run is None:
            raise ValueError(f"Unknown run_id: {run_id}")

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
        context = AgentWorkContextPresenter().present(
            request=request,
            brief=brief,
            dependencies=dependencies.model_dump(),
            agent_dependency_graph=agent_graph,
            run=run_to_dict(run),
        )

        self._record_pre_work_events(
            run_id=run_id,
            brief=brief,
            dependencies=dependencies.model_dump(),
            context=context,
        )
        prompt = _gated_prompt(context=context, base_prompt=base_prompt)
        context_path = self._artifacts.write_text(
            run_id=run_id,
            name="agent-work-context.json",
            content=json.dumps(
                {
                    "agent_work_context": context,
                    "agent_dependency_graph": agent_graph,
                    "dependencies": dependencies.model_dump(),
                },
                indent=2,
                sort_keys=True,
            ),
        )
        self._recorder.record_artifact(
            RunArtifactInput(
                run_id=run_id,
                artifact_type="agent_work_context",
                path=str(context_path),
                content_type="application/json",
                metadata={
                    "brief_id": brief["brief_id"],
                    "protocol": "experiment_os.pre_work.v1",
                    "gate": "adapter",
                },
            )
        )
        return AgentPreWorkResult(
            prompt=prompt,
            env={
                "EXPERIMENT_OS_AGENT_WORK_CONTEXT_PATH": str(context_path.resolve()),
                "EXPERIMENT_OS_BRIEF_ID": brief["brief_id"],
                "EXPERIMENT_OS_RUN_ID": run_id,
            },
            brief_id=brief["brief_id"],
            context_artifact_path=str(context_path),
        )

    def complete(self, *, run_id: str, stdout: str, stderr: str) -> None:
        final_answer = _extract_final_answer(stdout) or _tail_text(stdout, stderr)
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="mcp_tool_called",
                payload={
                    "server": "experiment_os",
                    "tool": "record_run_event",
                    "recorded_event_type": "final_answer",
                    "recorded_run_id": run_id,
                    "status": "completed",
                    "transport": "adapter_gate",
                },
            )
        )
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="final_answer",
                payload={"answer": final_answer, "source": "adapter_gate"},
            )
        )
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="mcp_tool_called",
                payload={
                    "server": "experiment_os",
                    "tool": "summarize_run",
                    "status": "completed",
                    "transport": "adapter_gate",
                },
            )
        )

    def _record_pre_work_events(
        self,
        *,
        run_id: str,
        brief: dict[str, Any],
        dependencies: dict[str, Any],
        context: dict[str, Any],
    ) -> None:
        for tool in (
            "start_pre_work_protocol",
            "get_agent_work_context",
            "get_agent_dependency_graph",
        ):
            self._recorder.record_event(
                RunEventInput(
                    run_id=run_id,
                    event_type="mcp_tool_called",
                    payload={
                        "server": "experiment_os",
                        "tool": tool,
                        "status": "completed",
                        "transport": "adapter_gate",
                    },
                )
            )
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="brief_loaded",
                payload={
                    "brief_id": brief["brief_id"],
                    "required_pages": brief["required_pages"],
                    "recommended_pages": brief["recommended_pages"],
                    "required_load_order": context["required_load_order"],
                    "gate": "adapter",
                },
            )
        )
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="dependency_resolved",
                payload={
                    "root_pages": dependencies["root_pages"],
                    "dependency_pages": [page["id"] for page in dependencies["pages"]],
                    "gate": "adapter",
                },
            )
        )


def _gated_prompt(*, context: dict[str, Any], base_prompt: str | None) -> str:
    return (
        "# Experiment OS Enforced Pre-work Context\n\n"
        "This context was loaded by the adapter before agent execution. Follow it before editing.\n\n"
        "```json\n"
        + json.dumps(context, indent=2, sort_keys=True)
        + "\n```\n\n"
        "# User Task\n\n"
        + (base_prompt or context["task"])
    )


def _extract_final_answer(stdout: str) -> str | None:
    answer: str | None = None
    for line in stdout.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = payload.get("item")
        if not isinstance(item, dict):
            continue
        if item.get("type") == "agent_message" and isinstance(item.get("text"), str):
            answer = item["text"]
    return answer


def _tail_text(stdout: str, stderr: str) -> str:
    text = stdout.strip() or stderr.strip()
    return text[-4000:] if text else "Agent execution produced no final text."
