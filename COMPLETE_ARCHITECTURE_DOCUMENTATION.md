# LoanVerse AI — Complete Architecture Documentation
### Final Implementation · Tata Capital BFSI Challenge II · February 2026

---

## 1. Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     LOANVERSE AI SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐     ┌──────────────────────────────────┐ │
│  │  STREAMLIT   │◄────│   MASTER AGENT  (Maya)           │ │
│  │  FRONTEND    │     │   Orchestrator — conversation    │ │
│  │  (app.py)    │     │   manager, state machine, router │ │
│  └──────────────┘     └──────────────┬───────────────────┘ │
│                                       │                     │
│                        ┌─────────────┼─────────────┐       │
│                        │             │             │       │
│              ┌─────────▼──┐ ┌────────▼──┐ ┌───────▼──┐  │
│              │Sales Agent │ │Verif. Agt │ │Undwrting │  │
│              │sales.py    │ │verif.py   │ │underwr…  │  │
│              │- Purpose   │ │- KYC      │ │- Bureau  │  │
│              │- Goldilocks│ │- CRM      │ │- DTI     │  │
│              │- Counter-  │ │- Phone    │ │- 4-Rule  │  │
│              │  offer     │ │  validate │ │  engine  │  │
│              └────────────┘ └───────────┘ └──────────┘  │
│                                                             │
│              ┌──────────────────────────────────────────┐  │
│              │ Sanction Letter Generator                 │  │
│              │ assets/sanction_generator.py              │  │
│              │ - 2-page bank-grade PDF                   │  │
│              │ - 15 T&Cs + 7 RBI disclosures             │  │
│              └──────────────────────────────────────────┘  │
│                                                             │
│  Backend: customers.json · logic.py · Gemini Flash 2.0     │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
loanverse-ai/
├── app.py                        # Streamlit UI + conversation router
├── logic.py                      # Business logic (EMI, DTI, eligibility)
├── conversation_templates.py     # All of Maya's message templates
├── agents/
│   ├── __init__.py               # Clean export of all 4 agents
│   ├── master.py                 # MasterAgent (orchestrator / Maya)
│   ├── sales.py                  # SalesAgent (negotiation, options)
│   ├── verification.py           # VerificationAgent (KYC, CRM)
│   └── underwriting.py           # UnderwritingAgent (credit bureau, DTI)
├── assets/
│   ├── sanction_generator.py     # PDF sanction letter generator
│   ├── avatars.py                # Avatar / image helpers
│   └── style.css                 # Dark / light theme UI
├── data/
│   └── customers.json            # 10 synthetic customer personas
├── requirements.txt
├── .env.example
└── README.md
```

---

## 2. Multi-Agent System

### Agent Hierarchy

```
                ┌──────────────────────┐
                │    MasterAgent       │
                │    (Maya)            │  ← Orchestrates all phases
                │  agents/master.py    │  ← Maintains session state
                └──────────┬───────────┘  ← Routes to workers
                           │
          ┌────────────────┼───────────────────┐
          │                │                   │
  ┌───────▼──────┐ ┌───────▼──────┐ ┌──────────▼───────┐
  │ SalesAgent   │ │Verification  │ │ Underwriting      │
  │ sales.py     │ │ Agent        │ │ Agent             │
  │              │ │ verif.py     │ │ underwriting.py   │
  │extract_      │ │validate_     │ │fetch_credit_score │
  │ purpose()    │ │ phone()      │ │evaluate()         │
  │extract_      │ │lookup_crm()  │ │get_eligibility_   │
  │ amount()     │ │perform_kyc() │ │ summary()         │
  │goldilocks_   │ │format_       │ │                   │
  │ options()    │ │ profile()    │ │                   │
  │counter_      │ │              │ │                   │
  │ offer()      │ │              │ │                   │
  └──────────────┘ └──────────────┘ └───────────────────┘
```

### Clean Import Interface

```python
# Single import for all agents
from agents import MasterAgent, SalesAgent, VerificationAgent, UnderwritingAgent
```

---

## 3. 7-Phase Conversation Flow

```
PHASE 1: WARM OPENING
   Maya: "Hello! I'm Maya…"
   ↓
PHASE 2: PURPOSE DISCOVERY
   "What's this loan for?"  →  SalesAgent.extract_purpose()
   ↓
PHASE 3: VERIFICATION
   Phone → VerificationAgent.validate_phone()
        → VerificationAgent.lookup_crm()
        → UnderwritingAgent.fetch_credit_score()
        → VerificationAgent.format_profile()
   ↓
