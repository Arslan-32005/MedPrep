from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file
)

from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    ListFlowable,
    ListItem,
    KeepTogether
)

from gemini_service import generate_visit_summary


app = Flask(__name__)


# -----------------------------------
# HOME
# -----------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------------
# SAFETY NOTICE
# -----------------------------------

def build_safety_notice(patient_data):

    symptoms = patient_data.get("symptoms", [])

    if not isinstance(symptoms, list):
        symptoms = []

    urgent_symptoms = [
        symptom
        for symptom in symptoms
        if symptom in ["Chest pain", "Breathing difficulty"]
    ]

    if urgent_symptoms:

        symptom_text = ", ".join(urgent_symptoms)

        return {
            "level": "warning",
            "title": "Important Safety Notice",
            "message": (
                f"You selected: {symptom_text}. "
                "If these symptoms are severe, sudden, or worsening, "
                "seek emergency medical care immediately. "
                "Do not wait for an AI-generated report."
            )
        }

    return {
        "level": "info",
        "title": "Health Safety Reminder",
        "message": (
            "If any symptom is sudden, severe, rapidly worsening, "
            "or you feel in immediate danger, seek urgent medical care "
            "instead of waiting for this application."
        )
    }


# -----------------------------------
# GENERATE SUMMARY + QUESTIONS
# -----------------------------------

@app.route("/generate", methods=["POST"])
def generate():

    data = request.get_json(silent=True) or {}

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Invalid request data."
        }), 400

    main_problem = data.get("main_problem", "")

    if not isinstance(main_problem, str) or not main_problem.strip():

        return jsonify({
            "success": False,
            "error": "Please enter your main health concern."
        }), 400

    if len(main_problem) > 5000:

        return jsonify({
            "success": False,
            "error": "Main health concern is too long."
        }), 400

    try:

        # Generate AI content
        ai_result = generate_visit_summary(data)

        # Generate safety notice separately
        safety_notice = build_safety_notice(data)

        report = {
            "summary": ai_result["summary"],
            "doctor_questions": ai_result["doctor_questions"],
            "safety_notice": safety_notice
        }

        return jsonify({
            "success": True,
            "report": report
        })

    except Exception:
        app.logger.exception("Summary generation failed")

        return jsonify({
            "success": False,
            "error": (
                "Unable to generate the report. "
                "Please check your API key and internet connection."
            )
        }), 500


# -----------------------------------
# PDF MARKDOWN FORMATTER
# -----------------------------------

def format_markdown_line(text):

    safe_text = escape(str(text))

    safe_text = re.sub(
        r"\*\*(.*?)\*\*",
        r"<b>\1</b>",
        safe_text
    )

    safe_text = re.sub(
        r"\*(.*?)\*",
        r"<i>\1</i>",
        safe_text
    )

    return safe_text


# -----------------------------------
# ADD SUMMARY TO PDF
# -----------------------------------

def add_summary_to_pdf(story, summary, styles):

    bullet_items = []

    def flush_bullets():

        if bullet_items:

            story.append(
                ListFlowable(
                    [
                        ListItem(
                            Paragraph(
                                item,
                                styles["ReportBullet"]
                            )
                        )
                        for item in bullet_items
                    ],
                    bulletType="bullet",
                    leftIndent=18
                )
            )

            story.append(Spacer(1, 6))
            bullet_items.clear()

    for raw_line in summary.splitlines():

        line = raw_line.strip()

        if not line:
            flush_bullets()
            continue

        if line.startswith("- ") or line.startswith("* "):

            bullet_items.append(
                format_markdown_line(line[2:])
            )

            continue

        flush_bullets()

        if line.startswith("### "):

            story.append(
                Paragraph(
                    format_markdown_line(line[4:]),
                    styles["SectionHeading"]
                )
            )

        elif line.startswith("## "):

            story.append(
                Paragraph(
                    format_markdown_line(line[3:]),
                    styles["SectionHeading"]
                )
            )

        elif line.startswith("# "):

            story.append(
                Paragraph(
                    format_markdown_line(line[2:]),
                    styles["SectionHeading"]
                )
            )

        else:

            story.append(
                Paragraph(
                    format_markdown_line(line),
                    styles["ReportBody"]
                )
            )

    flush_bullets()


# -----------------------------------
# CREATE COMPLETE PDF
# -----------------------------------

