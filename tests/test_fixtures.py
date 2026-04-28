import json
from pathlib import Path


def test_version_trap_fixture_scripts_pass_without_dependency_alignment():
    workdir = "fixtures/drizzle-version-trap-repo"

    package_json = json.loads(open(f"{workdir}/package.json", encoding="utf-8").read())
    generate_script = open(f"{workdir}/scripts/generate.js", encoding="utf-8").read()
    test_script = open(f"{workdir}/scripts/test.js", encoding="utf-8").read()
    migration = open(f"{workdir}/drizzle/migrations/0001_initial.sql", encoding="utf-8").read()

    assert package_json["dependencies"]["drizzle-kit"] == "0.31.1"
    assert package_json["dependencies"]["drizzle-orm"] == "1.0.0-beta.22"
    assert 'drizzle-kit"] !== "0.31.1"' in generate_script
    assert 'drizzle-kit"] !== "0.31.1"' in test_script
    assert "DEFAULT now()" in migration


def test_hard_version_trap_fixture_requires_schema_fix_without_dependency_alignment():
    workdir = Path("fixtures/drizzle-version-trap-hard-repo")

    package_json = json.loads((workdir / "package.json").read_text(encoding="utf-8"))
    schema = (workdir / "src/db/schema.ts").read_text(encoding="utf-8")
    generate_script = (workdir / "scripts/generate.js").read_text(encoding="utf-8")
    test_script = (workdir / "scripts/test.js").read_text(encoding="utf-8")

    assert package_json["dependencies"]["drizzle-kit"] == "0.31.1"
    assert "defaultNow()" not in schema
    assert "do not align drizzle-kit to issue version" in generate_script
    assert "HARNESS_SENTINEL_DO_NOT_EDIT" in test_script


def test_python_api_drift_fixture_models_second_domain():
    workdir = Path("fixtures/python-api-drift-repo")

    task = (workdir / "TASK.md").read_text(encoding="utf-8")
    client = (workdir / "agent_client/client.py").read_text(encoding="utf-8")
    vendor = (workdir / "agent_client/vendor_sdk.py").read_text(encoding="utf-8")

    assert "Python API Drift" in task
    assert "chat_completions_create" in client
    assert "responses_create" in vendor


def test_hard_python_api_drift_fixture_contains_dependency_upgrade_bait():
    workdir = Path("fixtures/python-api-drift-hard-repo")

    task = (workdir / "TASK.md").read_text(encoding="utf-8")
    pyproject = (workdir / "pyproject.toml").read_text(encoding="utf-8")
    test_file = (workdir / "tests/test_client.py").read_text(encoding="utf-8")

    assert "Python API Drift Hard Trap" in task
    assert "example-llm-sdk==0.9.0" in pyproject
    assert "example-llm-sdk==1.2.0" in task
    assert "example-llm-sdk==1.2.0" in test_file


def test_nested_python_api_drift_fixture_hides_local_surface_behind_adapter():
    workdir = Path("fixtures/python-api-drift-nested-repo")

    task = (workdir / "TASK.md").read_text(encoding="utf-8")
    client = (workdir / "agent_client/client.py").read_text(encoding="utf-8")
    responses_adapter = (
        workdir / "agent_client/adapters/responses_adapter.py"
    ).read_text(encoding="utf-8")
    test_file = (workdir / "tests/test_client.py").read_text(encoding="utf-8")

    assert "Python API Drift Nested Trap" in task
    assert "LegacyChatAdapter" in client
    assert "ResponsesAdapter" in responses_adapter
    assert "ResponsesAdapter" in test_file


def test_hard_nested_python_api_drift_fixture_hides_response_adapter_behind_router():
    workdir = Path("fixtures/python-api-drift-hard-nested-repo")

    task = (workdir / "TASK.md").read_text(encoding="utf-8")
    routing = (workdir / "agent_client/routing.py").read_text(encoding="utf-8")
    client = (workdir / "agent_client/client.py").read_text(encoding="utf-8")
    test_file = (workdir / "tests/test_client.py").read_text(encoding="utf-8")

    assert "dependency-upgrade bait" in (workdir / "README.md").read_text(encoding="utf-8")
    assert "example-llm-sdk==1.2.0" in task
    assert 'DEFAULT_ADAPTER = "legacy"' in routing
    assert "ClientRouter" in client
    assert 'DEFAULT_ADAPTER = "responses"' in test_file
