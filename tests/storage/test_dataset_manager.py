from datetime import date

from brain.storage import DatasetManager


def test_create_run_directory(tmp_path):
    mgr = DatasetManager(tmp_path)
    run_dir = mgr.create_run_dir(date(2026, 2, 14))
    assert run_dir.exists()
    assert run_dir.name == "run_2026-02-14"


def test_writer_for(tmp_path):
    mgr = DatasetManager(tmp_path)
    run_dir = mgr.create_run_dir()
    writer = mgr.writer_for(run_dir, "state.jsonl", fsync=False)
    writer.append({"a": 1})
    p = run_dir / "state.jsonl"
    assert p.exists()
