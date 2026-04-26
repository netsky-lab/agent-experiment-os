from experiment_os.services.dependencies import DependencyResolver


def test_dependency_resolver_expands_depends_on(session):
    graph = DependencyResolver(session).resolve(
        ["policy.opencode-gemma-shell-escaping"],
        depth=2,
    )
    page_ids = {page["id"] for page in graph.pages}

    assert "policy.opencode-gemma-shell-escaping" in page_ids
    assert "failure.tool-call-syntax-drift" in page_ids
    assert "intervention.command-normalization" in page_ids

