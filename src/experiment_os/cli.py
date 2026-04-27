import json
import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config
import typer

from experiment_os.database import check_database, session_scope
from experiment_os.domain.schemas import BriefRequest, RunEventInput, RunStartInput
from experiment_os.mcp_server import create_mcp_server
from experiment_os.mcp_server.client_smoke import run_mcp_smoke
from experiment_os.retrieval.hybrid import HybridRetriever
from experiment_os.services.briefs import BriefCompiler
from experiment_os.services.dependencies import DependencyResolver
from experiment_os.services.experiments import ExperimentRunner
from experiment_os.services.issues import GitHubIssueIngestor
from experiment_os.services.review import ReviewService
from experiment_os.services.runs import RunRecorder
from experiment_os.services.seed import SeedService

app = typer.Typer(help="Experiment OS developer CLI.")
db_app = typer.Typer(help="Database commands.")
demo_app = typer.Typer(help="Demo and smoke-check commands.")
mcp_app = typer.Typer(help="MCP server commands.")
knowledge_app = typer.Typer(help="Knowledge search and indexing commands.")
issues_app = typer.Typer(help="GitHub issue ingestion commands.")
experiments_app = typer.Typer(help="Experiment runner commands.")
app.add_typer(db_app, name="db")
app.add_typer(demo_app, name="demo")
app.add_typer(mcp_app, name="mcp")
app.add_typer(knowledge_app, name="knowledge")
app.add_typer(issues_app, name="issues")
app.add_typer(experiments_app, name="experiments")


@db_app.command("check")
def db_check() -> None:
    """Check Postgres connectivity and pgvector availability."""
    status = check_database()
    typer.echo(f"database: {status['database']}")
    typer.echo(f"user: {status['user']}")
    typer.echo(f"postgres: {status['server_version']}")
    typer.echo(f"pgvector: {status['vector_version']}")


@db_app.command("migrate")
def db_migrate() -> None:
    """Run Alembic migrations to head."""
    command.upgrade(Config("alembic.ini"), "head")


@db_app.command("seed")
def db_seed() -> None:
    """Seed initial wiki knowledge pages and dependency edges."""
    with session_scope() as session:
        result = SeedService(session).seed()
    typer.echo(json.dumps(result, indent=2))


@knowledge_app.command("reindex")
def knowledge_reindex() -> None:
    """Rebuild local deterministic embeddings for wiki pages."""
    with session_scope() as session:
        result = HybridRetriever(session).reindex_all()
    typer.echo(json.dumps(result, indent=2))


@knowledge_app.command("search")
def knowledge_search(
    query: str,
    limit: int = typer.Option(8, help="Maximum number of results."),
) -> None:
    """Search wiki knowledge using full-text + pgvector retrieval."""
    with session_scope() as session:
        results = HybridRetriever(session).search(query, limit=limit)
    typer.echo(json.dumps({"query": query, "results": results}, indent=2))


@knowledge_app.command("list")
def knowledge_list(
    status: str | None = typer.Option(None, help="Filter by page status."),
    page_type: str | None = typer.Option(None, help="Filter by page type."),
) -> None:
    """List wiki pages for review."""
    with session_scope() as session:
        pages = ReviewService(session).list_pages(status=status, page_type=page_type)
    typer.echo(json.dumps({"pages": pages}, indent=2))


@knowledge_app.command("set-status")
def knowledge_set_status(
    page_id: str,
    status: str,
) -> None:
    """Set a wiki page status, e.g. draft/accepted/rejected/superseded."""
    with session_scope() as session:
        page = ReviewService(session).set_status(page_id, status)
    typer.echo(json.dumps(page, indent=2))


@knowledge_app.command("promote-claim")
def knowledge_promote_claim(
    claim_id: str,
    title: str | None = typer.Option(None, help="Optional title for the promoted card."),
) -> None:
    """Promote a claim into a draft knowledge card."""
    with session_scope() as session:
        page = ReviewService(session).promote_claim(claim_id, title=title)
    typer.echo(json.dumps(page, indent=2))


@issues_app.command("ingest")
def issues_ingest(
    repo: str = typer.Option(..., help="GitHub repo in owner/name form."),
    query: str = typer.Option(..., help="GitHub issue search query."),
    limit: int = typer.Option(5, help="Maximum number of issues to ingest."),
) -> None:
    """Ingest GitHub issues as source snapshots and source wiki pages."""
    with session_scope() as session:
        result = GitHubIssueIngestor(session).ingest(repo=repo, query=query, limit=limit)
    typer.echo(json.dumps(result, indent=2))


@experiments_app.command("seed-drizzle")
def experiments_seed_drizzle() -> None:
    """Seed the first Drizzle brief experiment definition."""
    with session_scope() as session:
        result = ExperimentRunner(session).seed_drizzle_experiment()
    typer.echo(json.dumps(result, indent=2))


@experiments_app.command("run-drizzle-fixture")
def experiments_run_drizzle_fixture() -> None:
    """Run a deterministic baseline vs brief-assisted Drizzle fixture."""
    with session_scope() as session:
        result = ExperimentRunner(session).run_drizzle_fixture()
    typer.echo(json.dumps(result, indent=2))