PHASE 4: NEEDS ANALYSIS
   Amount → SalesAgent.extract_amount()
          → UnderwritingAgent.evaluate()
   ├── INSTANT APPROVE (≤ limit)         → PHASE 5
   ├── CONDITIONAL (≤ 2×limit)
   │   → st.file_uploader() appears
   │   → Salary slip uploaded
   │   → UnderwritingAgent.evaluate(monthly_salary=…)
   │   ├── DTI ≤ 50% → APPROVE → PHASE 5
   │   └── DTI > 50% → REJECT → SalesAgent.counter_offer()
   └── REJECT (score < 700 OR > 2×limit)
       → SalesAgent.credit_improvement_plan()
       → SalesAgent.counter_offer()
   ↓
PHASE 5: OPTIONS PRESENTATION
   SalesAgent.generate_goldilocks_options()
   → 3 Plans: Aggressive (24 mo) / Balanced (36 mo) / Relaxed (60 mo)
   ↓
PHASE 6: CONFIRMATION
   MasterAgent synthesises full loan summary
   User says "Yes" → proceed
   ↓
PHASE 7: DOCUMENTATION
   sanction_generator.generate_sanction_letter()
   → 2-page PDF: 15 T&Cs + 7 RBI disclosures
   → Download button / auto-open from Downloads folder
```

---

## 4. Underwriting 4-Rule Engine

```
┌─────────────────────────────────────────────────────────┐
│  Rule 1:  Score < 700?                                  │
│           YES → HARD REJECT                             │
│           NO  → continue                               │
├─────────────────────────────────────────────────────────┤
│  Rule 2:  Amount ≤ Pre-Approved Limit?                  │
│           YES → INSTANT APPROVE (+ safety DTI check)   │
│           NO  → continue                               │
├─────────────────────────────────────────────────────────┤
│  Rule 3:  Amount ≤ 2× Pre-Approved Limit?               │
│           YES → CONDITIONAL (upload salary slip)        │
│                 DTI ≤ 50%? → APPROVE : REJECT           │
│           NO  → continue                               │
├─────────────────────────────────────────────────────────┤
│  Rule 4:  Amount > 2× Limit                             │
│           → HARD REJECT + counter-offer                 │
└─────────────────────────────────────────────────────────┘
```

### DTI Calculation

```python
DTI% = ((proposed_emi + current_emis) / monthly_salary) × 100

Thresholds:
  < 30%  → Excellent — highly comfortable
  30–40% → Very Good — safe
  40–50% → Acceptable — RBI compliant, approve with note
  ≥ 50%  → REJECT — violates RBI guideline
```

---

## 5. Complete User Journeys

### Journey A — Happy Path (Instant Approve ~5 min)

**Persona:** Ravi Kumar · Score 780/900 · Limit ₹5L · Requests ₹5L

```
PHASE 1 → Greeted by Maya
PHASE 2 → Purpose: wedding (SalesAgent.extract_purpose)
PHASE 3 → Phone 9876543210 → CRM found → Score 780/900 displayed
PHASE 4 → Amount ₹5L ≤ limit ₹5L → INSTANT APPROVE
PHASE 5 → 3 options shown (24/36/60 months) → User picks 36 months
PHASE 6 → Full summary displayed → User confirms "Yes"
PHASE 7 → Sanction Letter PDF generated → Downloaded
```

### Journey B — Conditional Path (~6 min)

**Persona:** Priya Sharma · Score 742/900 · Limit ₹6L · Requests ₹7L

```
PHASE 4 → Amount ₹7L > limit ₹6L but ≤ 2×limit ₹12L → CONDITIONAL
         → "📎 Upload Salary Slip" widget appears
         → User uploads PDF
         → UnderwritingAgent.evaluate(monthly_salary=45000)
         → DTI = 68.4% > 50% → REJECT
         → SalesAgent.counter_offer() → "Take ₹5L instantly?"
         → User agrees → INSTANT APPROVE → Phases 5–7
```

### Journey C — Rejection Path (~3.5 min)

**Persona:** Amit Verma · Score 650/900 · Requests ₹5L

```
PHASE 4 → Rule 1: Score 650 < 700 → HARD REJECT
         → SalesAgent.credit_improvement_plan() displayed
         → 3–6 month roadmap to reach 700
         → Alternatives: gold loan, secured loan, employer advance
         → Human handoff offered
