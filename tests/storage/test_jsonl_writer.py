import json
import tempfile
from pathlib import Path

from brain.storage import JSONLWriter


def test_atomic_append_writes_valid_lines(tmp_path):
    out = tmp_path / "data.jsonl"
    writer = JSONLWriter(str(out), fsync=False)
    writer.append({"a": 1, "b": "hello"})
    assert out.exists()
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    obj = json.loads(lines[0])
    assert obj["a"] == 1
    assert obj["b"] == "hello"


def test_flush_and_fsync_modes(tmp_path):
    out = tmp_path / "data_fsync.jsonl"
    writer = JSONLWriter(str(out), fsync=True)
    # Ensure no exception is raised when fsync is requested and file is written
    writer.append({"x": 42})
    contents = out.read_text(encoding="utf-8")
    assert "\n" in contents
    assert json.loads(contents.strip())["x"] == 42
