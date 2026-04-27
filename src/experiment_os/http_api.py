from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from experiment_os.database import check_database, session_scope
from experiment_os.services.dashboard import DashboardReadService
from experiment_os.services.review import ReviewService


class StatusUpdate(BaseModel):
    status: str


class PromotionRequest(BaseModel):
    title: str | None = None
    applies_to: dict[str, Any] | None = None
    mitigates: list[str] = Field(default_factory=list)


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

    @app.get("/runs/{run_id}")
    def run_detail(run_id: str) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return DashboardReadService(session).run_detail(run_id)
            except ValueError as error:
                raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/review-queue")
    def review_queue(limit: int = 50) -> dict[str, Any]:
        with session_scope() as session:
            return DashboardReadService(session).review_queue(limit=limit)

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

    @app.post("/review-actions/{page_id}/status")
    def set_status(page_id: str, update: StatusUpdate) -> dict[str, Any]:
        with session_scope() as session:
            try:
                return ReviewService(session).set_status(page_id, update.status)
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