def create_pdf(report):

    buffer = BytesIO()

    navy = colors.HexColor("#183247")
    teal = colors.HexColor("#287C7C")
    muted = colors.HexColor("#687983")

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=22 * mm,
        leftMargin=22 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="MedPrep Doctor Visit Report"
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=29,
            alignment=TA_CENTER,
            textColor=navy,
            spaceAfter=6
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            alignment=TA_CENTER,
            textColor=muted,
            spaceAfter=12
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=18,
            textColor=teal,
            spaceBefore=13,
            spaceAfter=7
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=16,
            textColor=navy,
            spaceAfter=8
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportBullet",
            parent=styles["BodyText"],
            fontSize=10,
            leading=15,
            textColor=navy,
            spaceAfter=4
        )
    )

    styles.add(
        ParagraphStyle(
            name="SafetyText",
            parent=styles["BodyText"],
            fontSize=9,
            leading=15,
            textColor=colors.HexColor("#754B22")
        )
    )

    story = []

    # Header

    story.append(
        Paragraph("MedPrep", styles["ReportTitle"])
    )

    story.append(
        Paragraph(
            "DOCTOR VISIT PREPARATION REPORT",
            styles["ReportSubtitle"]
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=teal,
            spaceAfter=14
        )
    )

    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y')}",
            styles["ReportSubtitle"]
        )
    )

    # Part 1: Summary

    story.append(
        Paragraph(
            "01. Doctor Visit Summary",
            styles["SectionHeading"]
        )
    )

    add_summary_to_pdf(
        story,
        report["summary"],
        styles
    )

    # Part 2: Doctor questions

    questions = report.get("doctor_questions", [])

    if questions:

        question_section = [
            Paragraph(
                "02. Questions to Discuss with Your Doctor",
                styles["SectionHeading"]
            )
        ]

        question_section.append(
            ListFlowable(
                [
                    ListItem(
                        Paragraph(
                            format_markdown_line(question),
                            styles["ReportBullet"]
                        )
                    )
                    for question in questions
                ],
                bulletType="1",
                leftIndent=20
            )
        )

        story.append(KeepTogether(question_section))

    # Part 3: Safety notice

    notice = report.get("safety_notice", {})

    if notice:

        story.append(
            Paragraph(
                "03. Safety Notice",
                styles["SectionHeading"]
            )
        )

        notice_text = (
            f"<b>{escape(notice.get('title', 'Safety Notice'))}</b><br/>"
            f"{escape(notice.get('message', ''))}"
        )

        story.append(
            Paragraph(
                notice_text,
                styles["SafetyText"]
            )
        )

    # Footer

    story.append(Spacer(1, 20))

    story.append(
        HRFlowable(
            width="100%",
            thickness=0.7,
            color=colors.HexColor("#DDE5E9")
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "MedPrep organizes patient-provided information for "
            "communication with a healthcare professional. "
            "It is not a diagnostic tool or treatment plan.",
            styles["ReportSubtitle"]
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer


# -----------------------------------
# DOWNLOAD PDF
# -----------------------------------

@app.route("/download-pdf", methods=["POST"])
def download_pdf():

    data = request.get_json(silent=True) or {}

    report = data.get("report")

    if not isinstance(report, dict):

        return jsonify({
            "success": False,
            "error": "Invalid report."
        }), 400

    summary = report.get("summary")
    questions = report.get("doctor_questions")
    safety_notice = report.get("safety_notice")

    if not isinstance(summary, str) or not summary.strip():

        return jsonify({
            "success": False,
            "error": "Summary is missing."
        }), 400

    if not isinstance(questions, list) or not all(
        isinstance(question, str) for question in questions
    ):

        return jsonify({
            "success": False,
            "error": "Doctor questions are invalid."
        }), 400

    if not isinstance(safety_notice, dict):

        return jsonify({
            "success": False,
            "error": "Safety notice is missing."
        }), 400

    if len(summary) > 15000:

        return jsonify({
            "success": False,
            "error": "Summary is too large."
        }), 400

    try:

        pdf_buffer = create_pdf({
            "summary": summary,
            "doctor_questions": questions[:5],
            "safety_notice": {
                "title": str(safety_notice.get("title", "Safety Notice")),
                "message": str(safety_notice.get("message", ""))
            }
        })

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="MedPrep_Doctor_Report.pdf"
        )

    except Exception:

        app.logger.exception("PDF generation failed")

        return jsonify({
            "success": False,
            "error": "Unable to create PDF."
        }), 500


# -----------------------------------
# RUN SERVER
# -----------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )