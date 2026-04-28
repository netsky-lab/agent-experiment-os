from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from pathlib import Path

from experiment_os.database import check_database, session_scope
from experiment_os.domain.schemas import BriefRequest
from experiment_os.retrieval.hybrid import HybridRetriever
from experiment_os.services.agent_actions import AgentActionService
from experiment_os.services.briefs import BriefCompiler
from experiment_os.services.completion import CompletionContractService
from experiment_os.services.dashboard import DashboardReadService
from experiment_os.services.experiment_lifecycle import ExperimentLifecycleService
from experiment_os.services.issues import GitHubIssueIngestor
from experiment_os.services.provenance import ProvenanceService
from experiment_os.services.protocol import AgentWorkProtocol
from experiment_os.services.review import ReviewService


class StatusUpdate(BaseModel):
    status: str
    rationale: str | None = None
    reviewer: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class PromotionRequest(BaseModel):
    title: str | None = None
    applies_to: dict[str, Any] | None = None
    mitigates: list[str] = Field(default_factory=list)


class ExperimentStatusUpdate(BaseModel):
    status: str
    rationale: str | None = None


class VersionAlignmentRequest(BaseModel):
    local_versions: dict[str, str] = Field(default_factory=dict)


class KnowledgeSearchRequest(BaseModel):
    query: str
    limit: int = 8
    libraries: list[str] = Field(default_factory=list)
    page_types: list[str] = Field(default_factory=list)
    status: str | None = "accepted"


class IssueKnowledgeSearchRequest(BaseModel):
    library: str
    topic: str
    version: str | None = None
    limit: int = 8


