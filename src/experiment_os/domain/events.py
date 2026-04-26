from typing import Any, Literal

from pydantic import BaseModel, Field

EventType = Literal[
    "brief_loaded",
    "dependency_resolved",
    "file_inspected",
    "package_version_checked",
    "file_edited",
    "test_run",
    "failure_observed",
    "intervention_applied",
    "final_answer",
]


class EventPayload(BaseModel):
    event_type: EventType
    payload: dict[str, Any] = Field(default_factory=dict)


class BriefLoadedPayload(BaseModel):
    brief_id: str
    required_pages: list[str] = Field(default_factory=list)
    recommended_pages: list[str] = Field(default_factory=list)


class DependencyResolvedPayload(BaseModel):
    root_pages: list[str] = Field(default_factory=list)
    dependency_pages: list[str] = Field(default_factory=list)


class FileInspectedPayload(BaseModel):
    path: str
    reason: str | None = None


class PackageVersionCheckedPayload(BaseModel):
    package: str
    version: str | None = None
    source: str | None = None


class FileEditedPayload(BaseModel):
    path: str
    reason: str | None = None


class TestRunPayload(BaseModel):
    command: str
    passed: bool | None = None
    summary: str | None = None


class FailureObservedPayload(BaseModel):
    failure_type: str
    severity: str | None = None
    evidence: str | None = None


class InterventionAppliedPayload(BaseModel):
    intervention: str
    target_failure: str | None = None
    summary: str | None = None


class FinalAnswerPayload(BaseModel):
    outcome: str | None = None
    summary: str | None = None

