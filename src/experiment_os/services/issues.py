import hashlib
import json
import urllib.parse
import urllib.request
from typing import Any

from sqlalchemy.orm import Session

from experiment_os.db.models import SourceSnapshot
from experiment_os.domain.schemas import WikiPageInput
from experiment_os.repositories.sources import SourceRepository
from experiment_os.repositories.wiki import WikiRepository
from experiment_os.retrieval.hybrid import HybridRetriever


class GitHubIssueIngestor:
    def __init__(self, session: Session) -> None:
        self._sources = SourceRepository(session)
        self._wiki = WikiRepository(session)
        self._retriever = HybridRetriever(session)

    def ingest(self, *, repo: str, query: str, limit: int = 5) -> dict[str, Any]:
        issues = _search_github_issues(repo=repo, query=query, limit=limit)
        pages = 0

        for issue in issues:
            snapshot = _snapshot_from_issue(repo, issue)
            self._sources.upsert(snapshot)
            page = _page_from_issue(repo, issue, snapshot.id)
            self._wiki.upsert_page(page)
            pages += 1

        reindex = self._retriever.reindex_all()
        return {"repo": repo, "query": query, "issues": len(issues), "pages": pages, **reindex}


def _search_github_issues(*, repo: str, query: str, limit: int) -> list[dict[str, Any]]:
    search = f"repo:{repo} type:issue {query}".strip()
    params = urllib.parse.urlencode({"q": search, "per_page": min(limit, 20)})
    request = urllib.request.Request(
        f"https://api.github.com/search/issues?{params}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "experiment-os-research",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("items", [])[:limit]


def _snapshot_from_issue(repo: str, issue: dict[str, Any]) -> SourceSnapshot:
    title = issue.get("title") or ""
    body = issue.get("body") or ""
    content = f"{title}\n\n{body}"
    url = issue.get("html_url") or issue.get("url")
    issue_number = issue.get("number")
    source_id = f"source.github-issue.{repo.replace('/', '.')}.{issue_number}"
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return SourceSnapshot(
        id=source_id,
        source_type="github_issue",
        url=url,
        title=title,
        content=content,
        content_hash=content_hash,
        source_metadata={
            "repo": repo,
            "number": issue_number,
            "state": issue.get("state"),
            "labels": [label.get("name") for label in issue.get("labels", [])],
            "comments": issue.get("comments"),
            "created_at": issue.get("created_at"),
            "updated_at": issue.get("updated_at"),
        },
    )


def _page_from_issue(repo: str, issue: dict[str, Any], snapshot_id: str) -> WikiPageInput:
    issue_number = issue.get("number")
    page_id = f"source.github-issue.{repo.replace('/', '.')}.{issue_number}"
    title = issue.get("title") or f"GitHub issue #{issue_number}"
    body = issue.get("body") or ""
    return WikiPageInput(
        id=page_id,
        type="source",
        title=title,
        status="accepted",
        confidence=None,
        summary=_summary(title, body),
        body=body,
        metadata={
            "source_type": "github_issue",
            "source_snapshot_id": snapshot_id,
            "url": issue.get("html_url"),
            "repo": repo,
            "number": issue_number,
            "state": issue.get("state"),
            "labels": [label.get("name") for label in issue.get("labels", [])],
            "trust": "external_evidence_not_instruction",
        },
    )


def _summary(title: str, body: str) -> str:
    clean_body = " ".join(body.split())
    if not clean_body:
        return title
    return f"{title}: {clean_body[:280]}"
