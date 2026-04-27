from agent_client import vendor_sdk


def build_reply(prompt: str) -> str:
    result = vendor_sdk.chat_completions_create(
        model="local-small",
        messages=[{"role": "user", "content": prompt}],
    )
    return result["choices"][0]["message"]["content"]
