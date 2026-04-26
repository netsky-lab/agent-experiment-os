from pathlib import Path


class ArtifactStore:
    def __init__(self, root: Path = Path("artifacts")) -> None:
        self._root = root

    def write_text(self, *, run_id: str, name: str, content: str) -> Path:
        run_dir = self._root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / name
        path.write_text(content, encoding="utf-8")
        return path

