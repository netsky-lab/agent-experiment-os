from typing import Any

from experiment_os.db.models import Brief, Run, RunEvent, WikiPage


def page_to_dict(page: WikiPage, *, include_body: bool = False) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": page.id,
        "type": page.type,
        "title": page.title,
        "status": page.status,
        "confidence": page.confidence,
        "summary": page.summary,
        "metadata": page.page_metadata,
    }
    if include_body:
        data["body"] = page.body
    return data


def brief_to_dict(brief: Brief) -> dict[str, Any]:
    return {
        "brief_id": brief.id,
        "task": brief.task,
        "repo": brief.repo,
        "libraries": brief.libraries,
        "agent": brief.agent,
        "model": brief.model,
        "toolchain": brief.toolchain,
        "token_budget": brief.token_budget,
        "required_pages": brief.required_pages,
        "recommended_pages": brief.recommended_pages,
        "content": brief.content,
        "created_at": brief.created_at.isoformat() if brief.created_at else None,
    }


def run_to_dict(run: Run) -> dict[str, Any]:
    return {
        "run_id": run.id,
        "task": run.task,
        "repo": run.repo,
        "agent": run.agent,
        "model": run.model,
        "toolchain": run.toolchain,
        "status": run.status,
        "metadata": run.run_metadata,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "ended_at": run.ended_at.isoformat() if run.ended_at else None,
    }


def event_to_dict(event: RunEvent) -> dict[str, Any]:
    return {
        "event_id": str(event.id),
        "run_id": event.run_id,
        "step_index": event.step_index,
        "event_type": event.event_type,
        "payload": event.payload,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }

