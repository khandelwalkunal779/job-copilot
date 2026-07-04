import os
import json


def save_json(data_dict, file_path):
    """Saves a dictionary as formatted JSON to the specified path."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data_dict, f, indent=2, ensure_ascii=False)
    print(f"Saved extracted skills to: {file_path}")
