// ========================================
// MEDPREP FRONTEND
// ========================================

const form = document.getElementById("medprepForm");

const generateBtn = document.getElementById("generateBtn");
const downloadBtn = document.getElementById("downloadBtn");
const editBtn = document.getElementById("editBtn");

const loadingOverlay = document.getElementById("loadingOverlay");
const resultSection = document.getElementById("resultSection");

const summaryContent = document.getElementById("summaryContent");
const summaryDate = document.getElementById("summaryDate");

const doctorQuestions = document.getElementById("doctorQuestions");
const questionsCount = document.getElementById("questionsCount");

const safetyNotice = document.getElementById("safetyNotice");
const safetyTitle = document.getElementById("safetyTitle");
const safetyMessage = document.getElementById("safetyMessage");

const messageBox = document.getElementById("messageBox");

const characterCount = document.getElementById("characterCount");

let currentReport = null;


// ========================================
// CHARACTER COUNTER
// ========================================

const mainConcernInput = document.getElementById("mainConcern");

mainConcernInput.addEventListener("input", function () {

    characterCount.textContent =
        `${this.value.length} / 5000`;

});


// ========================================
// INPUT HELPER
// ========================================

function getValue(id) {

    const element = document.getElementById(id);

    return element ? element.value.trim() : "";

}


// ========================================
// SHOW ERROR / MESSAGE
// ========================================

function showMessage(message, type = "danger") {

    messageBox.className = `alert alert-${type} mt-3`;

    messageBox.textContent = message;

    messageBox.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

}


function hideMessage() {

    messageBox.className = "alert d-none mt-3";

    messageBox.textContent = "";

}


// ========================================
// COLLECT PATIENT INFORMATION
// ========================================

function collectPatientData() {

    const selectedSymptoms = Array.from(
        document.querySelectorAll(
            'input[name="symptoms"]:checked'
        )
    ).map(element => element.value);


    const patientData = {

        main_problem: getValue("mainConcern"),

        duration: getValue("duration"),

        symptoms: selectedSymptoms,

        summary_language: getValue("summaryLanguage")

    };


    const optionalFields = {

        patient_name: getValue("patientName"),

        age: getValue("age"),

        gender: getValue("gender"),

        body_part: getValue("bodyPart"),

        frequency: getValue("frequency"),

        severity: getValue("severity"),

        other_symptoms: getValue("otherSymptoms"),

        daily_impact: getValue("dailyImpact"),

        medical_history: getValue("medicalHistory"),

        medications: getValue("medications"),

        allergies: getValue("allergies"),

        previous_treatment: getValue("previousTreatment"),

        additional_info: getValue("additionalInfo")

    };


    Object.entries(optionalFields).forEach(([key, value]) => {

        if (value !== "") {
            patientData[key] = value;
        }

    });


    return patientData;

}


// ========================================
// SAFE MARKDOWN RENDERING
// ========================================

function escapeHTML(text) {

    return String(text).replace(/[&<>"']/g, function (character) {

        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        };

        return entities[character];

    });

}


function formatInlineMarkdown(text) {

    let safe = escapeHTML(text);

    safe = safe.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    safe = safe.replace(
        /\*(.*?)\*/g,
        "<em>$1</em>"
    );

    return safe;

}


// ========================================
// RENDER SUMMARY
// ========================================

function renderSummary(markdown) {

    const lines = markdown.split("\n");

    let html = "";

    let listOpen = false;


    lines.forEach(rawLine => {

        const line = rawLine.trim();


        if (!line) {

            if (listOpen) {
                html += "</ul>";
                listOpen = false;
            }

            return;

        }


        if (line.startsWith("### ")) {

            if (listOpen) {
                html += "</ul>";
                listOpen = false;
            }

            html += `<h4>${formatInlineMarkdown(line.substring(4))}</h4>`;

            return;

        }


        if (line.startsWith("## ")) {

            if (listOpen) {
                html += "</ul>";
                listOpen = false;
            }

            html += `<h3>${formatInlineMarkdown(line.substring(3))}</h3>`;

            return;

        }


        if (line.startsWith("# ")) {

            if (listOpen) {
                html += "</ul>";
                listOpen = false;
            }

            html += `<h3>${formatInlineMarkdown(line.substring(2))}</h3>`;

            return;

        }


        if (line.startsWith("- ") || line.startsWith("* ")) {

            if (!listOpen) {

                html += "<ul>";

                listOpen = true;

            }

            html += `<li>${formatInlineMarkdown(line.substring(2))}</li>`;

            return;

        }


        if (line === "---") {

            if (listOpen) {
                html += "</ul>";
                listOpen = false;
            }

            html += "<hr>";

            return;

        }


        if (listOpen) {

            html += "</ul>";

            listOpen = false;

        }


        html += `<p>${formatInlineMarkdown(line)}</p>`;

    });


    if (listOpen) {
        html += "</ul>";
    }


    summaryContent.innerHTML = html;

}


