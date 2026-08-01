from pathlib import Path
import json, csv, pickle
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


def from_file(path):
    input_path = Path(path)
    if not input_path.is_absolute():
        input_path = Path(settings.BASE_DIR) / input_path
    if not input_path.exists():
        return None
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        with input_path.open("r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            return [row for row in reader]
    elif suffix == ".json":
        with input_path.open("r", encoding="utf-8") as json_file:
            return json.load(json_file)
    elif suffix == ".jsonl":
        with input_path.open("r", encoding="utf-8") as json_file:
            return [json.loads(line) for line in json_file]
    return None


def save_artifact(path, artifact):
    output_path = Path(path)
    if not output_path.is_absolute():
        output_path = Path(settings.BASE_DIR) / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        pickle.dump(artifact, f)

def load_artifact(artifact_name):
    artifact_path = Path(settings.BASE_DIR) / Path(f"media/artifacts/{artifact_name}")
    with open(artifact_path, "rb") as f:
        artifact = pickle.load(f)
        return artifact
    return None