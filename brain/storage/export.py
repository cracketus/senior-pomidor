import json
from pathlib import Path
from typing import Iterable


def export_public_subset(
    input_file: str | Path,
    output_file: str | Path,
    *,
    whitelist: Iterable[str],
):
    """Read `input_file` (JSONL) and write a filtered JSONL `output_file`.

    Only whitelisted fields are retained. Non-present fields are omitted. Any
    invalid JSON lines are skipped.
    """
    in_path = Path(input_file)
    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wl = set(whitelist)
    with in_path.open("r", encoding="utf-8") as inf, out_path.open("w", encoding="utf-8") as outf:
        for line in inf:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                # skip malformed lines
                continue
            filtered = {k: v for k, v in obj.items() if k in wl}
            outf.write(json.dumps(filtered, ensure_ascii=False) + "\n")
