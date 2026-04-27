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