// ========================================
// RENDER DOCTOR QUESTIONS
// ========================================

function renderQuestions(questions) {

    doctorQuestions.innerHTML = "";

    questionsCount.textContent = questions.length;


    questions.forEach(question => {

        const li = document.createElement("li");

        li.textContent = question;

        doctorQuestions.appendChild(li);

    });

}


// ========================================
// RENDER SAFETY NOTICE
// ========================================

function renderSafetyNotice(notice) {

    safetyTitle.textContent = notice.title;

    safetyMessage.textContent = notice.message;

    safetyNotice.classList.remove("warning", "info");

    if (notice.level === "warning") {
        safetyNotice.classList.add("warning");
    } else {
        safetyNotice.classList.add("info");
    }

}


// ========================================
// GENERATE REPORT
// ========================================

form.addEventListener("submit", async function (event) {

    event.preventDefault();

    hideMessage();


    const patientData = collectPatientData();


    if (!patientData.main_problem) {

        showMessage("Please describe your main health concern.");

        return;

    }


    generateBtn.disabled = true;

    loadingOverlay.classList.remove("d-none");


    try {

        const response = await fetch("/generate", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(patientData)

        });


        const result = await response.json();


        if (!response.ok || !result.success) {

            throw new Error(
                result.error || "Unable to generate report."
            );

        }


        currentReport = result.report;


        // Validate response

        if (
            !currentReport ||
            typeof currentReport.summary !== "string" ||
            !Array.isArray(currentReport.doctor_questions) ||
            !currentReport.safety_notice
        ) {

            throw new Error("The generated report is incomplete.");

        }


        renderSummary(currentReport.summary);

        renderQuestions(currentReport.doctor_questions);

        renderSafetyNotice(currentReport.safety_notice);


        summaryDate.textContent = new Date().toLocaleDateString(
            undefined,
            {
                day: "2-digit",
                month: "long",
                year: "numeric"
            }
        );


        resultSection.classList.remove("d-none");


        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });


    }

    catch (error) {

        showMessage(error.message);

    }

    finally {

        generateBtn.disabled = false;

        loadingOverlay.classList.add("d-none");

    }

});


// ========================================
// DOWNLOAD COMPLETE PDF
// ========================================

downloadBtn.addEventListener("click", async function () {

    if (!currentReport) {

        showMessage("Generate a report before downloading.");

        return;

    }


    const originalText = downloadBtn.innerHTML;

    downloadBtn.disabled = true;

    downloadBtn.textContent = "Preparing PDF...";


    try {

        const response = await fetch("/download-pdf", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                report: currentReport
            })

        });


        if (!response.ok) {

            const error = await response.json();

            throw new Error(
                error.error || "Unable to download PDF."
            );

        }


        const pdfBlob = await response.blob();

        const url = URL.createObjectURL(pdfBlob);

        const link = document.createElement("a");

        link.href = url;

        link.download = "MedPrep_Doctor_Report.pdf";

        document.body.appendChild(link);

        link.click();

        link.remove();

        URL.revokeObjectURL(url);


    }

    catch (error) {

        showMessage(error.message);

    }

    finally {

        downloadBtn.disabled = false;

        downloadBtn.innerHTML = originalText;

    }

});


// ========================================
// EDIT INFORMATION
// ========================================

editBtn.addEventListener("click", function () {

    form.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

});