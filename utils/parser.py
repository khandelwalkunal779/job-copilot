import os
import requests
from html.parser import HTMLParser
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# =====================================================================
# Pydantic Schemas for Structured JSON Output
# =====================================================================


class ObjectiveSkills(BaseModel):
    experience_years: Optional[float] = Field(
        None,
        description="Measurable years of professional work experience explicitly stated in the document. If not, try to interpret using current date and joining date of professional experiences. Represent as a float if applicable (e.g. 2.5).",
    )
    grades: Optional[str] = Field(
        None,
        description="Quantifiable academic grades, GPA, percentages, or test ranks/scores explicitly mentioned in the document.",
    )
    education_universities: List[str] = Field(
        default_factory=list,
        description="Names of universities, colleges, or academic institutions from where the candidate received formal education.",
    )
    degrees: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Degrees or academic credentials earned or in-progress (e.g. B.Tech, M.S., Ph.D.) mapped against the specialisation (e.g. Civil Engineering, Electrical Engineering).",
    )
    experience_organizations: List[str] = Field(
        default_factory=list,
        description="Names of companies, employers, or organizations the candidate has worked with, exactly as is mentioned within the document.",
    )
    certifications: List[str] = Field(
        default_factory=list,
        description="Professional certifications, licenses, or courses completed.",
    )
    publications_patents: List[str] = Field(
        default_factory=list,
        description="List of academic publications, patents, or research papers mentioned.",
    )
    location: Optional[str] = Field(
        None,
        description="The candidate's location, city, state, or country if mentioned in the document.",
    )
    other_qualifications: List[str] = Field(
        default_factory=list,
        description="Other quantifiable or measurable academic/professional achievements (e.g. specific honors, awards, or internships).",
    )


class TechnicalSkills(BaseModel):
    programming_languages: Dict[str, int] = Field(
        default_factory=dict,
        description="Programming languages (e.g. Python, SQL, C++, Java, JavaScript) mapped to an integer score from 1 to 5. Set score based on frequency/prominence of appearance.",
    )
    frameworks: Dict[str, int] = Field(
        default_factory=dict,
        description="Frameworks, libraries, and SDKs (e.g. PySpark, React, PyTorch, OpenCV, Playwright, LangChain) mapped to an integer score from 1 to 5.",
    )
    cloud_and_platforms: Dict[str, int] = Field(
        default_factory=dict,
        description="Cloud services and data/development platforms (e.g. AWS, Azure, GCP, Databricks, Snowflake) mapped to an integer score from 1 to 5.",
    )
    technical_fields: Dict[str, int] = Field(
        default_factory=dict,
        description="Technical fields and domain areas (e.g. Machine Learning, Deep Learning, Computer Vision, NLP, Intelligent Document Processing, DevOps, Frontend) mapped to an integer score from 1 to 5.",
    )
    technical_systems: Dict[str, int] = Field(
        default_factory=dict,
        description="Technical systems and infrastructure concepts (e.g. Operating Systems like Linux/Windows, databases like MySQL/PostgreSQL, Git, API integrations) mapped to an integer score from 1 to 5.",
    )
    other_skills: Dict[str, int] = Field(
        default_factory=dict,
        description="Other technical tools, services, or methodologies (e.g. Microsoft Graph API, Docker, Jira, Agile) mapped to an integer score from 1 to 5.",
    )


class ExtractedInformation(BaseModel):
    objective_skills: ObjectiveSkills = Field(
        ...,
        description="Quantifiable objective background details, such as experience, grades, and qualifications.",
    )
    technical_skills: TechnicalSkills = Field(
        ...,
        description="Categorized technical skills mapped to their experience/prominence score from 1 to 5.",
    )
    subjective_skills: List[str] = Field(
        default_factory=list,
        description="List of subjective skillsets or soft skills (e.g., leadership, ownership, client management, communication, problem solving) mentioned in the document.",
    )


# =====================================================================
# Scoring Rubric / Instructions
# =====================================================================

