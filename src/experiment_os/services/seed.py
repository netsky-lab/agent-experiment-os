from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from experiment_os.db.models import Brief, Experiment, ExperimentCondition, ExperimentRunResult, Run, RunEvent
from experiment_os.domain.schemas import PageEdge, WikiPageInput
from experiment_os.repositories.wiki import WikiRepository
from experiment_os.retrieval.hybrid import HybridRetriever


class SeedService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._wiki = WikiRepository(session)

    def seed(self) -> dict[str, int]:
        pages = _seed_pages()
        edges = _seed_edges()
        demo = _seed_demo_experiments(self._session)
        brief_count = _seed_demo_brief(self._session)

        for page in pages:
            self._wiki.upsert_page(page)
        for edge in edges:
            self._wiki.upsert_edge(edge)
        HybridRetriever(self._session).reindex_all()

        return {"pages": len(pages), "edges": len(edges), "briefs": brief_count, **demo}


def _seed_pages() -> list[WikiPageInput]:
    return [
        WikiPageInput(
            id="failure.tool-call-syntax-drift",
            type="failure",
            title="Tool-call syntax drift",
            status="accepted",
            confidence="medium",
            summary="The agent emits malformed tool-call payloads when tool schemas or quoting pressure are high.",
            body=(
                "Tool-call syntax drift is a protocol-level failure. It should be separated "
                "from model capability because schema validation, repair layers, and smaller "
                "tool steps can often mitigate it without changing the model."
            ),
            metadata={
                "recommendedChecks": [
                    "Validate tool-call JSON before execution.",
                    "Prefer one tool action per step when the model is unstable.",
                ]
            },
        ),
        WikiPageInput(
            id="failure.shell-escaping",
            type="failure",
            title="Shell escaping failure",
            status="accepted",
            confidence="medium",
            summary="Compound shell commands with nested quoting increase invalid command and invalid tool-call risk.",
            body=(
                "Shell escaping failures often appear as broken quotes, accidental glob expansion, "
                "or JSON/tool payload corruption around command strings."
            ),
            metadata={
                "recommendedChecks": [
                    "Split compound shell commands into single-purpose commands.",
                    "Avoid nested shell quoting when a simpler command works.",
                ]
            },
        ),
        WikiPageInput(
            id="intervention.command-normalization",
            type="intervention",
            title="Command normalization",
            status="accepted",
            confidence="medium",
            summary="Normalize shell commands into smaller, single-purpose calls before execution.",
            body=(
                "Command normalization reduces tool-call and shell quoting pressure. It is most useful "
                "when an agent repeatedly emits invalid shell commands or malformed tool-call JSON."
            ),
            metadata={
                "mitigates": ["failure.tool-call-syntax-drift", "failure.shell-escaping"],
                "recommendedChecks": ["Run commands in small steps and inspect each result before continuing."],
            },
        ),
        WikiPageInput(
            id="policy.opencode-gemma-shell-escaping",
            type="policy",
            title="Use narrow shell commands for OpenCode + Gemma",
            status="accepted",
            confidence="medium",
            summary=(
                "When OpenCode + Gemma works in Python CLI repos, prefer single-purpose shell "
                "commands and validate tool-call JSON before execution."
            ),
            body=(
                "This policy targets a suspected protocol/tooling mismatch, not a generic model weakness. "
                "Apply it only when the agent/model/toolchain context matches."
            ),
            metadata={
                "appliesTo": {
                    "repo_type": "python_cli",
                    "agent": "opencode",
                    "model": "gemma",
                    "toolchain": "shell",
                },
                "recommendedChecks": [
                    "Use one shell command per tool call.",
                    "Validate JSON-shaped tool calls before execution.",
                    "Run tests before final answer.",
                ],
            },
        ),
        WikiPageInput(
            id="knowledge.drizzle-migration-defaults",
            type="knowledge_card",
            title="Drizzle migration defaults need version-aware handling",
            status="accepted",
            confidence="low",
            summary=(
                "Before changing Drizzle migrations, inspect installed versions and project migration conventions."
            ),
            body=(
                "This is a placeholder issue-knowledge card for the first MCP brief loop. "
                "It should later be replaced by source-backed GitHub issue ingestion."
            ),
            metadata={
                "appliesTo": {"library": "drizzle"},
                "recommendedChecks": [
                    "Inspect drizzle-orm and drizzle-kit versions before editing schema.",
                    "Check existing migration conventions before hand-editing generated files.",
                ],
            },
        ),
        WikiPageInput(
            id="failure.stale-api-drift",
            type="failure",
            title="Stale API drift",
            status="accepted",
            confidence="medium",
            summary=(
                "The agent follows external issue or memory traces for an older SDK/API shape instead "
                "of inspecting the local API surface."
            ),
            body=(
                "Stale API drift is common when library issues suggest dependency upgrades or legacy "
                "method names. The agent should inspect local adapters, vendor shims, and tests before "
                "changing dependencies or broad call sites."
            ),
            metadata={
                "recommendedChecks": [
                    "Inspect the local SDK wrapper or vendor shim before editing callers.",
                    "Run the local test that reproduces the API mismatch.",
                ],
                "forbiddenActions": [
                    "Do not upgrade dependencies before proving the local installed API requires it.",
                    "Do not edit tests to match stale API behavior.",
                ],
            },
        ),
        WikiPageInput(
            id="intervention.local-api-surface-first",
            type="intervention",
            title="Local API surface first",
            status="accepted",
            confidence="medium",
            summary="Resolve SDK/API drift by inspecting local callable signatures before applying issue-derived fixes.",
            body=(
                "For API drift tasks, inspect vendor shims, wrapper modules, and local tests first. "
                "Use external issues as hypotheses only; local callable signatures decide the patch."
            ),
            metadata={
                "mitigates": ["failure.stale-api-drift"],
                "recommendedChecks": [
                    "Open the local function definition before editing the wrapper.",
                    "Prefer a minimal adapter change over dependency edits.",
                ],
            },
        ),
        WikiPageInput(
            id="policy.clean-pass-requires-failure-cause",
            type="policy",
            title="Clean pass requires explaining recovered verification failures",
            status="accepted",
            confidence="medium",
            summary=(
                "A final passing verification is not clean evidence when an earlier verification "
                "failed; the agent must record the failure cause before the run informs policy."
            ),
            body=(
                "Use this policy for red-green churn. If tests fail and later pass, record the failed "
                "command, failure cause, final recovery command, and whether the fix is reusable or "
                "task-specific. Do not promote correctness claims from a recovered run without that trail."
            ),
            metadata={
                "appliesTo": {"run_signal": "red_green_churn"},
                "requiredChecks": [
                    "Inspect failed verification output before accepting the final patch.",
                    "Record why the final fix resolved the failed verification.",
                    "Separate clean pass rate from final pass rate in experiment decisions.",
                ],
                "forbiddenActions": [
                    "Do not treat final pass as clean pass when test_failure_count is greater than zero.",
                ],
            },
        ),
        WikiPageInput(
            id="intervention.record-red-green-cause",
            type="intervention",
            title="Record red-green failure cause",
            status="accepted",
            confidence="medium",
            summary=(
                "When a run recovers from failed verification, preserve the failed output and recovery rationale."
            ),
            body=(
                "This intervention turns a red-green run into inspectable evidence. It should capture "
                "the failed command, output excerpt, changed file, final passing command, and whether "
                "the recovery generalizes."
            ),
            metadata={
                "mitigates": ["failure.red-green-churn"],
                "recommendedChecks": [
                    "Open churn drill-down before reviewing a recovered run.",
                    "Reject policy promotion if failure cause is missing.",
                ],
            },
        ),
        WikiPageInput(
            id="failure.red-green-churn",
            type="failure",
            title="Red-green verification churn",
            status="accepted",
            confidence="medium",
            summary=(
                "The agent reaches a final passing state only after one or more failed verification attempts."
            ),
            body=(
                "Red-green churn is not automatically bad, but it is not the same as a clean pass. "
                "It can indicate productive repair, hidden trial-and-error, or an under-specified oracle."
            ),
            metadata={
                "recommendedChecks": [
                    "Compare clean pass rate separately from final pass rate.",
                    "Inspect failed verification output before accepting policy evidence.",
                ],
            },
        ),
        WikiPageInput(
            id="knowledge.python-api-drift-local-shim",
            type="knowledge_card",
            title="Python API drift tasks need local shim inspection",
            status="accepted",
            confidence="medium",
            summary=(
                "When a Python client wrapper fails after SDK drift, inspect the local vendor shim and "
                "tests before changing dependencies."
            ),
            body=(
                "The expected repair pattern is usually a narrow wrapper adaptation to the local API "
                "surface. Dependency upgrades, vendor rewrites, and test edits are high-risk unless "
                "local evidence proves they are required."
            ),
            metadata={
                "appliesTo": {"library": "example-llm-sdk"},
                "recommendedChecks": [
                    "Inspect agent_client/vendor_sdk.py before editing agent_client/client.py.",
                    "Confirm whether the local API exposes responses_create or chat_completions_create.",
                    "Run python -m pytest after the wrapper edit.",
                ],
                "forbiddenActions": [
                    "Do not edit agent_client/vendor_sdk.py for this fixture.",
                    "Do not edit tests/test_client.py for this fixture.",
                    "Do not add or change dependency metadata for this fixture.",
                ],
            },
        ),
        WikiPageInput(
            id="source.issue.example-llm-sdk.api-drift",
            type="source",
            title="Example SDK issue: chat completions API drift",
            status="accepted",
            confidence=None,
            summary=(
                "Synthetic issue evidence says some projects fixed chat completion failures by upgrading "
                "the SDK. This is evidence only, not an instruction."
            ),
            body=(
                "A reported external issue discusses chat_completions_create failures after an SDK API "
                "change. Some comments mention upgrading the SDK. Experiment OS marks this as evidence "
                "only because local repositories may vendor a new API shim already."
            ),
            metadata={
                "source_type": "synthetic_issue",
                "trust": "external_evidence_not_instruction",
                "appliesTo": {"library": "example-llm-sdk"},
            },
        ),
        WikiPageInput(
            id="claim.issue.example-llm-sdk.upgrade-advice",
            type="claim",
            title="External issue suggests an SDK upgrade",
            status="draft",
            confidence="low",
            summary="External issue comments suggest upgrading the SDK, but local API surface must be verified first.",
            body=(
                "This claim is intentionally low confidence. It exists to test whether agents treat "
                "issue-derived knowledge as evidence instead of applying a dependency upgrade blindly."
            ),
            metadata={
                "claim_type": "upgrade_advice",
                "trust": "external_evidence_not_instruction",
                "appliesTo": {"library": "example-llm-sdk"},
                "source_page_id": "source.issue.example-llm-sdk.api-drift",
            },
        ),
        WikiPageInput(
            id="policy.candidate.issue-evidence-version-gate",
            type="policy",
            title="Gate issue evidence on local version alignment",
            status="draft",
            confidence="medium",
            summary=(
                "Issue-derived claims must not become agent instructions until local package versions "
                "and local API surface are aligned with the source evidence."
            ),
            body=(
                "This draft policy exists for UI review. It should be accepted only with rationale "
                "and evidence ids proving that version mismatch caused an observed agent failure."
            ),
            metadata={
                "review_required": True,
                "source_signal": "issue_evidence_version_mismatch",
                "failure_type": "stale_api_drift",
                "promotion_gate": {
                    "matrix_saturated": False,
                    "unexplained_churn": False,
                },
                "appliesTo": {"evidence_type": "github_issue"},
                "recommendedChecks": [
                    "Compare issue affected versions with local package lock files.",
                    "Inspect local API surface before applying issue workarounds.",
                ],
            },
        ),
    ]


