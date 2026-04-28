from agent_client.adapters.legacy_chat_adapter import LegacyChatAdapter
from agent_client.adapters.responses_adapter import ResponsesAdapter

DEFAULT_ADAPTER = "legacy"


class ClientRouter:
    def __init__(self, *, model: str, adapter_name: str | None = None) -> None:
        self._model = model
        self._adapter_name = adapter_name or DEFAULT_ADAPTER

    def build(self):
        registry = {
            "legacy": LegacyChatAdapter,
            "responses": ResponsesAdapter,
        }
        adapter = registry[self._adapter_name]
        return adapter(model=self._model)
