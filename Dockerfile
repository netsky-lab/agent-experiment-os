FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /workspace

ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/tmp/experiment-os-venv

CMD ["sleep", "infinity"]
