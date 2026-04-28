from agent_client import vendor_sdk


class ResponsesAdapter:
    def __init__(self, *, model: str) -> None:
        self._model = model

    def generate(self, prompt: str) -> str:
        result = vendor_sdk.responses_create(model=self._model, input=prompt)
        return result["output_text"]
