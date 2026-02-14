from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

from .jsonl_writer import JSONLWriter


class DatasetManager:
    """Manage run directories and dataset lifecycle.

    Creates `run_YYYYMMDD` directories under a base path and provides
    helpers to create writers bound to the dataset.
    """

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def run_dir_name(self, run_date: Optional[date] = None) -> str:
        run_date = run_date or date.today()
        return f"run_{run_date.isoformat()}"

    def create_run_dir(self, run_date: Optional[date] = None) -> Path:
        name = self.run_dir_name(run_date)
        p = self.base_dir / name
        p.mkdir(parents=True, exist_ok=True)
        return p

    def writer_for(self, run_dir: Path, filename: str, fsync: bool = False) -> JSONLWriter:
        path = run_dir / filename
        return JSONLWriter(str(path), fsync=fsync)
