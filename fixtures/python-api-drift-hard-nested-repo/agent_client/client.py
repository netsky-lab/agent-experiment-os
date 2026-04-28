from agent_client.routing import ClientRouter


def build_reply(prompt: str) -> str:
    router = ClientRouter(model="local-small")
    adapter = router.build()
    return adapter.generate(prompt)
