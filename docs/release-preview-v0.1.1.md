# v0.1.1 Research Preview

This preview moves the repo from backend/MCP infrastructure toward a usable product workbench.

Highlights:

- Next.js dashboard has agent contract, review, issue evidence, graph, health, and run protocol views.
- Seed data now includes demo experiments, demo runs, a demo agent brief, and a draft policy candidate.
- FastAPI exposes issue ingestion and optional API-key protection for write endpoints.
- Docker Compose starts the full stack and includes healthchecks.
- A production frontend Dockerfile and `docker-compose.prod.yml` are available.
- CI includes backend tests, frontend typecheck/build/audit, and Playwright smoke testing.

Known limits:

- auth is API-key only;
- dashboard drill-downs are intentionally shallow;
- issue ingestion is evidence-only and still requires local verification;
- local Docker port publishing may need the documented `make dev-proxy` fallback on some hosts.