def create_app() -> FastAPI:
    app = FastAPI(title="Experiment OS API", version="0.1.0")
    static_dir = Path(__file__).resolve().parents[2] / "web"
    if static_dir.exists():
        app.mount("/app", StaticFiles(directory=static_dir, html=True), name="app")

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "database": check_database()}

    @app.get("/experiments")
    def list_experiments() -> dict[str, Any]:
        with session_scope() as session:
            return DashboardReadService(session).list_experiments()

    @app.get("/experiments/{experiment_id}")
    def experiment_detail(experiment_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).experiment_detail(experiment_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/experiments/{experiment_id}/matrix")
    def experiment_matrix(experiment_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).experiment_matrix(experiment_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/experiments/{experiment_id}/matrix/latest")
    def latest_experiment_matrix(experiment_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).latest_experiment_matrix(experiment_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/experiments/{experiment_id}/matrix/latest-comparison")
    def latest_matrix_comparison_candidate(experiment_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).latest_matrix_comparison_candidate(
                    experiment_id
                )
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/experiments/{experiment_id}/story")
    def experiment_story(experiment_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).experiment_story(experiment_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/experiments/{experiment_id}/protocol-compliance")
    def protocol_compliance(experiment_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).protocol_compliance(experiment_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/experiments/{experiment_id}/matrix/compare")
    def compare_matrices(
        experiment_id: str,
        left_matrix_id: str,
        right_matrix_id: str,
    ) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).matrix_comparison(
                    experiment_id,
                    left_matrix_id=left_matrix_id,
                    right_matrix_id=right_matrix_id,
                )
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/experiments/{experiment_id}/matrix/regression")
    def matrix_regression(
        experiment_id: str,
        left_matrix_id: str,
        right_matrix_id: str,
    ) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).matrix_regression(
                    experiment_id,
                    left_matrix_id=left_matrix_id,
                    right_matrix_id=right_matrix_id,
                )
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.post("/experiments/{experiment_id}/status")
    def set_experiment_status(
        experiment_id: str,
        update: ExperimentStatusUpdate,
    ) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return ExperimentLifecycleService(session).set_status(
                    experiment_id,
                    update.status,
                    rationale=update.rationale,
                )
            except ValueError as error:
                raise HTTPException(status_code=400, detail=str(error)) from error

    @app.get("/runs/{run_id}")
    def run_detail(run_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).run_detail(run_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/runs/{run_id}/churn")
    def run_churn(run_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).run_churn(run_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/runs/{run_id}/completion-contract")
    def run_completion_contract(run_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return CompletionContractService(session).validate(run_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/runs/{run_id}/next-required-action")
    def run_next_required_action(run_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return AgentActionService(session).next_required_action(run_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/experiments/{experiment_id}/churn")
    def experiment_churn(
        experiment_id: str,
        matrix_id: str | None = None,
    ) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).experiment_churn(
                    experiment_id,
                    matrix_id=matrix_id,
                )
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/experiments/{experiment_id}/churn/latest")
    def latest_churn_runs(experiment_id: str, limit: int = 20) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).latest_churn_runs(
                    experiment_id,
                    limit=limit,
                )
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.post("/briefs")
    def create_brief(request: BriefRequest) -> dict[str, Any]:
        with session_scope() as session:
            return BriefCompiler(session).compile(request)

    @app.get("/briefs/{brief_id}/agent-work-context")
    def agent_work_context(brief_id: str, dependency_depth: int = 2) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return AgentWorkProtocol(session).agent_work_context_for_brief(
                    brief_id,
                    dependency_depth=dependency_depth,
                )
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/briefs/{brief_id}/presentation-preview")
    def presentation_preview(brief_id: str, dependency_depth: int = 2) -> dict[str, Any]:
        with session_scope() as session:
            try:
                context = AgentWorkProtocol(session).agent_work_context_for_brief(
                    brief_id,
                    dependency_depth=dependency_depth,
                )
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error
            return {
                "brief_id": brief_id,
                "presentation_contract": context["presentation_contract"],
                "tool_sequence": context["tool_sequence"],
                "completion_contract": context["completion_contract"],
            }

    @app.post("/knowledge/search")
    def search_knowledge(request: KnowledgeSearchRequest) -> dict[str, Any]:
        with session_scope() as session:
            return {
                "query": request.query,
                "results": HybridRetriever(session).search(
                    request.query,
                    limit=request.limit,
                    libraries=request.libraries,
                    page_types=request.page_types,
                    status=request.status,
                ),
            }

    @app.post("/issue-knowledge/search")
    def search_issue_knowledge(request: IssueKnowledgeSearchRequest) -> dict[str, Any]:
        query = " ".join(
            part for part in [request.library, request.topic, request.version] if part
        )
        with session_scope() as session:
            results = HybridRetriever(session).search(
                query,
                limit=request.limit,
                libraries=[request.library],
                page_types=["source", "claim", "knowledge_card"],
                status=None,
            )
            return {"query": query, "results": results}

    @app.post("/issue-knowledge/{page_id}/version-alignment")
    def issue_version_alignment(
        page_id: str,
        request: VersionAlignmentRequest,
    ) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return GitHubIssueIngestor(session).version_alignment(
                    page_id=page_id,
                    local_versions=request.local_versions,
                )
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/review-queue")
    def review_queue(limit: int = 50) -> dict[str, Any]:
        with session_scope() as session:
            return DashboardReadService(session).review_queue(limit=limit)

    @app.get("/policy-candidates")
    def policy_candidates(limit: int = 50) -> dict[str, Any]:
        with session_scope() as session:
            return DashboardReadService(session).policy_candidates(limit=limit)

    @app.get("/policy-candidates/categories")
    def policy_candidate_categories(limit: int = 50) -> dict[str, Any]:
        with session_scope() as session:
            return DashboardReadService(session).policy_candidate_categories(limit=limit)

    @app.get("/briefs/{brief_id}/evidence-graph")
    def evidence_graph(brief_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).evidence_graph(brief_id=brief_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/review-actions/{page_id}")
    def review_actions(page_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).review_actions(page_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/pages/{page_id}/provenance")
    def page_provenance(page_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return ProvenanceService(session).page_provenance(page_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/wiki/graph")
    def wiki_graph() -> dict[str, Any]:
        with session_scope() as session:
            return DashboardReadService(session).wiki_graph()

    @app.get("/knowledge/stale")
    def stale_knowledge() -> dict[str, Any]:
        with session_scope() as session:
            return DashboardReadService(session).stale_knowledge()

    @app.get("/knowledge/duplicates")
    def duplicate_knowledge() -> dict[str, Any]:
        with session_scope() as session:
            return DashboardReadService(session).duplicate_knowledge()

    @app.get("/ui/contract")
    def ui_contract() -> dict[str, Any]:
        with session_scope() as session:
            return DashboardReadService(session).ui_contract()

    @app.get("/ui/bootstrap")
    def ui_bootstrap(experiment_id: str | None = None) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).ui_bootstrap(experiment_id=experiment_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.post("/review-actions/{page_id}/status")
    def set_status(page_id: str, update: StatusUpdate) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return ReviewService(session).set_status(
                    page_id,
                    update.status,
                    rationale=update.rationale,
                    reviewer=update.reviewer,
                    evidence_ids=update.evidence_ids,
                )
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.post("/claims/{claim_id}/promote/knowledge")
    def promote_knowledge(claim_id: str, request: PromotionRequest) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return ReviewService(session).promote_claim(claim_id, title=request.title)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.post("/claims/{claim_id}/promote/policy")
    def promote_policy(claim_id: str, request: PromotionRequest) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return ReviewService(session).promote_claim_to_policy(
                    claim_id,
                    title=request.title,
                    applies_to=request.applies_to,
                )
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.post("/claims/{claim_id}/promote/intervention")
    def promote_intervention(claim_id: str, request: PromotionRequest) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return ReviewService(session).promote_claim_to_intervention(
                    claim_id,
                    title=request.title,
                    mitigates=request.mitigates,
                )
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    return app


app = create_app()
