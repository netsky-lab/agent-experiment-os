def responses_create(*, model: str, input: str, metadata: dict | None = None) -> dict:
    style = (metadata or {}).get("style", "plain")
    return {
        "id": "resp.local",
        "model": model,
        "output_text": f"local response: {input} [{style}]",
    }


def chat_completions_create(*, model: str, messages: list[dict]) -> dict:
    raise RuntimeError("local API drift: inspect and use responses_create")

