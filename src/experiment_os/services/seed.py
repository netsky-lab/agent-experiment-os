from sqlalchemy.orm import Session

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

        for page in pages:
            self._wiki.upsert_page(page)
        for edge in edges:
            self._wiki.upsert_edge(edge)
        HybridRetriever(self._session).reindex_all()

        return {"pages": len(pages), "edges": len(edges)}


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
    ]
