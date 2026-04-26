import typer

from experiment_os.db import check_database

app = typer.Typer(help="Experiment OS developer CLI.")
db_app = typer.Typer(help="Database commands.")
app.add_typer(db_app, name="db")


@db_app.command("check")
def db_check() -> None:
    """Check Postgres connectivity and pgvector availability."""
    status = check_database()
    typer.echo(f"database: {status.database}")
    typer.echo(f"user: {status.user}")
    typer.echo(f"postgres: {status.server_version}")
    typer.echo(f"pgvector: {status.vector_version}")

