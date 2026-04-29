# Local Stack

`make up` is the default product loop:

```bash
make up
```

It starts:

- Postgres with pgvector;
- the FastAPI backend on `http://127.0.0.1:8080`;
- the Next.js dashboard on `http://127.0.0.1:3000`;
- migrations and seeded demo knowledge before the API starts.

If local Docker port publishing accepts TCP but browser requests hang, run the proxy fallback:

```bash
NEXT_PUBLIC_EXPERIMENT_OS_API_URL=http://127.0.0.1:8091 docker compose up -d --force-recreate frontend
make dev-proxy
```

Then use:

- UI: `http://127.0.0.1:3019`
- API: `http://127.0.0.1:8091`

For protected local write flows, set:

```bash
EXPERIMENT_OS_API_KEY=local-secret
NEXT_PUBLIC_EXPERIMENT_OS_API_KEY=local-secret
```

Read endpoints stay open. Mutations for briefs, experiment status, review actions, promotion, and issue ingestion require `x-api-key` only when `EXPERIMENT_OS_API_KEY` is set.

Production-style compose:

```bash
make up-prod
```

This uses `Dockerfile.frontend` and `docker-compose.prod.yml` so the dashboard starts from a prebuilt Next.js artifact instead of running `npm install` on container startup.

Reset the seeded demo data:

```bash
make seed-reset
```
