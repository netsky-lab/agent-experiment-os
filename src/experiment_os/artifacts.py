from pathlib import Path
from uuid import uuid4


class ArtifactStore:
    def __init__(
        self,
        root: Path = Path("artifacts"),
        fallback_root: Path = Path("runs/artifacts"),
    ) -> None:
        self._root = writable_root(root, fallback_root)

    def write_text(self, *, run_id: str, name: str, content: str) -> Path:
        run_dir = self._root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / name
        path.write_text(content, encoding="utf-8")
        return path


def writable_root(primary: Path, fallback: Path) -> Path:
    if _can_write(primary):
        return primary
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def _can_write(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / f".write-test-{uuid4().hex}"
        probe.write_text("", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False
