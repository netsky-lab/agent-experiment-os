# Python API Drift Nested Fixture

This fixture makes the local API surface less adjacent to the failing wrapper.
The application entrypoint still must be fixed in `agent_client/client.py`, but
the compatible implementation lives behind `agent_client/adapters/responses_adapter.py`.

Run:

```bash
python -m pytest
```
