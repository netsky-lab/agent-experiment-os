from typing import Any, Literal

from pydantic import BaseModel, Field


PageType = Literal[
    "source",
    "claim",
    "knowledge_card",
    "failure",
    "intervention",
    "policy",
    "experiment",
    "run_report",
]


class WikiPageInput(BaseModel):
    id: str
    type: PageType
    title: str
    status: str = "draft"
    confidence: str | None = None
    summary: str = ""
    body: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class PageEdge(BaseModel):
    source_page_id: str
    target_page_id: str
    edge_type: str = "dependsOn"
    metadata: dict[str, Any] = Field(default_factory=dict)


class BriefRequest(BaseModel):
    task: str
    repo: str | None = None
    libraries: list[str] = Field(default_factory=list)
    agent: str | None = None
    model: str | None = None
    toolchain: str | None = None
    token_budget: int = 2000


class DependencyGraph(BaseModel):
    root_pages: list[str]
    pages: list[dict[str, Any]]
    edges: list[dict[str, Any]] = Field(default_factory=list)
    truncated: bool = False


class RunStartInput(BaseModel):
    task: str
    repo: str | None = None
    agent: str | None = None
    model: str | None = None
    toolchain: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunEventInput(BaseModel):
    run_id: str
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    step_index: int | None = None


class ExperimentInput(BaseModel):
    id: str
    title: str
    hypothesis: str
    status: str = "draft"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentConditionInput(BaseModel):
    id: str
    experiment_id: str
    name: str
    description: str = ""
    config: dict[str, Any] = Field(default_factory=dict)


class RunArtifactInput(BaseModel):
    run_id: str
    artifact_type: str
    path: str
    content_type: str = "text/plain"
    metadata: dict[str, Any] = Field(default_factory=dict)
