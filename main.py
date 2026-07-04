import os
import json
from dotenv import load_dotenv
from parser import parse_markdown, parse_pdf

# Load environment variables
load_dotenv()


def save_json(data_dict, file_path):
    """Saves a dictionary as formatted JSON to the specified path."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data_dict, f, indent=2, ensure_ascii=False)
    print(f"Saved extracted skills to: {file_path}")


def main():
    print("Starting Job-Copilot Document Parsing Framework...")

    # 1. Parse data/project_desc.md
    project_desc_path = "data/project_desc.md"
    project_desc_export = "exports/project_desc_skills.json"

    print(f"\n--- Parsing Project Description: {project_desc_path} ---")
    try:
        project_skills = parse_markdown(project_desc_path)
        # Convert pydantic model to dict
        project_skills_dict = project_skills.model_dump()
        save_json(project_skills_dict, project_desc_export)
    except Exception as e:
        print(f"Error parsing project description: {e}")

    # 2. Parse data/resume.pdf
    resume_path = "data/resume.pdf"
    resume_export = "exports/resume_skills.json"

    print(f"\n--- Parsing Resume PDF: {resume_path} ---")
    try:
        resume_skills = parse_pdf(resume_path)
        # Convert pydantic model to dict
        resume_skills_dict = resume_skills.model_dump()
        save_json(resume_skills_dict, resume_export)
    except Exception as e:
        print(f"Error parsing resume PDF: {e}")


if __name__ == "__main__":
    main()
