from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from experiment_os.database import check_database, session_scope
from experiment_os.domain.schemas import BriefRequest
from experiment_os.retrieval.hybrid import HybridRetriever
from experiment_os.services.briefs import BriefCompiler
from experiment_os.services.dashboard import DashboardReadService
from experiment_os.services.protocol import AgentWorkProtocol
from experiment_os.services.review import ReviewService


class StatusUpdate(BaseModel):
    status: str
    rationale: str | None = None
    reviewer: str | None = None


class PromotionRequest(BaseModel):
    title: str | None = None
    applies_to: dict[str, Any] | None = None
    mitigates: list[str] = Field(default_factory=list)


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

    @app.get("/review-queue")
    def review_queue(limit: int = 50) -> dict[str, Any]:
        with session_scope() as session:
            return DashboardReadService(session).review_queue(limit=limit)

    @app.get("/policy-candidates")
    def policy_candidates(limit: int = 50) -> dict[str, Any]:
        with session_scope() as session:
            return DashboardReadService(session).policy_candidates(limit=limit)

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

    @app.get("/ui/contract")
    def ui_contract() -> dict[str, Any]:
        with session_scope() as session:
            return DashboardReadService(session).ui_contract()

    @app.post("/review-actions/{page_id}/status")
    def set_status(page_id: str, update: StatusUpdate) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return ReviewService(session).set_status(
                    page_id,
                    update.status,
                    rationale=update.rationale,
                    reviewer=update.reviewer,
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
