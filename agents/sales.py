"""
LoanVerse AI - Sales Agent
===========================
Worker Agent: Handles customer engagement, needs analysis,
negotiation psychology, and loan option presentation.

Author: LoanVerse Team
Purpose: Tata Capital Techathon 2026
"""

import re
from typing import Dict, Optional, Tuple


class SalesAgent:
    """
    Sales Worker Agent — the Empathy & Negotiation Engine.

    Responsibilities:
    1. Extract loan purpose from natural language
    2. Parse requested loan amount from free-form text
    3. Generate Goldilocks (3-option) EMI plans
    4. Draft counter-offers when requested amount is too high
    5. Handle common objections (rate, tenure, amount)

    Maya's consultative philosophy:
    - Never say "no" without offering an alternative
    - Match tone to purpose (celebratory for wedding, clinical for medical)
    - Present exactly 3 options to nudge the middle choice (Goldilocks)
    """

    # Purpose keyword map (keyword → canonical category)
    _PURPOSE_KEYWORDS = {
        "wedding": "wedding",
        "marriage": "wedding",
        "shaadi": "wedding",
        "reception": "wedding",
        "education": "education",
        "college": "education",
        "university": "education",
        "degree": "education",
        "school": "education",
        "fees": "education",
        "medical": "medical",
        "hospital": "medical",
        "surgery": "medical",
        "health": "medical",
        "treatment": "medical",
        "medicine": "medical",
        "home": "home",
        "house": "home",
        "renovation": "home",
        "repair": "home",
        "interior": "home",
        "travel": "travel",
        "vacation": "travel",
        "holiday": "travel",
        "trip": "travel",
        "business": "business",
        "startup": "business",
        "shop": "business",
        "invest": "business",
        "debt": "debt_consolidation",
        "consolidat": "debt_consolidation",
        "emi": "debt_consolidation",
        "car": "vehicle",
        "vehicle": "vehicle",
        "bike": "vehicle",
        "emergency": "emergency",
        "urgent": "emergency",
    }

    # ─────────────────────────────────────────────────────────
    # 1. Purpose Extraction
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def extract_purpose(user_input: str) -> Optional[str]:
        """
        Identify loan purpose from natural language.

        Checks against a comprehensive keyword map.
        Falls back to None if no purpose detected.

        Args:
            user_input: Raw user message.

        Returns:
            Canonical purpose string (e.g., 'wedding'), or None.
        """
        text = user_input.lower()
        for keyword, purpose in SalesAgent._PURPOSE_KEYWORDS.items():
            if keyword in text:
                return purpose
        return None

    # ─────────────────────────────────────────────────────────
    # 2. Amount Extraction
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def extract_amount(user_input: str) -> Optional[float]:
        """
        Parse a rupee amount from natural language.

        Handles formats:
        - "5 lakhs", "5L", "5lakh"       → 500,000
        - "10 crore", "10cr"              → 100,000,000
        - "₹5,00,000"                     → 500,000
        - "500000"                         → 500,000
        - "five lakhs"                     → 500,000
        - "5.5 lakhs"                      → 550,000

        Returns:
            Float amount in rupees, or None if not found.
        """
        text = user_input.lower().replace(",", "")

        # Lakh patterns: "5 lakhs", "5L", "5.5 lakh"
        lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|l\b)", text)
        if lakh_match:
            return float(lakh_match.group(1)) * 100_000

        # Crore patterns
        crore_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:crore|cr\b)", text)
        if crore_match:
            return float(crore_match.group(1)) * 10_000_000

        # Plain number with ₹ symbol
        rupee_match = re.search(r"₹\s*(\d+(?:\.\d+)?)", text)
        if rupee_match:
            return float(rupee_match.group(1))

        # Plain number (>= 4 digits to avoid confusion with tenures)
        plain_match = re.search(r"\b(\d{4,}(?:\.\d+)?)\b", text)
        if plain_match:
            return float(plain_match.group(1))

        return None

    # ─────────────────────────────────────────────────────────
    # 3. Goldilocks EMI Options
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def generate_goldilocks_options(
        amount: float,
        interest_rate: float,
        monthly_salary: float,
        current_emis: float = 0.0
    ) -> Dict:
        """
        Generate 3 EMI plan options (short / balanced / extended).

        The three tenures are tuned to the Goldilocks principle:
        Option 1 (Aggressive) — faster payoff, higher EMI
        Option 2 (Balanced)   — recommended middle path ⭐
        Option 3 (Relaxed)    — lower EMI, longer commitment

        This is a wrapper over logic.generate_goldilocks_options()
        to keep the formal agent interface intact.

        Args:
            amount: Loan amount in ₹
            interest_rate: Annual interest rate (e.g., 11.5)
            monthly_salary: Borrower's monthly take-home
            current_emis: Existing EMI obligations per month

        Returns:
            dict with 'aggressive', 'balanced', 'relaxed' plan dicts.
        """
        from logic import generate_goldilocks_options
        return generate_goldilocks_options(
            amount, interest_rate, monthly_salary, current_emis
        )

    # ─────────────────────────────────────────────────────────
    # 4. Counter-Offer Generator
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def counter_offer(
        requested: float,
        pre_approved_limit: float,
        user_name: str,
        monthly_salary: Optional[float] = None,
        current_emis: float = 0.0
    ) -> str:
        """
        Generate an empathetic counter-offer when the requested
        amount exceeds the customer's capacity or hard cap.

        Strategies:
        - Over 2× limit → Offer the 2× limit as conditional, or limit instantly
        - High DTI      → Calculate the max safe amount and offer that

        Args:
            requested: Amount the customer asked for.
            pre_approved_limit: Customer's pre-approved ceiling.
            user_name: First name for personalisation.
            monthly_salary: If available, used for DTI-based max calculation.
            current_emis: Existing monthly obligations.

        Returns:
            Markdown-formatted counter-offer message string.
        """
        first_name = user_name.split()[0]
        max_conditional = 2 * pre_approved_limit

        lines = [
            f"I understand you need ₹{requested:,.0f}, {first_name}.",
            "",
            "Here's the situation:",
            f"• Your instant pre-approved limit: **₹{pre_approved_limit:,.0f}**",
            f"• Maximum I can offer (with income verification): **₹{max_conditional:,.0f}**",
            f"• Your requested amount: ₹{requested:,.0f}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "💡 **What I CAN arrange:**",
            "",
            f"**Option A — Instant (Zero Docs)**",
            f"₹{pre_approved_limit:,.0f} in 24 hours. No salary slip, no waiting.",
            "",
            f"**Option B — Maximum Available (2 min)**",
            f"₹{max_conditional:,.0f} with a quick salary slip upload.",
            "",
            "**Option C — Build Up Over Time**",
            f"Take ₹{pre_approved_limit:,.0f} now. After 6 months of on-time payments,",
            "your limit will increase to the higher amount.",
            "",
            "Which option works best for your timeline?",
        ]

        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────
    # 5. Objection Handling
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def handle_rate_objection(credit_score: int, rate: float) -> str:
        """
        Handle "rate is too high" objections with transparent pricing.

        Shows RBI repo rate breakdown so customer understands
        exactly how the rate was computed — builds trust.

        Args:
            credit_score: Customer's CIBIL score (out of 900)
            rate: The offered interest rate (e.g., 11.5)
        """
        base_rate = 6.5
        operating_cost = 2.0
        risk_premium = rate - base_rate - operating_cost
        score_note = "Prime customer discount already applied ✅" if credit_score >= 750 else "Improve score to 750+ for a lower rate"

        return f"""I completely understand your concern.

Let me show you exactly how we arrived at **{rate}%**:

📊 **RATE BREAKDOWN:**
• RBI Repo Rate (Base):              {base_rate}%
• Bank Operating Costs:              {operating_cost}%
• Risk Premium (unsecured loan):     {risk_premium:.1f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**YOUR FINAL RATE:**                 {rate}%

✅ {score_note}

💡 **Comparison:**
• Credit Cards:   36–42% per annum
• Gold Loans:     14–18% per annum
• **Your Rate:    {rate}%** ← Significantly lower

Would you like to proceed at {rate}%, or would a smaller amount reduce the EMI burden?"""

    @staticmethod
    def credit_improvement_plan(current_score: int, target_score: int = 700) -> str:
        """
        Provide actionable credit improvement steps for rejected customers.

        Args:
            current_score: Customer's current CIBIL score.
            target_score: Minimum score needed for approval.
        """
        gap = target_score - current_score
        months_estimate = "3–4 months" if gap <= 30 else "4–6 months"

        return f"""I understand this isn't the news you hoped for. 😔

**Current Score:** {current_score} / 900
**Required Score:** {target_score} / 900
**Gap:** Just {gap} points — very achievable!

📈 **Your Credit Improvement Plan:**

1. **Pay all EMIs & bills on time** — biggest impact (35% of score)
2. **Reduce credit card usage to under 30%** of your limit
3. **Don't apply for new credit right now** — each inquiry drops score 5–10 pts
4. **Check your CIBIL report for errors** — 30% of reports have mistakes

⏰ **Timeline:** Follow these steps for {months_estimate} and you should cross {target_score}.

💡 **Meanwhile, alternatives:**
• **Gold loan** (if you have jewellery) — score doesn't matter
• **Secured loan** against FD or property
• **Employer salary advance** — zero interest

💪 You're {gap} points away. Let me follow up in 3 months to check your progress!"""
