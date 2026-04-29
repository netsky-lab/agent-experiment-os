.PHONY: up down dev-proxy migrate seed test compile check ci api mcp frontend frontend-build frontend-typecheck frontend-audit api-drift-matrix version-trap-hard-matrix

up:
	docker compose up -d postgres app frontend

down:
	docker compose down

dev-proxy:
	socat TCP-LISTEN:8091,fork,reuseaddr SYSTEM:'docker compose exec -T app socat STDIO TCP\:127.0.0.1\:8080' &
	socat TCP-LISTEN:3019,fork,reuseaddr SYSTEM:'docker compose exec -T frontend socat STDIO TCP\:127.0.0.1\:3000' &
	@echo "UI: http://127.0.0.1:3019"
	@echo "API: http://127.0.0.1:8091"

migrate:
	docker compose run --rm app uv run experiment-os db migrate

seed:
	docker compose run --rm app uv run experiment-os db seed

test:
	docker compose run --rm app uv run pytest

compile:
	docker compose run --rm app uv run python -m compileall src

check: test compile frontend-typecheck frontend-build frontend-audit
	git diff --check

ci: up check

api:
	docker compose run --rm --service-ports app uv run experiment-os api serve --host 0.0.0.0 --port 8080

frontend:
	cd frontend && npm run dev

frontend-typecheck:
	cd frontend && npm run typecheck

frontend-build:
	cd frontend && npm run build

frontend-audit:
	cd frontend && npm audit --omit=dev

mcp:
	docker compose run --rm app uv run experiment-os mcp serve

api-drift-matrix:
	docker compose run --rm app uv run experiment-os experiments run-codex-api-drift-matrix --repeat-count 3 --sandbox danger-full-access --approval-policy never

version-trap-hard-matrix:
	docker compose run --rm app uv run experiment-os experiments run-codex-version-trap-hard-matrix --repeat-count 3 --sandbox danger-full-access --approval-policy never
