import os
from pathlib import Path
import json
from dotenv import load_dotenv

from utils.parser import parse_markdown, parse_pdf
from utils.func_utils import save_json, print_header

load_dotenv()

try:
    configs = json.loads(Path("configs.json").read_text())
except Exception:
    configs = {}

DOCS_DIR = Path("./docs")
EXPORTS_DIR = Path("./exports")
EXPORTS_DIR.mkdir(exist_ok=True)


def main():
    print_header("Job Copilot", is_main=True)

    # =====================================================================
    # Processing profile documents
    # =====================================================================

    print_header("Processing Profile Documents")
    if not configs.get("process_profile", True):
        print(
            "Skipping profile processing: process_profile is set to False in configs."
        )
        return

    if not DOCS_DIR.exists():
        print(f"Error: The directory '{DOCS_DIR}' does not exist.")
        return

    files = [f for f in DOCS_DIR.iterdir() if f.is_file()]
    if not files:
        print(f"No files found in '{DOCS_DIR}' directory to process.")
        return

    print(
        f"Found {len(files)} files in '{DOCS_DIR}'. Processing based on file extensions..."
    )

    for file_path in files:
        filename = file_path.name
        ext = file_path.suffix.lower()
        base_name = file_path.stem

        export_path = EXPORTS_DIR / f"{base_name}_skills.json"

        print(f"\nProcessing: {filename} ({ext})")

        try:
            if ext == ".md":
                skills = parse_markdown(str(file_path))
            elif ext == ".pdf":
                skills = parse_pdf(str(file_path))
            else:
                print(
                    f"Skipping unsupported file extension '{ext}' for file '{filename}'."
                )
                continue

            skills_dict = skills.model_dump()
            save_json(skills_dict, str(export_path))

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # =====================================================================
    # Processing job descriptions
    # =====================================================================

    print("\n" + "=" * 60 + "\n")
    print_header("Processing Job Descriptions")

    jd_webpages = configs.get("jd_webpages", [])
    if not jd_webpages:
        print("Skipping profile processing: jd_webpages is Empty in configs.")
        return

    for webpage in jd_webpages:
        print(webpage)


if __name__ == "__main__":
    main()
