import shutil
from pathlib import Path
from uuid import uuid4

from experiment_os.artifacts import writable_root


class FixtureWorkspacePreparer:
    def __init__(
        self,
        root: Path = Path("artifacts/workdirs"),
        fallback_root: Path = Path("runs/workdirs"),
    ) -> None:
        self._root = writable_root(root, fallback_root)

    def prepare(self, *, fixture_path: Path, label: str) -> Path:
        if not fixture_path.exists():
            raise FileNotFoundError(f"Fixture path does not exist: {fixture_path}")

        safe_label = "".join(char if char.isalnum() or char in "-_" else "-" for char in label)
        workdir = self._root / f"{safe_label}-{uuid4().hex[:8]}"
        shutil.copytree(
            fixture_path,
            workdir,
            ignore=shutil.ignore_patterns("node_modules", ".git", "dist"),
        )
        return workdir
