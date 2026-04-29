# Security Notes

Experiment OS is MCP-native infrastructure, so the main risks are not only web API risks. The system also presents knowledge to agents that may execute tools.

Current controls:

- write endpoints can require `EXPERIMENT_OS_API_KEY` and `x-api-key`;
- GitHub issues are stored as source-backed evidence, not instructions;
- issue-derived claims start as low-confidence draft knowledge;
- policy and intervention acceptance requires rationale and evidence ids;
- agent contracts separate `must_load`, `dependsOn`, decision rules, and evidence-only pages;
- the dashboard exposes provenance and review state instead of silently promoting memories.

Production guidance:

- set `EXPERIMENT_OS_API_KEY`;
- do not expose write endpoints without auth;
- run behind TLS and a reverse proxy;
- keep MCP servers scoped to trusted local agents;
- treat source pages and claims as untrusted text until local versions and local APIs are verified;
- keep run artifacts free of secrets before publishing reports.

Open security work:

- role-based access for review and ingestion;
- signed agent run events;
- source trust levels per repository;
- redaction for run artifacts and transcript uploads;
- stricter CORS configuration for non-local deployments.
