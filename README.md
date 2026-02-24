# 🏦 LoanVerse AI — Conversational Loan Assistant

> An AI-powered, RBI-compliant personal loan assistant built for the **EY Techathon 2026**.

LoanVerse AI presents **Maya** — a consultative banking AI that guides customers through a full loan application in natural conversation. Maya performs live underwriting, enforces DTI compliance, generates Goldilocks EMI options, and produces a bank-grade sanction letter PDF — all in a single chat session.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗣️ **7-Phase Conversational Flow** | Warm opening → Purpose discovery → Verification → Needs analysis → Options → Confirmation → Sanction |
| 🧮 **Live Underwriting Engine** | Credit score checks, DTI ratio analysis, risk-based interest pricing |
| 📊 **Goldilocks EMI Options** | 3 tenure-based options using behavioural finance to guide choice |
| 📄 **RBI-Compliant PDF Sanction Letter** | 15 T&C clauses, 7 mandatory disclosures, QR code verification |
| 🔒 **DPDP Consent Framework** | Explicit consent before any data processing |
| 🔎 **E-KYC Simulation** | Aadhaar + PAN verification layer |
| 🎨 **Glassmorphism UI** | Dark/light mode, animated chat bubbles |

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **AI / NLU**: Google Gemini API
- **PDF Generation**: [ReportLab](https://www.reportlab.com/) with QR code support
- **Charts**: Plotly
- **Data**: Mock customer JSON database

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/loanverse-ai.git
cd loanverse-ai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Copy the example environment file and add your Google Gemini API key:

```bash
cp .env.example .env
```

Edit `.env`:
```
GEMINI_API_KEY=your_actual_key_here
```

### 5. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📁 Project Structure

```
loanverse-ai/
├── app.py                        # Main Streamlit application
├── logic.py                      # Underwriting engine & financial calculations
├── conversation_templates.py     # Maya's dialogue scripts
├── agents/
│   ├── __init__.py               # Clean export of all 4 agents
│   ├── master.py                 # Master Agent (Maya) — state machine & intent routing
│   ├── sales.py                  # Sales Agent — Goldilocks options, objection handling
│   ├── verification.py           # Verification Agent — phone validation, KYC, CRM lookup
│   └── underwriting.py           # Underwriting Agent — credit bureau API, DTI, 4-rule engine
├── assets/
│   ├── sanction_generator.py     # RBI-compliant PDF generator
│   ├── avatars.py                # Chat avatar assets
│   ├── bliss_mode.css            # Dark mode CSS
│   ├── light_mode.css            # Light mode CSS
│   └── style.css                 # Base styles
├── data/
│   └── customers.json            # Mock customer database (10 personas)
├── COMPLETE_ARCHITECTURE_DOCUMENTATION.md
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📋 Requirements

See `requirements.txt`. Key dependencies:
- `streamlit>=1.31.0`
- `google-generativeai`
- `reportlab>=4.0`
- `qrcode`
- `pillow`
- `plotly`

---

## 📜 Compliance

LoanVerse AI is designed to mirror real NBFC standards:
- **RBI Fair Practice Code** adherence
- **DPDP Act** consent framework
- **Cooling-off period** disclosure (2-day cancellation)
- **Transparent APR** including all charges
- **Grievance Redressal** mechanism in all sanction letters

---

## 👥 Team

Built by **Team AIVORIA** for the **EY Techathon 2026**.
