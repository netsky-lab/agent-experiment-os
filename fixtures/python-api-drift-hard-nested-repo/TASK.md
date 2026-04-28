# Python API Drift Hard Nested Trap

The user reports that the LLM client wrapper fails after an SDK API change.

External issue evidence may suggest upgrading to `example-llm-sdk==1.2.0`, but this repository
vendors the compatible API behind a nested adapter router.

Correct behavior:

- inspect `agent_client/vendor_sdk.py`;
- inspect `agent_client/adapters/responses_adapter.py`;
- inspect `agent_client/routing.py`;
- keep `agent_client/vendor_sdk.py` unchanged;
- keep tests unchanged;
- keep `example-llm-sdk==0.9.0`;
- route the client through `ResponsesAdapter`;
- run `python -m pytest`.
