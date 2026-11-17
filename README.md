# MedPrep — AI-Powered Doctor Visit Preparation Assistant

**Prepare for better conversations with your doctor.**

MedPrep is an AI-powered Doctor Visit Preparation Assistant that helps patients organize their health concerns and relevant medical information before visiting a healthcare professional.

Using a guided form and Google's Gemini AI, MedPrep transforms patient-provided information into a structured doctor-visit summary, generates relevant questions to discuss with a doctor, and provides a downloadable PDF report.

MedPrep supports both English and Roman Urdu, making it easier for patients to explain their concerns in their preferred language.

> **Important:** MedPrep is a preparation and communication tool. It does not diagnose medical conditions, predict diseases, prescribe medication, or replace professional medical advice.

---

## Problem Statement

Patients sometimes struggle to communicate their health concerns effectively during medical appointments.

They may forget important details, such as:

- When their symptoms started.
- Which symptoms they have experienced.
- How frequently symptoms occur.
- How their symptoms affect daily activities.
- Which medications they currently take.
- Relevant medical history or previous treatments.

Writing all this information in an organized way can be difficult, especially for people who are not comfortable explaining medical concerns in English.

As a result, important information may be overlooked during a consultation.

## Our Solution

MedPrep provides a structured and multilingual platform that helps patients prepare for their doctor visits.

Instead of asking patients to write complicated AI prompts, MedPrep collects information through a simple, guided form.

Gemini AI processes the information and generates three main outputs:

1. **Doctor Visit Summary:** An organized summary of the patient's reported health concerns and relevant medical information.
2. **Doctor Discussion Guide:** Three to five relevant questions that patients can discuss with their healthcare professional.
3. **Safety Notice:** A precautionary notice based on selected symptoms, reminding users to seek urgent medical attention when appropriate.

Patients can review the generated report and download it as a professionally formatted PDF.

---

## Key Features

### 1. Structured Patient Information Collection

MedPrep collects information through dedicated form fields instead of relying entirely on free-text prompts.

Patients can provide:

**Main Health Concern**
- Description of the main problem.
- Duration of the concern.
- Selected symptoms.

**Patient Information**
- Patient name.
- Age.
- Gender.
- Affected body part.

**Symptom Details**
- Other symptoms.
- Symptom severity.
- Frequency.
- Effect on daily activities.

**Medical History**
- Existing medical conditions.
- Current medications.
- Known allergies.
- Previous treatments or medical tests.

**Additional Information**
- Any other relevant information the patient wants to share with their doctor.

Optional fields are excluded from the generated report when the patient leaves them empty.

### 2. Multilingual AI Support

Patients can describe their concerns in:

- English
- Roman Urdu

MedPrep provides three language options for the generated summary:

- Same as patient's input (Auto Detect).
- English.
- Roman Urdu.

This helps patients communicate their health concerns naturally without requiring them to write complicated English medical descriptions.

### 3. AI-Powered Doctor Visit Summary

MedPrep uses Google's Gemini AI to organize patient-provided information into a readable document.

The generated summary may include:

- Main health concern.
- Reported symptoms.
- Duration and frequency.
- Symptom severity and daily-life impact.
- Relevant medical history.
- Current medications and allergies.
- Previous treatments or tests.
- Additional information.

The AI includes only relevant information supplied by the patient and avoids filling empty fields with unnecessary placeholders.

The summary format adapts to the amount of information provided. It can use paragraphs, headings, and bullet points.

### 4. Doctor Discussion Guide

MedPrep generates three to five questions based on the patient's reported information.

These questions help patients prepare for their medical appointments.

Examples include:

- When did you first notice this concern?
- How frequently have you experienced these symptoms?
- Has the problem changed since it started?
- How does it affect your daily activities?

These are discussion prompts, not disease predictions or medical recommendations.

### 5. Symptom-Based Safety Notices

MedPrep includes a basic rule-based safety notice feature.

When a patient selects certain symptoms, such as:

- Chest pain.
- Breathing difficulty.

The application displays an additional warning explaining that severe, sudden, or worsening symptoms may require emergency medical attention.

A general health safety reminder is also displayed for other cases.

**Safety limitation:** This is not a comprehensive emergency screening system. It does not evaluate every possible emergency symptom or determine whether a patient is medically safe.

### 6. Professional PDF Report

Patients can download their generated doctor-visit report as a PDF.

The report contains:

- Doctor Visit Summary.
- Questions to Discuss with Your Doctor.
- Safety Notice.
- Report generation date.
- MedPrep branding and disclaimer.

The PDF is generated dynamically using ReportLab.

---

## How MedPrep Works

```text
Patient Opens MedPrep
         |
         v
Enters Main Health Concern
         |
         v
Selects Duration and Symptoms
         |
         v
Adds Optional Medical Details
         |
         v
Selects Summary Language
         |
         v
Information Sent to Gemini AI
         |
         v
AI Generates Visit Summary
         |
         v
AI Generates Doctor Questions
         |
         v
Application Generates Safety Notice
         |
         v
Complete Report Displayed
         |
         v
Download Professional PDF
```

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Flask | Backend framework and API routes |
| HTML5 | Frontend structure |
| CSS3 | Custom frontend styling |
| Bootstrap 5.3 | Responsive UI components and layout |
| JavaScript | Form handling and frontend interactions |
| Google Gemini 3.1 Flash-Lite | AI-powered summary and question generation |
| Google Gen AI SDK | Gemini API integration |
| python-dotenv | Environment variable management |
| ReportLab | PDF report generation |