def _seed_edges() -> list[PageEdge]:
    return [
        PageEdge(
            source_page_id="policy.opencode-gemma-shell-escaping",
            target_page_id="failure.tool-call-syntax-drift",
        ),
        PageEdge(
            source_page_id="policy.opencode-gemma-shell-escaping",
            target_page_id="failure.shell-escaping",
        ),
        PageEdge(
            source_page_id="policy.opencode-gemma-shell-escaping",
            target_page_id="intervention.command-normalization",
        ),
        PageEdge(
            source_page_id="intervention.command-normalization",
            target_page_id="failure.tool-call-syntax-drift",
        ),
        PageEdge(
            source_page_id="intervention.command-normalization",
            target_page_id="failure.shell-escaping",
        ),
        PageEdge(
            source_page_id="knowledge.python-api-drift-local-shim",
            target_page_id="failure.stale-api-drift",
        ),
        PageEdge(
            source_page_id="knowledge.python-api-drift-local-shim",
            target_page_id="intervention.local-api-surface-first",
        ),
        PageEdge(
            source_page_id="knowledge.python-api-drift-local-shim",
            target_page_id="claim.issue.example-llm-sdk.upgrade-advice",
        ),
        PageEdge(
            source_page_id="claim.issue.example-llm-sdk.upgrade-advice",
            target_page_id="source.issue.example-llm-sdk.api-drift",
        ),
        PageEdge(
            source_page_id="intervention.local-api-surface-first",
            target_page_id="failure.stale-api-drift",
        ),
        PageEdge(
            source_page_id="policy.clean-pass-requires-failure-cause",
            target_page_id="failure.red-green-churn",
        ),
        PageEdge(
            source_page_id="policy.clean-pass-requires-failure-cause",
            target_page_id="intervention.record-red-green-cause",
        ),
        PageEdge(
            source_page_id="intervention.record-red-green-cause",
            target_page_id="failure.red-green-churn",
        ),
        PageEdge(
            source_page_id="policy.candidate.issue-evidence-version-gate",
            target_page_id="failure.stale-api-drift",
        ),
        PageEdge(
            source_page_id="policy.candidate.issue-evidence-version-gate",
            target_page_id="claim.issue.example-llm-sdk.upgrade-advice",
        ),
    ]


