import datetime
import json
import os
from pathlib import Path
from typing import Any, Optional


class JSONLWriter:
    """Simple JSONL writer with configurable fsync and basic rotation helpers.

    Each `append` opens the file, writes a single JSON line, flushes, and
    optionally calls `os.fsync` to force durability. This approach keeps the
    implementation simple and cross-platform while providing explicit fsync
    control for tests and production.
    """

    def __init__(self, path: str, fsync: bool = False, encoding: str = "utf-8"):
        self._path = Path(path)
        self._fsync = bool(fsync)
        self._encoding = encoding
        # ensure parent dir exists
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: Any) -> None:
        line = json.dumps(record, ensure_ascii=False) + "\n"
        # Open, write, flush, and optionally fsync on every append to ensure
        # durability and predictable behavior across platforms.
        with open(self._path, "a", encoding=self._encoding) as f:
            f.write(line)
            f.flush()
            if self._fsync:
                try:
                    os.fsync(f.fileno())
                except (AttributeError, OSError):
                    # Some platforms or file-like objects may not support fsync;
                    # swallow failures only after the write succeeded.
                    pass

    def rotate_on_size(self, max_bytes: int) -> Optional[Path]:
        """Rotate the current file if it exceeds `max_bytes`.

        Returns the rotated file path when rotation occurred, otherwise None.
        """
        if not self._path.exists():
            return None
        try:
            size = self._path.stat().st_size
        except OSError:
            return None
        if size <= max_bytes:
            return None
        ts = int(os.path.getmtime(self._path))
        rotated = self._path.with_name(f"{self._path.stem}.{ts}{self._path.suffix}")
        try:
            os.replace(self._path, rotated)
            return rotated
        except OSError:
            return None

    def rotate_on_day(self, day_boundary_date: datetime.date) -> Optional[Path]:
        """Rotate the file if its modification date is before `day_boundary_date`.

        The rotated file is renamed with the ISO date of its mtime: ``stem.YYYY-MM-DD.suffix``.
        Returns the rotated path or None if no rotation occurred.
        """
        if not self._path.exists():
            return None
        try:
            mtime = os.path.getmtime(self._path)
        except OSError:
            return None
        mdate = datetime.date.fromtimestamp(mtime)
        if mdate >= day_boundary_date:
            return None
        rotated = self._path.with_name(f"{self._path.stem}.{mdate.isoformat()}{self._path.suffix}")
        try:
            os.replace(self._path, rotated)
            return rotated
        except OSError:
            return None