@experiments_app.command("run-shell")
def experiments_run_shell(
    condition_id: str = typer.Option(..., help="Experiment condition id."),
    command: str = typer.Option(..., help="Shell command to execute as the agent."),
    workdir: Path = typer.Option(Path("."), help="Working directory for the command."),
    timeout_seconds: int = typer.Option(300, help="Command timeout."),
) -> None:
    """Run a shell-command agent condition and capture transcript artifacts."""
    with session_scope() as session:
        result = ExperimentRunner(session).run_shell_condition(
            condition_id=condition_id,
            command=command,
            workdir=workdir,
            timeout_seconds=timeout_seconds,
        )
    typer.echo(json.dumps(result, indent=2))


@experiments_app.command("run-codex")
def experiments_run_codex(
    condition_id: str = typer.Option(..., help="Experiment condition id."),
    prompt: str = typer.Option(..., help="Prompt to send to codex exec."),
    workdir: Path = typer.Option(Path("."), help="Working directory for Codex."),
    model: str | None = typer.Option(None, help="Optional Codex model override."),
    sandbox: str = typer.Option("workspace-write", help="Codex sandbox mode."),
    approval_policy: str = typer.Option("never", help="Codex approval policy."),
    timeout_seconds: int = typer.Option(900, help="Command timeout."),
) -> None:
    """Run a Codex CLI condition through codex exec and capture transcript artifacts."""
    with session_scope() as session:
        result = ExperimentRunner(session).run_codex_condition(
            condition_id=condition_id,
            prompt=prompt,
            workdir=workdir,
            model=model,
            sandbox=sandbox,
            approval_policy=approval_policy,
            timeout_seconds=timeout_seconds,
        )
    typer.echo(json.dumps(result, indent=2))


@experiments_app.command("run-codex-toy")
def experiments_run_codex_toy(
    condition_id: str = typer.Option(
        "condition.001-drizzle-brief-assisted",
        help="Experiment condition id.",
    ),
    prompt: str | None = typer.Option(None, help="Optional prompt override."),
    model: str | None = typer.Option(None, help="Optional Codex model override."),
    sandbox: str = typer.Option("workspace-write", help="Codex sandbox mode."),
    approval_policy: str = typer.Option("never", help="Codex approval policy."),
    timeout_seconds: int = typer.Option(900, help="Command timeout."),
    fixture_path: Path = typer.Option(
        Path("fixtures/drizzle-toy-repo"),
        help="Fixture repo copied into artifacts/workdirs before running Codex.",
    ),
) -> None:
    """Copy the Drizzle toy fixture and run Codex against the disposable workspace."""
    with session_scope() as session:
        result = ExperimentRunner(session).run_codex_toy_fixture(
            condition_id=condition_id,
            prompt=prompt,
            model=model,
            sandbox=sandbox,
            approval_policy=approval_policy,
            timeout_seconds=timeout_seconds,
            fixture_path=fixture_path,
        )
    typer.echo(json.dumps(result, indent=2))


@experiments_app.command("run-codex-toy-comparison")
def experiments_run_codex_toy_comparison(
    model: str | None = typer.Option(None, help="Optional Codex model override."),
    sandbox: str = typer.Option("workspace-write", help="Codex sandbox mode."),
    approval_policy: str = typer.Option("never", help="Codex approval policy."),
    timeout_seconds: int = typer.Option(900, help="Command timeout per condition."),
    fixture_path: Path = typer.Option(
        Path("fixtures/drizzle-toy-repo"),
        help="Fixture repo copied into disposable workdirs before running Codex.",
    ),
) -> None:
    """Run baseline and brief-assisted Codex conditions against the toy fixture."""
    with session_scope() as session:
        result = ExperimentRunner(session).run_codex_toy_comparison(
            model=model,
            sandbox=sandbox,
            approval_policy=approval_policy,
            timeout_seconds=timeout_seconds,
            fixture_path=fixture_path,
        )
    typer.echo(json.dumps(result, indent=2))


@demo_app.command("smoke")
def demo_smoke() -> None:
    """Run the v0 work-brief loop without an MCP client."""
    with session_scope() as session:
        seed_result = SeedService(session).seed()
        brief = BriefCompiler(session).compile(
            BriefRequest(
                task="Fix a Drizzle migration issue in a Python CLI repo",
                repo="example/repo",
                libraries=["drizzle"],
                agent="opencode",
                model="gemma",
                toolchain="shell",
            )
        )
        dependencies = DependencyResolver(session).resolve(brief["required_pages"], depth=2)
        recorder = RunRecorder(session)
        run = recorder.start_run(
            RunStartInput(
                task="Fix a Drizzle migration issue in a Python CLI repo",
                repo="example/repo",
                agent="opencode",
                model="gemma",
                toolchain="shell",
                metadata={"brief_id": brief["brief_id"]},
            )
        )
        event = recorder.record_event(
            RunEventInput(
                run_id=run["run_id"],
                event_type="brief_loaded",
                payload={
                    "brief_id": brief["brief_id"],
                    "required_pages": brief["required_pages"],
                },
            )
        )

    typer.echo(
        json.dumps(
            {
                "seed": seed_result,
                "brief": brief,
                "dependencies": dependencies.model_dump(),
                "run": run,
                "event": event,
            },
            indent=2,
        )
    )


@demo_app.command("mcp-smoke")
def demo_mcp_smoke() -> None:
    """Run the v0 work-brief loop through a real MCP stdio client."""
    result = asyncio.run(run_mcp_smoke())
    typer.echo(json.dumps(result, indent=2))


@mcp_app.command("serve")
def mcp_serve(
    transport: str = typer.Option("stdio", help="MCP transport: stdio or streamable-http."),
) -> None:
    """Run the MCP server."""
    create_mcp_server().run(transport=transport)
