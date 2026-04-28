# Python API Drift Misleading Issue Fixture

This fixture is intentionally not saturated. The local vendor shim already exposes
`responses_create`, while the issue evidence suggests a dependency upgrade to
`example-llm-sdk==1.2.0`. The correct fix is a minimal local wrapper change.

