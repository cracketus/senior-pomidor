import json
import time
from datetime import date, timedelta

from brain.storage import JSONLWriter


def test_rotate_on_size(tmp_path):
    p = tmp_path / "big.jsonl"
    writer = JSONLWriter(str(p), fsync=False)
    # write multiple lines to exceed small threshold
    for i in range(10):
        writer.append({"i": i, "v": "x" * 20})
    rotated = writer.rotate_on_size(50)
    assert rotated is not None
    assert rotated.exists()


def test_rotate_on_day(tmp_path):
    p = tmp_path / "today.jsonl"
    writer = JSONLWriter(str(p), fsync=False)
    writer.append({"hello": "world"})
    # ensure mtime is in the past by at least one day (not used directly)
    rotated = writer.rotate_on_day(date.today())
    # mtime is today's date; rotation should not happen
    assert rotated is None
    # force rotation by asking boundary of tomorrow
    rotated2 = writer.rotate_on_day(date.today() + timedelta(days=1))
    assert rotated2 is not None
    assert rotated2.exists()
