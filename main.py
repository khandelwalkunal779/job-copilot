from pathlib import Path
import json
import hashlib
from dotenv import load_dotenv

from utils.parser import parse_markdown, parse_pdf, parse_html
from utils.func_utils import save_json, print_header

load_dotenv()

try:
    configs = json.loads(Path("configs.json").read_text())
except Exception:
    configs = {}

DOCS_DIR = Path("./docs")
EXPORTS_DIR = Path("./exports")
EXPORTS_DIR.mkdir(exist_ok=True)
TMP_DIR = Path("./tmp")
TMP_DIR.mkdir(exist_ok=True)


def main():
    print_header("Job Copilot", is_main=True)

    # =====================================================================
    # Processing profile documents
    # =====================================================================

    print_header("Processing Profile Documents")

    if configs.get("process_profile", True):
        if not DOCS_DIR.exists():
            print(f"Error: The directory '{DOCS_DIR}' does not exist.")
        else:
            files = [f for f in DOCS_DIR.iterdir() if f.is_file()]
            if not files:
                print(f"No files found in '{DOCS_DIR}' directory to process.")
            else:
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
    else:
        print(
            "Skipping profile processing: process_profile is set to False in configs."
        )

    # =====================================================================
    # Processing job descriptions
    # =====================================================================

    print("\n" + "=" * 60 + "\n")
    print_header("Processing Job Descriptions")

    if configs.get("process_jd", True):
        jd_webpages = configs.get("jd_webpages", [])
        if not jd_webpages:
            print(
                "Skipping job description processing: jd_webpages is Empty in configs."
            )
        else:
            print(f"Found {len(jd_webpages)} job description webpage(s). Processing...")
            for webpage in jd_webpages:
                print(f"\nProcessing webpage: {webpage}")
                try:
                    url_hash = hashlib.md5(webpage.encode("utf-8")).hexdigest()

                    existing_files = list(TMP_DIR.glob(f"*{url_hash}*"))
                    if existing_files:
                        print(
                            f"Webpage already processed: {webpage} (found file with hash {url_hash}). Skipping parse_html."
                        )
                        continue

                    skills = parse_html(webpage)
                    skills_dict = skills.model_dump()
                    filename = f"{url_hash}_skills.json"

                    # Prevent overly long filenames
                    if len(filename) > 100:
                        filename = filename[:95] + "_skills.json"

                    export_path = TMP_DIR / filename
                    save_json(skills_dict, str(export_path))

                except Exception as e:
                    print(f"Error processing webpage {webpage}: {e}")
    else:
        print(
            "Skipping job description processing: process_jd is set to False in configs."
        )


if __name__ == "__main__":
    main()
