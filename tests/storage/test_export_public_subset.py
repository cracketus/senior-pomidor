import json

from brain.storage import export_public_subset


def test_export_filters_private_fields(tmp_path):
    src = tmp_path / "in.jsonl"
    out = tmp_path / "out.jsonl"
    records = [
        {"a": 1, "b": 2, "secret": "no"},
        {"a": 3, "b": 4, "secret": "nope"},
    ]
    with src.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    export_public_subset(src, out, whitelist=["a", "b"])
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    for line in lines:
        obj = json.loads(line)
        assert "secret" not in obj