---

## Project Architecture

MedPrep uses a simple Flask-based architecture.

```text
                    PATIENT
                       |
                       v
                Bootstrap Frontend
                  (index.html)
                       |
                       v
                JavaScript (app.js)
                       |
                       v
                 Flask Backend
                    (app.py)
                       |
             +---------+---------+
             |                   |
             v                   v
       Gemini Service       Safety Rules
    (gemini_service.py)     (app.py)
             |
             v
        Gemini API
             |
             v
     Summary + Questions
             |
             v
       Frontend Report
             |
             v
        PDF Generator
          (ReportLab)
             |
             v
        Download PDF
```

---

## Project Structure

```text
MedPrep/
│
├── app.py
├── gemini_service.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
│
├── templates/
│   └── index.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    ├── js/
    │   └── app.js
    │
    └── images/
```

### File Responsibilities

| File | Responsibility |
|---|---|
| `app.py` | Flask routes, safety notices, PDF generation |
| `gemini_service.py` | Gemini API integration and AI content generation |
| `index.html` | Main frontend interface |
| `style.css` | Custom responsive styling |
| `app.js` | Form interactions, API requests and report rendering |
| `requirements.txt` | Python dependencies |
| `.env` | Stores the Gemini API key locally |
| `.env.example` | Example environment variable configuration |

---

## Installation and Setup

### Prerequisites

Before running MedPrep, make sure you have:

- Python 3.10 or newer.
- Anaconda or a Python installation.
- A Google Gemini API key.
- Git (optional, for cloning the repository).

### 1. Clone the Repository

```bash
git clone https://github.com/Arslan-32005/MedPrep.git
```

Navigate into the project directory:

```bash
cd MedPrep
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory.

Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

You can obtain an API key through Google AI Studio:

https://aistudio.google.com/app/apikey

**Important:** Never upload your actual `.env` file or API key to GitHub.

### 4. Run the Application

Start the Flask development server:

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

MedPrep should now be running locally.

---

## AI Model Integration

MedPrep uses Google's Gemini 3.1 Flash-Lite model through the Google Gen AI SDK.

The model is responsible for:

1. Understanding patient-provided information.
2. Organizing relevant details into a readable summary.
3. Generating questions for discussion with a healthcare professional.
4. Following the patient's selected output language.
5. Avoiding unsupported diagnoses, medication recommendations and invented information.

The safety notice is generated separately through application rules rather than relying solely on AI interpretation.

### AI Output Principles

- Patient-provided information only.
- No invented medical history.
- No disease diagnosis.
- No disease probabilities or risk scores.
- No medication prescriptions.
- No unnecessary missing-field placeholders.
- Language-aware report generation.

---

## Limitations and Responsible AI

MedPrep is an early-stage hackathon MVP, not a clinically validated healthcare product.

The following limitations are important:

- The generated summary may misunderstand or incorrectly organize patient information.
- AI-generated discussion questions are suggestions, not medical advice.
- Language detection may not always correctly identify mixed English and Roman Urdu input.
- The current safety notices cover only selected symptom checkboxes and do not screen for every emergency.
- Uploaded medical documents and image-based medical analysis are not currently supported.
- The application does not maintain a patient database or appointment history.
- The application has no user authentication or patient account management.
- No clinical validation has been performed.

Patients should verify their generated summaries with a qualified healthcare professional.

**Emergency situations:** Patients experiencing severe, sudden or worsening symptoms should seek urgent medical attention rather than waiting for an AI-generated report.

---

## Privacy and Data Handling

MedPrep does not currently use a database to persist patient records.

However, patient information entered into the application is sent to Google's Gemini API for AI processing.

Therefore:

- Do not use real identifiable patient information for public demonstrations.
- Use fictional or anonymized information when testing.
- Never commit API keys or credentials to GitHub.
- Review the applicable Google AI API data-handling terms before using real patient information.

The current MVP does not provide a formal healthcare data compliance or certification guarantee.

---

## Future Improvements

Potential future development includes:

- Better symptom history and timeline collection.
- Support for additional languages.
- Improved accessibility for patients with limited digital literacy.
- Optional medical document attachment.
- More comprehensive, clinically reviewed emergency guidance.
- Patient report history with appropriate privacy controls.
- Improved PDF customization.
- Integration with healthcare appointment workflows.
- Clinical evaluation with qualified medical professionals before any diagnostic or risk-assessment functionality is considered.

These are planned possibilities, not currently implemented features.

---

## Project Goal

MedPrep aims to improve how patients prepare for and communicate their health concerns during medical appointments.

Rather than functioning as another general-purpose AI chatbot, MedPrep provides a structured, multilingual workflow designed specifically around doctor-visit preparation.

**MedPrep — Better prepared conversations, better-informed visits.**

---

*Disclaimer: MedPrep is an educational and informational hackathon project. It is not intended to diagnose, treat, cure, or prevent any disease and must not replace professional medical consultation.*