SCORING_RUBRIC = """
For each technical skill identified, assign a score from 1 to 5 using the following objective, document-based rubric:
- **Score 5 (Expert/Primary)**: The skill is a primary focus, appearing repeatedly across multiple major projects with details of deep implementation/optimization or extensive usage (e.g., used to build the core system, or explicitly described as a primary expertise).
- **Score 4 (Advanced)**: The skill is used as a core tool in at least one major project or is mentioned multiple times with specific context (e.g., built a specific system or pipeline with it, or has detailed descriptions of its application).
- **Score 3 (Intermediate)**: The skill is mentioned in the context of project implementation but not as the central technology, or is listed under technical skills/tools with supporting project context.
- **Score 2 (Basic)**: The skill is mentioned briefly as a secondary tool or listed in a skills section without much project context.
- **Score 1 (Familiar)**: The skill is only mentioned once or listed in passing without details of usage.

Important:
- Scores must be integers from 1 to 5.
- Only include skills that are explicitly mentioned in the document. Do not extrapolate skills not appearing in the text.
- If a skill is not mentioned, do not list it in the dictionary.
"""

# =====================================================================
# Parsing Functions
# =====================================================================


def get_llm():
    """Returns an instance of ChatGoogleGenerativeAI configured with Gemini 3.5 Flash."""
    return ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.0)


def parse_markdown(file_path: str) -> ExtractedInformation:
    """Parses a markdown file to extract objective and technical skills."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found at {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    llm = get_llm()
    structured_llm = llm.with_structured_output(ExtractedInformation)

    prompt = f"""
You are an expert technical recruiter and resume/project analyst.
Analyze the following project description document and extract objective skills and technical skills.

{SCORING_RUBRIC}

Document Content:
---
{content}
---
"""

    return structured_llm.invoke(prompt)


def parse_pdf(file_path: str) -> ExtractedInformation:
    """Parses a PDF file to extract objective and technical skills using multimodal Gemini input."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at {file_path}")

    # Get absolute path for the Files API
    abs_path = os.path.abspath(file_path)

    # Initialize the google-genai client to upload the file
    client = genai.Client()
    print(f"Uploading PDF file to Gemini Files API: {file_path}...")
    uploaded_file = client.files.upload(file=abs_path)
    print(f"Upload complete. URI: {uploaded_file.uri}")

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(ExtractedInformation)

        prompt = f"""
You are an expert technical recruiter and resume/project analyst.
Analyze the attached resume PDF document and extract objective skills and technical skills.

{SCORING_RUBRIC}
"""

        # Construct multimodal message using LangChain's HumanMessage schema
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "media",
                    "file_uri": uploaded_file.uri,
                    "mime_type": "application/pdf",
                },
            ]
        )

        print("Invoking Gemini for PDF parsing...")
        result = structured_llm.invoke([message])
        return result

    finally:
        # Always clean up the uploaded file to free storage space
        print("Cleaning up uploaded file from Gemini...")
        client.files.delete(name=uploaded_file.name)
        print("Cleanup complete.")


def parse_html(url: str) -> ExtractedInformation:
    """Fetches a webpage URL, extracts text from the HTML, and parses structured skills using Gemini."""

    class HTMLTextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.result = []
            self.in_script_or_style = False

        def handle_starttag(self, tag, attrs):
            if tag in ("script", "style"):
                self.in_script_or_style = True

        def handle_endtag(self, tag):
            if tag in ("script", "style"):
                self.in_script_or_style = False

        def handle_data(self, data):
            if not self.in_script_or_style:
                text = data.strip()
                if text:
                    self.result.append(text)

        def get_text(self):
            return "\n".join(self.result)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    print(f"Fetching job description webpage: {url}...")
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    # Parse and extract raw text from HTML body
    extractor = HTMLTextExtractor()
    extractor.feed(response.text)
    extracted_text = extractor.get_text()

    llm = get_llm()
    structured_llm = llm.with_structured_output(ExtractedInformation)

    prompt = f"""
You are an expert technical recruiter and job description analyst.
Analyze the following extracted text content from a job description webpage and extract required objective skills and technical skills.

{SCORING_RUBRIC}

Webpage Content:
---
{extracted_text}
---
"""
    print("Invoking Gemini for HTML content parsing...")
    return structured_llm.invoke(prompt)
