def responses_create(*, model: str, input: str) -> dict:
    return {
        "id": "resp.local",
        "model": model,
        "output_text": f"local response: {input}",
    }


def chat_completions_create(*, model: str, messages: list[dict]) -> dict:
    raise RuntimeError("stale API: use responses_create from the local vendor shim")
