from experiment_os.repositories.wiki import WikiRepository
from experiment_os.services.issues import GitHubIssueIngestor, _claims_from_issue


def test_issue_claim_extraction_includes_versions():
    issue = {
        "number": 123,
        "title": "Migration default regression",
        "body": """
### What version of `drizzle-orm` are you using?
1.0.0-beta.22

### What version of `drizzle-kit` are you using?
1.0.0-beta.22

Generate migrations after changing a default value.
Workaround: pin the old generator until the migration fix is released.
Fixed in the latest beta, but migration compatibility is risky.
""",
    }

    claims = _claims_from_issue("drizzle-team/drizzle-orm", issue, "source.github-issue.test")
    version_claim = next(claim for claim in claims if claim.metadata["claim_type"] == "version_note")

    assert version_claim.metadata["versions"] == {
        "drizzle-orm": "1.0.0-beta.22",
        "drizzle-kit": "1.0.0-beta.22",
    }
    reproduction_claim = next(
        claim for claim in claims if claim.metadata["claim_type"] == "reproduction_signal"
    )
    assert reproduction_claim.metadata["review"]["allowed_use"] == "evidence_only"
    assert reproduction_claim.metadata["source_page_id"] == "source.github-issue.test"
    assert reproduction_claim.metadata["symptom"]
    assert "Workaround" in reproduction_claim.metadata["workaround"]
    assert "Fixed" in reproduction_claim.metadata["verified_fix"]
    assert reproduction_claim.metadata["risk"]


def test_issue_ingestor_can_run_end_to_end_from_local_issue_payload(session):
    result = GitHubIssueIngestor(session).ingest(
        repo="openai/openai-python",
        query="responses migration",
        issues=[
            {
                "number": 2677,
                "title": "Responses migration tool call incompatibility",
                "body": """
### What version of `openai` are you using?
2.21.0

Migration from chat completions to responses fails when tool calls are replayed.
Workaround: inspect local response parsing before changing app code.
""",
                "html_url": "https://github.com/openai/openai-python/issues/2677",
                "url": "https://api.github.com/repos/openai/openai-python/issues/2677",
                "state": "open",
                "labels": [{"name": "bug"}],
            }
        ],
    )

    wiki = WikiRepository(session)
    card = wiki.get_page(result["knowledge_card"])
    version_claim = wiki.get_page("claim.github-issue.openai.openai-python.2677.versions")

    assert result["issues"] == 1
    assert result["claims"] >= 2
    assert result["allowed_use"] == "evidence_only_until_verified_locally"
    assert card is not None
    assert card.page_metadata["allowed_use"] == "evidence_only"
    assert version_claim is not None
    assert version_claim.page_metadata["allowed_use"] == "evidence_only"
