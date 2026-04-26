import hashlib
import math


class DeterministicEmbeddingProvider:
    """Small local embedding provider for repeatable development and tests.

    This is not meant to be a high-quality semantic model. It exists so the
    pgvector path is real from day one without adding an external API key.
    """

    def __init__(self, dimensions: int = 64) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = _tokens(text)
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            sign = 1.0 if digest[2] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [round(value / norm, 6) for value in vector]


def vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(value) for value in vector) + "]"


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in text.replace("_", " ").replace("-", " ").split()]

