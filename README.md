# 🧬 Metabolic Diagnostic Engine

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a67d.svg)
![HTML5](https://img.shields.io/badge/Frontend-Vanilla_JS-f06529.svg)
![Tailwind](https://img.shields.io/badge/Style-Tailwind_CSS-38bdf8.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A decoupled, full-stack clinical heuristic assessment tool designed to evaluate the risk of 14 specific micronutrient and mineral deficiencies based on dietary, lifestyle, and systemic clinical inputs. 

Built for academic and research purposes, this project utilizes a strict point-based algorithm with clinical threshold gating to separate optimal health from moderate/high-risk deficiencies.

---

## 📑 Table of Contents
- [Architecture](#-architecture)
- [Key Features](#-key-features)
- [Prerequisites](#-prerequisites)
- [Installation & Setup (GitHub Codespaces)](#-installation--setup-github-codespaces)
- [API Reference](#-api-reference)
- [Clinical Methodology](#-clinical-methodology)

---

## 🏗️ Architecture

This project strictly adheres to a decoupled **Client-Server Architecture**, designed to run seamlessly in GitHub Codespaces or local development environments.
```text
┌───────────────────────┐          HTTP POST JSON           ┌───────────────────────┐
│                       │ ─────────────────────────────────▶│                       │
│    Frontend Client    │                                   │    Python REST API    │
│   (HTML / Vanilla JS) │                                   │   (FastAPI Engine)    │
│       Port 8080       │ ◀─────────────────────────────────│       Port 3000       │
│                       │    Returns Diagnostic Report      │                       │
└───────────────────────┘                                   └───────────────────────┘
```

* **The Backend (Port 3000):** A high-performance Python FastAPI server. It houses the proprietary Knowledge Base and scoring logic. It remains completely headless and handles all heavy computation.
* **The Frontend (Port 8080):** A lightweight, dependency-free HTML/JS client. It renders the UI, collects user inputs, and dynamically routes API calls to the backend.

---

## ✨ Key Features
* **14 Nutrient Tracking:** Evaluates Vitamin D, B12, Folic Acid (B9), Vitamin A, Riboflavin (B2), Vitamin C, Thiamine (B1), B6, Niacin (B3), Vitamin E, Iron, Zinc, Calcium, and Iodine.
* **Clinical Threshold Gates:** Filters out sub-clinical "noise" (Scores 0-2) and only alerts on **Moderate** (Scores 3-5) or **High Risk** (Scores 6+) deficiencies.
* **Tailored Medical Advice:** Returns specific, scientifically rigorous recommendations based on the exact severity tier of the flagged deficiency.
* **Codespaces Auto-Routing:** The frontend JavaScript automatically detects if it is running inside a `.github.dev` environment and routes the API calls across Codespaces' forwarded ports securely, bypassing CORS issues.

---

## 📦 Prerequisites

If running locally, ensure you have the following installed:
* Python 3.9+
* `pip` (Python package manager)

---

## 🚀 Installation & Setup (GitHub Codespaces)

Because this is a decoupled architecture, you need to run **two separate terminals** simultaneously.

### 1. Start the Backend API (Terminal 1)
Open a terminal in VS Code and install the required dependencies:
```bash
pip install fastapi uvicorn pydantic
```
Start the FastAPI server on port 3000:
```bash
python backend_api.py
```
> ⚠️ **CRITICAL FOR CODESPACES:** Go to the **Ports** tab at the bottom of VS Code. Find Port `3000`, right-click under the "Visibility" column, and change it from "Private" to **"Public"**. If you skip this step, the frontend will be blocked by network errors!

### 2. Start the Frontend Client (Terminal 2)
Leave Terminal 1 running. Open a **new, second terminal** (click the `+` icon in the terminal panel) and start a simple web server:
```bash
python -m http.server 8080
```
A popup will appear in the bottom right corner. Click **Open in Browser** to view your application.

---

## 📡 API Reference

### Evaluate Patient Intake
`POST /api/analyze`

Accepts an array of heuristic keys and returns a computed clinical diagnostic report.

**Request Body (JSON):**
```json
{
  "answers": [
    "diet_strict_vegan",
    "sun_none",
    "sym_fatigue",
    "clin_spoon_nails"
  ]
}
```

**Successful Response (200 OK):**
```json
{
  "is_optimal_health": false,
  "total_risks_identified": 2,
  "deficiencies": [
    {
      "nutrient": "Iron",
      "score": 6,
      "severity": "High Clinical Risk",
      "advice": "Clinical anemia risk detected (e.g., koilonychia). Consult a doctor for a full iron panel and consider bisglycinate/heme iron supplements."
    },
    {
      "nutrient": "Vitamin B12",
      "score": 3,
      "severity": "Moderate / Developing Risk",
      "advice": "Include more fortified plant milks or nutritional yeast. Monitor energy levels and neurological symptoms."
    }
  ]
}
```

---

## 📚 Clinical Methodology

The diagnostic engine uses a cumulative weighting system derived from established clinical markers:
* **Block 1 (Dietary Base):** +1 to +2 points (e.g., un-soaked legumes strip Zinc/Iron via phytates).
* **Block 2 (Lifestyle/Environment):** +1 to +3 points (e.g., lack of sun blocking Vitamin D synthesis, which in turn blocks Calcium absorption).
* **Block 3 (Systemic Symptoms):** +1 point per symptom.
* **Block 4 (Clinical Red Flags):** +3 points (Severe physiological manifestations like goiters, scurvy-like bruising, or koilonychia).

---
*Disclaimer: This tool is built for academic demonstration purposes and does not replace professional medical diagnosis.*
```