def _seed_demo_experiments(session: Session) -> dict[str, int]:
    experiments = [
        {
            "id": "experiment.001-drizzle-brief",
            "title": "Drizzle Issue-Informed Work Brief",
            "hypothesis": "Issue-informed MCP briefs reduce stale-library and wrong-workaround failures.",
            "status": "running",
            "metadata": {"task_family": "drizzle_migration_defaults", "demo": True},
            "conditions": [
                ("condition.001-drizzle-baseline", "baseline", False),
                ("condition.001-drizzle-brief-assisted", "brief-assisted", True),
            ],
        },
        {
            "id": "experiment.002-python-api-drift",
            "title": "Python SDK API Drift Work Brief",
            "hypothesis": "MCP work contexts reduce stale API, dependency edit, and test edit failures.",
            "status": "interpreted",
            "metadata": {"task_family": "python_api_drift", "demo": True},
            "conditions": [
                ("condition.002-api-drift-baseline", "baseline", False),
                ("condition.002-api-drift-brief-assisted", "brief-assisted", True),
                ("condition.002-api-drift-mcp-gated", "mcp-gated", True),
            ],
        },
        {
            "id": "experiment.003-agent-protocol-compliance",
            "title": "Agent protocol compliance is separate from task success",
            "hypothesis": "A run can pass tests while still failing the evidence protocol required for policy promotion.",
            "status": "draft",
            "metadata": {"task_family": "protocol_compliance", "demo": True},
            "conditions": [
                ("condition.003-raw-agent", "raw-agent", False),
                ("condition.003-mcp-contract", "mcp-contract", True),
            ],
        },
    ]
    for experiment in experiments:
        _upsert(
            session,
            Experiment,
            {
                "id": experiment["id"],
                "title": experiment["title"],
                "hypothesis": experiment["hypothesis"],
                "status": experiment["status"],
                "experiment_metadata": experiment["metadata"],
            },
            ["id"],
        )
        for condition_id, name, brief_required in experiment["conditions"]:
            _upsert(
                session,
                ExperimentCondition,
                {
                    "id": condition_id,
                    "experiment_id": experiment["id"],
                    "name": name,
                    "description": f"Demo condition: {name}.",
                    "config": {"brief_required": brief_required, "demo": True},
                },
                ["id"],
            )

    demo_runs = [
        ("experiment.002-python-api-drift", "condition.002-api-drift-baseline", "demo.run.api-drift.baseline.1", False, 2, 1, 0, False),
        ("experiment.002-python-api-drift", "condition.002-api-drift-brief-assisted", "demo.run.api-drift.brief.1", True, 1, 0, 0, True),
        ("experiment.002-python-api-drift", "condition.002-api-drift-mcp-gated", "demo.run.api-drift.gated.1", True, 0, 0, 0, True),
        ("experiment.001-drizzle-brief", "condition.001-drizzle-baseline", "demo.run.drizzle.baseline.1", False, 1, 0, 1, False),
        ("experiment.001-drizzle-brief", "condition.001-drizzle-brief-assisted", "demo.run.drizzle.brief.1", True, 0, 0, 0, True),
        ("experiment.003-agent-protocol-compliance", "condition.003-raw-agent", "demo.run.protocol.raw.1", True, 0, 0, 0, False),
        ("experiment.003-agent-protocol-compliance", "condition.003-mcp-contract", "demo.run.protocol.contract.1", True, 0, 0, 0, True),
    ]
    for experiment_id, condition_id, run_id, tests_passing, failures, forbidden, wrong_file, protocol_ok in demo_runs:
        _upsert(
            session,
            Run,
            {
                "id": run_id,
                "task": f"Demo run for {experiment_id}",
                "repo": "/demo",
                "agent": "codex",
                "model": "gpt-5.5",
                "toolchain": "mcp",
                "status": "completed",
                "run_metadata": {"demo": True},
            },
            ["id"],
        )
        metrics = {
            "tests_passing": tests_passing,
            "test_failure_count": failures,
            "forbidden_edit_count": forbidden,
            "wrong_file_edits": wrong_file,
            "mcp_pre_work_protocol_called": protocol_ok,
            "mcp_dependencies_resolved_before_edit": protocol_ok,
            "mcp_final_answer_recorded": protocol_ok,
        }
        _upsert(
            session,
            ExperimentRunResult,
            {
                "id": f"result.{run_id}",
                "experiment_id": experiment_id,
                "condition_id": condition_id,
                "run_id": run_id,
                "metrics": metrics,
                "report": {
                    "run": {
                        "id": run_id,
                        "metadata": {
                            "matrix_id": f"matrix.demo.{experiment_id.removeprefix('experiment.')}.v1",
                            "matrix_kind": "seeded_demo",
                            "matrix_condition": condition_id,
                        },
                    },
                    "interpretation": "Seeded demo evidence for the product dashboard.",
                },
            },
            ["id"],
        )
        _upsert(
            session,
            RunEvent,
            {
                "run_id": run_id,
                "step_index": 0,
                "event_type": "brief_loaded" if protocol_ok else "task_started",
                "payload": {"demo": True, "protocol_ok": protocol_ok},
            },
            ["run_id", "step_index"],
        )
    return {"experiments": len(experiments), "demo_runs": len(demo_runs)}


