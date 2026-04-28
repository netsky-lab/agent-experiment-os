from agent_client.adapters.legacy_chat_adapter import LegacyChatAdapter


def build_reply(prompt: str) -> str:
    adapter = LegacyChatAdapter(model="local-small")
    return adapter.generate(prompt)
