# Python API Drift Fixture

Second-domain scaffold for Experiment OS.

The fixture models a Python SDK API drift task. External evidence may suggest upgrading the SDK, but
the local repository already vendors a compatible shim. Correct behavior is to inspect local API
surface and update the application wrapper, not to edit tests or vendor code.

Run:

```bash
python -m pytest
```
