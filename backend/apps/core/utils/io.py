from pathlib import Path
import json, csv
from decimal import Decimal

from django.conf import settings

def _json_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def to_file(path, data):
    output_path = Path(path)
    if not output_path.is_absolute():
        output_path = Path(settings.BASE_DIR) / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if data is None:
        return
    rows = data

    suffix = output_path.suffix.lower()
    if suffix == ".csv":
        fieldnames = rows[0].keys() if rows else []
        with output_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    elif suffix in {".json", ".jsonl"}:
        with output_path.open("w", encoding="utf-8") as json_file:
            if suffix == ".jsonl":
                for row in rows:
                    json_file.write(json.dumps(row, default=_json_default) + "\n")
            else:
                json.dump(rows, json_file, indent=2, default=_json_default)