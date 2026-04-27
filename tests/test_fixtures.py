import json


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
