import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = "gemini-3.1-flash-lite"


def generate_visit_summary(patient_data: dict) -> dict:

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing in .env")

    clean_data = {}

    for key, value in patient_data.items():

        if value is None:
            continue

        if isinstance(value, str) and not value.strip():
            continue

        if isinstance(value, list) and not value:
            continue

        clean_data[key] = value

    main_problem = clean_data.get("main_problem")

    if not main_problem:
        raise ValueError("Main health concern is required.")

    language = clean_data.pop("summary_language", "auto")

    if language == "roman_urdu":
        language_instruction = """
        Write all output in natural Roman Urdu using Latin letters.
        Never use Urdu script.
        """

    elif language == "english":
        language_instruction = """
        Write all output in clear, professional English.
        """

    else:
        language_instruction = """
        Detect the dominant language of the patient's main concern
        and explanations.

        If primarily Roman Urdu, respond in Roman Urdu.
        If primarily English, respond in English.
        For mixed input, use the dominant language.
        Never use Urdu script.
        """

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are MedPrep, an AI-powered doctor-visit preparation assistant.

PATIENT INFORMATION:
{json.dumps(clean_data, ensure_ascii=False, indent=2)}

LANGUAGE:
{language_instruction}

YOUR TASK:
Create a patient visit summary and a doctor discussion guide.

PART 1: VISIT SUMMARY

- Create an informative, professionally written summary.
- Aim for 150-250 words when sufficient information is available.
- If fewer details are provided, keep it proportionate.
- Include the main concern, duration, symptoms and relevant
  medical information actually supplied by the patient.
- Use headings and bullet points where appropriate.
- Never mention missing fields.
- Never invent information or repeat details unnecessarily.
- Preserve the meaning of the patient's statements.

PART 2: DOCTOR DISCUSSION QUESTIONS

Create 3-5 useful questions the patient can discuss with their doctor.

- Base questions on the patient's actual concern and information.
- Questions may help clarify onset, frequency, progression,
  triggers or impact on daily life.
- Avoid suggesting a particular disease.
- Never make a diagnosis.
- Never recommend medication or treatment.
- Use simple, understandable language.
- Do not ask questions that assume an unreported symptom.

SAFETY RULES:

- Never predict that the patient has heart disease or any other disease.
- Never provide disease probabilities or risk scores.
- Never claim that the patient is healthy or safe.
- Do not prescribe medicines or treatments.
- This is not a diagnostic system.

Return ONLY valid JSON with this exact structure:

{{
    "summary": "Complete formatted summary using Markdown",
    "doctor_questions": [
        "Question 1",
        "Question 2",
        "Question 3"
    ]
}}

Do not include Markdown code fences around the JSON.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    raw_response = response.text.strip()

    # Remove accidental Markdown code fences
    if raw_response.startswith("```"):

        raw_response = raw_response.replace(
            "```json", "", 1
        ).replace(
            "```", ""
        ).strip()

    try:
        result = json.loads(raw_response)

    except json.JSONDecodeError:

        start = raw_response.find("{")
        end = raw_response.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("Invalid AI response format.")

        result = json.loads(raw_response[start:end + 1])

    summary = result.get("summary")
    questions = result.get("doctor_questions")

    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("AI did not generate a valid summary.")

    if not isinstance(questions, list):
        raise ValueError("AI did not generate doctor questions.")

    questions = [
        question.strip()
        for question in questions
        if isinstance(question, str) and question.strip()
    ][:5]

    if len(questions) < 3:
        raise ValueError("AI generated fewer than three questions.")

    return {
        "summary": summary.strip(),
        "doctor_questions": questions
    }