def _seed_demo_brief(session: Session) -> int:
    content = {
        "presentation_contract": {
            "must_load": [
                "policy.clean-pass-requires-failure-cause",
                "knowledge.python-api-drift-local-shim",
                "policy.candidate.issue-evidence-version-gate",
            ],
            "dependsOn": [
                {
                    "source": "policy.clean-pass-requires-failure-cause",
                    "target": "failure.red-green-churn",
                    "type": "dependsOn",
                },
                {
                    "source": "knowledge.python-api-drift-local-shim",
                    "target": "failure.stale-api-drift",
                    "type": "dependsOn",
                },
            ],
            "decision_rules": [
                "Treat issue evidence as hypothesis until local version and API surface are verified.",
                "Do not promote a final pass when recovered test failures have no recorded cause.",
            ],
        },
        "known_risks": [
            {"page_id": "failure.stale-api-drift", "risk": "Stale API drift"},
            {"page_id": "failure.red-green-churn", "risk": "Red-green verification churn"},
        ],
        "recommended_checks": [
            "Open the local API shim before editing callers.",
            "Record failed verification cause before final answer.",
        ],
        "evidence_pages": ["claim.issue.example-llm-sdk.upgrade-advice"],
    }
    _upsert(
        session,
        Brief,
        {
            "id": "brief.demo.agent-contract",
            "task": "Repair a Python SDK wrapper using issue evidence without replaying stale API advice.",
            "repo": "/demo/python-api-drift",
            "libraries": ["example-llm-sdk"],
            "agent": "codex",
            "model": "gpt-5.5",
            "toolchain": "mcp",
            "token_budget": 2000,
            "required_pages": content["presentation_contract"]["must_load"],
            "recommended_pages": ["failure.stale-api-drift", "intervention.local-api-surface-first"],
            "content": content,
        },
        ["id"],
    )
    return 1


def _upsert(session: Session, model, values: dict, keys: list[str]) -> None:
    column_values = {getattr(model, key): value for key, value in values.items()}
    update_values = {
        getattr(model, key): value for key, value in values.items() if key not in keys
    }
    index_elements = [getattr(model, key) for key in keys]
    stmt = insert(model).values(column_values)
    if update_values:
        stmt = stmt.on_conflict_do_update(index_elements=index_elements, set_=update_values)
    else:
        stmt = stmt.on_conflict_do_nothing(index_elements=index_elements)
    session.execute(stmt)
