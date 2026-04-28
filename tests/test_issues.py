from experiment_os.services.issues import _claims_from_issue


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
