# OpenAI Python Responses API Migration Issue Snapshot

Date: 2026-04-28

Ingestion command:

```bash
docker compose run --rm app uv run experiment-os issues ingest \
  --repo openai/openai-python \
  --query "responses api migration" \
  --limit 2
```

Result:

- issues: `2`
- source pages: `source.github-issue.openai.openai-python.2677`, `source.github-issue.openai.openai-python.2872`
- draft claims: `3`
- draft knowledge card: `knowledge.github-issues.openai.openai-python.responses-api-migration`

## Sources

- https://github.com/openai/openai-python/issues/2677
- https://github.com/openai/openai-python/issues/2872

## Extracted Knowledge

### Issue 2677

State: open

Title: Incompatibility of assistant with tool_calls and tool role in the /v1/responses endpoint

Agent-use status: evidence only. The issue is useful as a migration-risk signal for tool-augmented
flows moving from chat completions to responses. It should not become a direct instruction until the
local project confirms the same endpoint, SDK version, and tool-message representation.

Extracted facets:

- symptom: migration from chat completions to responses hits assistant/tool role compatibility questions;
- affected_version: not extracted by the heuristic;
- workaround: not extracted by the heuristic;
- verified_fix: not extracted by the heuristic;
- risk: tool response representation may differ across APIs.

### Issue 2872

State: open

Title: responses.parse() throws a PydanticSerializationUnexpectedValue error in v2.21.0

Agent-use status: evidence only. The issue is useful as a version-specific warning around
`responses.parse()` and Pydantic serialization behavior. It should be checked against the local
installed SDK version before changing dependencies or parser code.

Extracted facets:

- symptom: `responses.parse()` produces Pydantic serialization warnings/errors;
- affected_version: issue title mentions `v2.21.0`;
- workaround: not extracted by the heuristic;
- verified_fix: not extracted by the heuristic;
- risk: not extracted by the heuristic.

## Review Decision

Keep the generated card as draft. The card can improve agent retrieval for Responses API migration
tasks, but every claim remains external evidence until a local repo confirms matching versions and
API surface.
