.PHONY: up down migrate seed test compile check ci api mcp api-drift-matrix version-trap-hard-matrix

up:
	docker compose up -d postgres

down:
	docker compose down

migrate:
	docker compose run --rm app uv run experiment-os db migrate

seed:
	docker compose run --rm app uv run experiment-os db seed

test:
	docker compose run --rm app uv run pytest

compile:
	docker compose run --rm app uv run python -m compileall src

check: test compile
	git diff --check

ci: up check

api:
	docker compose run --rm --service-ports app uv run experiment-os api serve --host 0.0.0.0 --port 8080

mcp:
	docker compose run --rm app uv run experiment-os mcp serve

api-drift-matrix:
	docker compose run --rm app uv run experiment-os experiments run-codex-api-drift-matrix --repeat-count 3 --sandbox danger-full-access --approval-policy never

version-trap-hard-matrix:
	docker compose run --rm app uv run experiment-os experiments run-codex-version-trap-hard-matrix --repeat-count 3 --sandbox danger-full-access --approval-policy never
