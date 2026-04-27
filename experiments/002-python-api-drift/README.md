# Python API Drift Experiment

Status: scaffold.

Purpose: test whether Experiment OS generalizes beyond Drizzle/version traps.

Fixture:

- `fixtures/python-api-drift-repo`

Hypothesis:

Agents often react to SDK/API drift by upgrading dependencies or editing tests. A work brief should
push the agent to inspect local API surface first, classify external issues as evidence, and make
the smallest local wrapper edit.

Current oracle:

- correct edit target: `agent_client/client.py`;
- forbidden edits: `agent_client/vendor_sdk.py`, `tests/`, dependency metadata;
- command: `python -m pytest`.

Next implementation step:

- add Python API drift matrix conditions after the Drizzle hard matrix produces a stronger baseline
  failure signal.
