from agent_client import vendor_sdk


class LegacyChatAdapter:
    def __init__(self, *, model: str) -> None:
        self._model = model

    def generate(self, prompt: str) -> str:
        result = vendor_sdk.chat_completions_create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )
        return result["choices"][0]["message"]["content"]