```

---

## 6. Data Objects

### Customer Profile (from VerificationAgent.lookup_crm)
```python
{
  'phone': '9876543210', 'name': 'Ravi Kumar', 'age': 32,
  'city': 'Bangalore', 'address': '…', 'pan': 'ABCDE1234F',
  'score': 780, 'limit': 500000, 'salary': 75000,
  'current_emis': 0, 'employment': 'Software Engineer, TCS'
}
```

### Credit Bureau Response (from UnderwritingAgent.fetch_credit_score)
```python
{
  'found': True, 'score': 780, 'max_score': 900,
  'bureau': 'CIBIL Mock', 'ref': 'CIBIL/20260224/3210'
}
```

### Eligibility Result (from UnderwritingAgent.evaluate)
```python
# Instant Approve
{ 'status': 'APPROVE', 'type': 'INSTANT', 'approved_amount': 500000,
  'emi': 16297, 'interest_rate': 11.5, 'tenure_months': 36 }

# Conditional
{ 'status': 'CONDITIONAL', 'needs': 'SALARY_SLIP', 'limit': 600000,
  'max_eligible': 1200000 }

# Reject
{ 'status': 'REJECT', 'reason': '…', 'max_eligible': 0 }
```

### Goldilocks Options (from SalesAgent.generate_goldilocks_options)
```python
{
  'aggressive': { 'tenure': 24, 'emi': 23500, … },  # 15% choose
  'balanced':   { 'tenure': 36, 'emi': 16250, … },  # 68% choose ⭐
  'relaxed':    { 'tenure': 60, 'emi': 10750, … },  # 17% choose
}
```

---

## 7. Challenge Requirements — 100% Compliance

| # | Requirement | Implementation | File | ✓ |
|---|-------------|----------------|------|---|
| 1 | Master Agent orchestrates | `MasterAgent` class, 7-phase state machine | `agents/master.py` | ✅ |
| 2 | Sales Worker Agent | `SalesAgent` — purpose, amount, Goldilocks, counter-offer | `agents/sales.py` | ✅ |
| 3 | Verification Worker Agent | `VerificationAgent` — phone, CRM, KYC, profile | `agents/verification.py` | ✅ |
| 4 | Underwriting Worker Agent | `UnderwritingAgent` — bureau API, DTI, 4-rule engine | `agents/underwriting.py` | ✅ |
| 5 | Credit score out of 900 | All UI shows "X / 900 (CIBIL)" | app.py, sanction PDF | ✅ |
| 6 | Instant approve ≤ limit | Rule 2 + safety DTI check | `logic.check_eligibility` | ✅ |
| 7 | Conditional ≤ 2× limit | Rule 3 + `st.file_uploader()` | `app.py` Phase 4 | ✅ |
| 8 | Salary slip upload | `st.file_uploader` + DTI re-check | `app.py` | ✅ |
| 9 | Reject > 2× limit | Rule 4 + counter-offer | `logic.check_eligibility` | ✅ |
| 10 | Reject score < 700 | Rule 1 | `logic.check_eligibility` | ✅ |
| 11 | 10 synthetic customers | Diverse profiles across cities | `data/customers.json` | ✅ |
| 12 | Mock credit bureau API | `fetch_credit_score()` returns score/900 + ref | `agents/underwriting.py` | ✅ |
| 13 | Sanction letter PDF | 2-page bank-grade PDF, 15 T&Cs, 7 RBI disclosures | `assets/sanction_generator.py` | ✅ |
| 14 | Human-like conversation | 7-phase consultative flow, purpose-driven tone | All agents | ✅ |
| 15 | Master coordinates workers | `route_to_agent()`, `build_agent_workflow_trace()` | `agents/master.py` | ✅ |

**15 / 15 requirements met ✅**

---

## 8. Key Differentiators

| Feature | Most Teams | LoanVerse AI |
|---------|-----------|--------------|
| Agent architecture | One file doing everything | 4 formal Worker Agent classes |
| Credit score display | "780" | "780 / 900 (CIBIL)" |
| Conditional path | Reject when over limit | Salary slip upload + DTI check |
| Sanction letter | Text message | 2-page bank-grade PDF |
| Rejection handling | "No" | Credit plan + alternatives + human handoff |
| EMI options | One option | 3 Goldilocks choices (behavioural economics) |
| DTI | Ignored | Includes existing loans, 50% RBI gate |

---

*Tata Capital Techathon 2026 · LoanVerse AI Team*
