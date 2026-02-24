"""
LoanVerse AI - Negotiator Agent
================================
World-class negotiation specialist. Intercepts customer push-back on
rate, amount, or EMI/tenure and responds with tiered, psychologically-
calibrated counter-arguments.

Escalation ladder:
  Attempt 0 → Tier 1: Educate & Empathise
  Attempt 1 → Tier 2: Creative Trade-off
  Attempt 2 → Tier 3: Final Sweetener
  Attempt 3+→ Human Executive Handoff

Author: LoanVerse Team
Purpose: Tata Capital Techathon 2026
"""

import re
from typing import Optional


class NegotiatorAgent:
    """
    The Negotiator — LoanVerse's most persuasive specialist.

    Triggered whenever a customer challenges:
      • The offered interest rate
      • The approved loan amount (wants more than the limit)
      • The EMI or tenure terms

    Uses three escalating tiers of argument. On the fourth pushback,
    hands the customer off gracefully to a senior human loan officer.
    """

    # ── Intent detection ─────────────────────────────────────────────────────

    _RATE_SIGNALS = [
        'rate', 'interest', 'percent',
        'too high', 'expensive', 'costly', 'reduce rate', 'lower rate',
        'better rate', 'discount', 'cheap', 'less interest', 'better deal',
        'other bank', 'competitor', 'market rate', 'rbi rate',
    ]

    _AMOUNT_SIGNALS = [
        'more money', 'need more', 'want more', 'full amount', 'complete amount',
        'not enough', 'increase', 'raise', 'higher amount', 'can you give more',
        'not fair', 'why limit', 'why 6', 'why so less', 'too low', 'maximum',
        'max out', 'stretch', 'full 8', 'full 7', 'full 10', 'entire amount',
        'whole amount', 'reconsider', 'reviewed again',
    ]

    _EMI_SIGNALS = [
        'emi', 'monthly', 'installment', 'instalment', 'payment', 'per month',
        'afford', 'burden', 'too much', 'reduce emi', 'lower emi', 'small emi',
        'less emi', 'stretch tenure', 'more months', 'longer period', 'extend',
        'flexible', 'can i pay less', 'smaller payment',
    ]

    @staticmethod
    def detect_negotiation_intent(user_input: str) -> Optional[str]:
        """
        Returns 'RATE', 'AMOUNT', 'EMI', or None.

        Detection avoids false positives on pure acceptance messages
        ('yes', 'ok', 'confirm') that happen to contain partial matches.
        """
        msg = user_input.lower().strip()

        # Skip pure acceptances — not a negotiation
        pure_accept = {'yes', 'ok', 'okay', 'sure', 'confirm', 'proceed',
                       'go ahead', 'yep', 'yeah', 'fine', 'done', 'agreed',
                       'accept', 'sounds good', 'alright', 'great'}
        if msg in pure_accept or len(msg) <= 3:
            return None

        # Check has a negotiation flavour (complaint/ask phrasing)
        challenge_words = [
            'why', 'how', 'can', 'could', 'please', 'need', 'want',
            'reduce', 'lower', 'not', "don't", 'too', 'is it', 'what',
            'better', 'less', 'more', 'high', 'much',
        ]
        has_challenge = any(w in msg for w in challenge_words)

        if not has_challenge:
            return None

        # Order matters — EMI before amount to catch "EMI is too much"
        if any(sig in msg for sig in NegotiatorAgent._EMI_SIGNALS
               if sig not in ('more', 'maximum', 'raise')):
            return 'EMI'
        if any(sig in msg for sig in NegotiatorAgent._RATE_SIGNALS):
            return 'RATE'
        if any(sig in msg for sig in NegotiatorAgent._AMOUNT_SIGNALS):
            return 'AMOUNT'
        return None

    # ── Main dispatcher ───────────────────────────────────────────────────────

    @staticmethod
    def negotiate(intent: str, context: dict, attempt: int) -> str:
        """
        Return the appropriate negotiation response for this intent and attempt.

        Args:
            intent  : 'RATE', 'AMOUNT', or 'EMI'
            context : Customer and loan data dict (see module docstring)
            attempt : 0-based attempt count (0 = first pushback)

        Returns:
            str: Full markdown-ready response to add to chat
        """
        if intent == 'RATE':
            return NegotiatorAgent._tier_rate(context, attempt)
        elif intent == 'AMOUNT':
            return NegotiatorAgent._tier_amount(context, attempt)
        else:
            return NegotiatorAgent._tier_emi(context, attempt)

    # ── Rate negotiation tiers ────────────────────────────────────────────────

    @staticmethod
    def _tier_rate(ctx: dict, attempt: int) -> str:
        name   = ctx.get('customer_name', 'there').split()[0]
        rate   = ctx.get('rate') or 13.5
        score  = ctx.get('credit_score', 750)
        amount = ctx.get('approved', ctx.get('requested', 0))

        if attempt == 0:
            return (
                f"I completely understand, {name} — nobody wants to pay more than they have to! "
                f"Let me be fully transparent about how your rate is set. 💡\n\n"
                f"**How your {rate}% rate is calculated:**\n"
                f"- Your CIBIL score is **{score}/900** — this determines your risk tier\n"
                f"- RBI guidelines mandate NBFCs use risk-based pricing\n"
                f"- Our rate tiers: 800+ → 10.5% | 750–799 → 11.5% | 700–749 → 13.5% | Below 700 → 15%\n\n"
                f"**Market comparison:**\n"
                f"- Major nationalized banks: 13–17% p.a. for personal loans\n"
                f"- Other NBFCs: 14–24% p.a.\n"
                f"- Gold loans: 14–18% p.a.\n\n"
                f"Your rate of **{rate}%** is already at the **lower end of the market** for your profile. "
                f"Plus, we've waived the processing fee (typically ₹1,499–₹5,000 elsewhere), "
                f"saving you real money upfront. 🎯\n\n"
                f"Would you like to proceed, or shall I show you the total cost comparison?"
            )
        elif attempt == 1:
            credit_improve_score = min(score + 50, 900)
            improved_rate = max(rate - 1.0, 10.5)
            return (
                f"I hear you, {name}, and I genuinely want to help you get the best deal. "
                f"Let me share two paths that could work in your favour. 🛤️\n\n"
                f"**Option A — Credit Score Improvement Plan:**\n"
                f"Your score is currently {score}. With a few targeted actions over 3–6 months:\n"
                f"- Pay all existing EMIs on time → +20–30 points\n"
                f"- Keep credit utilisation below 30% → +15–20 points\n"
                f"- Avoid new credit inquiries → +10 points\n"
                f"- Projected score: ~{credit_improve_score} → **rate drops to {improved_rate}%**\n\n"
                f"**Option B — Proceed now at {rate}%:**\n"
                f"The difference on ₹{amount:,.0f}:\n"
                f"- At {rate}%: ₹{int(amount * rate / 1200):,}/month interest component\n"
                f"- At {improved_rate}%: ₹{int(amount * improved_rate / 1200):,}/month interest component\n"
                f"- Monthly saving: ₹{int(amount * (rate - improved_rate) / 1200):,}\n\n"
                f"For most customers, the opportunity cost of **waiting 6 months** outweighs the small rate difference. "
                f"But the choice is entirely yours. Which makes more sense for your situation?"
            )
        else:  # Tier 3 – final sweetener
            return (
                f"Alright, {name} — you drive a hard bargain! 😄 Here's our absolute best offer:\n\n"
                f"**🎁 Special Rate Lock Package (Limited Time):**\n"
                f"1. **Rate locked at {rate}%** for the next **30 days** — no revision risk\n"
                f"2. **Zero processing fee** (₹0) — vs. market average of ₹3,000–₹5,000\n"
                f"3. **Complimentary rate review** eligibility after 12 on-time EMIs — "
                f"if your score improves, we'll formally reconsider a rate reduction\n"
                f"4. **Zero pre-closure penalty** — pay off early without any charges\n\n"
                f"Combined, these benefits are worth ₹5,000–₹8,000 in real savings. "
                f"This is the maximum flexibility I can offer you today, {name}. 🤝\n\n"
                f"If you'd still like to explore further options, I can connect you with "
                f"our **Senior Loan Advisor** who may have additional discretionary authority. "
                f"Would you like me to do that, or shall we proceed with this package?"
            )

    # ── Amount negotiation tiers ──────────────────────────────────────────────

    @staticmethod
    def _tier_amount(ctx: dict, attempt: int) -> str:
        name      = ctx.get('customer_name', 'there').split()[0]
        requested = ctx.get('requested', 0)
        approved  = ctx.get('approved', 0)
        salary    = ctx.get('salary', 0)
        emis      = ctx.get('current_emis', 0)
        purpose   = ctx.get('purpose', 'your needs')
        max_emi_capacity = salary * 0.5

        if attempt == 0:
            dti_at_requested = ((requested / 36) * 0.01135 + requested / 36) / salary * 100
            return (
                f"I completely relate to your need for the full amount, {name} — "
                f"₹{requested:,.0f} for {purpose} is a totally legitimate ask. "
                f"Let me show you exactly why the number is what it is. 📊\n\n"
                f"**Your Affordability Math (RBI DTI Rule):**\n"
                f"- Monthly take-home salary: **₹{salary:,}**\n"
                f"- Existing EMI commitments: **₹{emis:,}**\n"
                f"- Available EMI capacity (50% of salary): **₹{max_emi_capacity:,.0f}**\n"
                f"- After existing EMIs: **₹{max_emi_capacity - emis:,.0f}** free capacity\n\n"
                f"An EMI for ₹{requested:,.0f} at 36 months would need ~₹{int(requested/36 * 1.135):,}/month, "
                f"which pushes your DTI to **~{min(dti_at_requested, 99):.1f}%** — above the **50% RBI ceiling**.\n\n"
                f"The ₹{approved:,.0f} limit keeps you safely at or below 50%, "
                f"which actually **protects your credit score** and prevents over-leveraging. 🛡️\n\n"
                f"Shall we proceed with ₹{approved:,.0f}, or explore an alternative path?"
            )
        elif attempt == 1:
            return (
                f"I respect your position, {name}. Let me offer you two concrete paths to get closer to what you need. 🔑\n\n"
                f"**Path 1 — Salary Slip Verification:**\n"
                f"If you upload your latest 3-month salary slip, I can run an enhanced underwriting check. "
                f"If your declared salary is confirmed at or above ₹{salary:,}, "
                f"I may be able to approve up to **₹{min(requested, approved * 1.5):,.0f}** "
                f"under our Conditional Approval scheme.\n\n"
                f"**Path 2 — Co-Borrower Addition:**\n"
                f"If you add a co-borrower (spouse, parent, sibling) with their income, "
                f"the combined DTI calculation could unlock the full **₹{requested:,.0f}**. "
                f"Many of our customers use this for large loan requirements.\n\n"
                f"**Path 3 — Split into Two Products:**\n"
                f"Take ₹{approved:,.0f} as a personal loan now, and apply for the remaining "
                f"₹{requested - approved:,.0f} as a separate product (home improvement loan, "
                f"credit line) 3–4 months from now once your DTI improves.\n\n"
                f"Which of these paths sounds workable for your situation?"
            )
        else:  # Tier 3
            partial_increase = min(requested, int(approved * 1.15))
            return (
                f"Alright, {name} — here's my absolute final offer before I pass you to my senior colleague. "
                f"I've done a manual override review and this is what I can table:\n\n"
                f"**🔖 Negotiated Terms — Final Offer:**\n"
                f"- Approved amount: **₹{partial_increase:,.0f}** (vs. original ₹{approved:,.0f})\n"
                f"- Condition: Upload salary slip to confirm income ≥ ₹{salary:,}\n"
                f"- Tenure: 48 months (to keep EMI manageable)\n"
                f"- All other terms unchanged\n\n"
                f"This is ₹{partial_increase - approved:,.0f} more than the standard offer "
                f"and is the maximum I'm authorised to clear at this level. 🤝\n\n"
                f"If this still doesn't meet your requirement, I'd recommend speaking with our "
                f"**Senior Relationship Manager** who has discretionary authority for higher limits. "
                f"Shall I connect you, or would you like to accept this enhanced offer?"
            )

    # ── EMI / tenure negotiation tiers ────────────────────────────────────────

    @staticmethod
    def _tier_emi(ctx: dict, attempt: int) -> str:
        name    = ctx.get('customer_name', 'there').split()[0]
        emi     = ctx.get('emi', 0)
        tenure  = ctx.get('tenure', 36)
        amount  = ctx.get('approved', ctx.get('requested', 0))
        rate    = ctx.get('rate') or 13.5
        salary  = ctx.get('salary', 0)

        if attempt == 0:
            tenure_60_emi = int(amount * (rate/1200) / (1 - (1 + rate/1200) ** -60))
            tenure_84_emi = int(amount * (rate/1200) / (1 - (1 + rate/1200) ** -84))
            return (
                f"That's a very fair concern, {name} — monthly cash flow is everything! "
                f"Let me show you how the EMI changes with different tenures. 📅\n\n"
                f"**EMI options for ₹{amount:,.0f} at {rate}%:**\n"
                f"| Tenure | Monthly EMI | Total Interest |\n"
                f"|--------|------------|----------------|\n"
                f"| {tenure} months (current) | **₹{emi:,}** | ₹{int(emi*tenure - amount):,} |\n"
                f"| 60 months | **₹{tenure_60_emi:,}** | ₹{int(tenure_60_emi*60 - amount):,} |\n"
                f"| 84 months | **₹{tenure_84_emi:,}** | ₹{int(tenure_84_emi*84 - amount):,} |\n\n"
                f"Extending to **60 months** reduces your EMI by ₹{emi - tenure_60_emi:,}/month — "
                f"that's extra breathing room every month. 💨\n\n"
                f"You do pay slightly more total interest, but you avoid any cash flow stress. "
                f"Which tenure feels right for your budget?"
            )
        elif attempt == 1:
            tenure_60_emi = int(amount * (rate/1200) / (1 - (1 + rate/1200) ** -60))
            monthly_savings = emi - tenure_60_emi
            return (
                f"Let me dig deeper on this for you, {name}. There are two more ways to reduce the burden further. 💡\n\n"
                f"**Strategy 1 — Maximum Tenure Extension (84 months):**\n"
                f"- Monthly EMI drops to: **₹{int(amount * (rate/1200) / (1 - (1 + rate/1200) ** -84)):,}**\n"
                f"- That's your absolute lowest possible monthly commitment\n"
                f"- Pre-close any time after 6 EMIs with zero penalty\n\n"
                f"**Strategy 2 — Step-Up EMI Plan:**\n"
                f"- Start at a lower EMI now, step up by 5–10% annually as your income grows\n"
                f"- Many of our salaried customers get annual increments — this plan rides along\n\n"
                f"**Strategy 3 — Part Pre-payment:**\n"
                f"- Take the loan, invest a lump sum after 6 months to reduce outstanding principal\n"
                f"- Even a ₹50,000 pre-payment at month 6 reduces subsequent EMIs noticeably\n\n"
                f"As your salary is ₹{salary:,}/month, an EMI of ₹{tenure_60_emi:,} means "
                f"only **{int(tenure_60_emi/salary*100)}% of your take-home** — very manageable. 😊\n\n"
                f"Which strategy would you like me to calculate in detail?"
            )
        else:  # Tier 3
            tenure_84_emi = int(amount * (rate/1200) / (1 - (1 + rate/1200) ** -84))
            return (
                f"Alright {name}, I've pushed the parameters as far as our system allows. "
                f"Here's my best possible offer on the EMI front:\n\n"
                f"**🎁 Optimised EMI Package — Final Offer:**\n"
                f"- Tenure extended to **84 months** → EMI = **₹{tenure_84_emi:,}/month**\n"
                f"- **Zero processing fee** (saving ₹0–₹3,000)\n"
                f"- **Zero pre-closure penalty** — reduce loan anytime\n"
                f"- **Step-up adjustment** — request a formal EMI revision after 12 months\n\n"
                f"At ₹{tenure_84_emi:,}/month, this is {int(tenure_84_emi/salary*100)}% of your salary — "
                f"comfortably within RBI's guideline.\n\n"
                f"This is the lowest I can go through our automated system. "
                f"If you need further flexibility, our **Senior Loan Advisor** can explore "
                f"bespoke repayment structures including moratorium periods and balloon payments. "
                f"Shall I escalate to them?"
            )

    # ── Alternative Path selection ────────────────────────────────────────────

    _PATH1_SIGNALS = [
        'path 1', 'path1', 'salary slip', 'salary', 'upload', 'payslip',
        'income proof', 'slip verification', 'verify income', 'first path',
        'first option', 'option 1', 'option a',
    ]
    _PATH2_SIGNALS = [
        'path 2', 'path2', 'co-borrower', 'coborrower', 'co borrower',
        'joint', 'add someone', 'spouse', 'parent', 'sibling', 'guarantor',
        'second path', 'second option', 'option 2', 'option b',
    ]
    _PATH3_SIGNALS = [
        'path 3', 'path3', 'split', 'two products', 'separate', 'partial',
        'half now', 'proceed with', 'approved amount', 'go ahead with',
        'third path', 'third option', 'option 3', 'option c',
    ]

    @staticmethod
    def detect_path_selection(user_input: str) -> Optional[str]:
        """
        Returns 'PATH_1', 'PATH_2', 'PATH_3', or None.
        Detects when the user picks one of the 3 alternative paths offered
        in the Tier 2 AMOUNT negotiation response.
        """
        msg = user_input.lower().strip()
        if any(s in msg for s in NegotiatorAgent._PATH1_SIGNALS):
            return 'PATH_1'
        if any(s in msg for s in NegotiatorAgent._PATH2_SIGNALS):
            return 'PATH_2'
        if any(s in msg for s in NegotiatorAgent._PATH3_SIGNALS):
            return 'PATH_3'
        return None

    @staticmethod
    def handle_path_selection(path: str, context: dict):
        """
        Execute a selected alternative path.

        Returns:
            (message: str, action_code: str)
            action_code: 'SALARY_SLIP' | 'CO_BORROWER' | 'SPLIT_LOAN'
        """
        name      = context.get('customer_name', 'there').split()[0]
        requested = context.get('requested', 0)
        approved  = context.get('approved', 0)
        salary    = context.get('salary', 0)

        if path == 'PATH_1':
            msg = (
                f"Great choice, {name}! 🎉 Salary verification is the fastest route to an enhanced limit.\n\n"
                f"**Here's what happens next:**\n"
                f"- Upload your **latest 3-month salary slip** (PDF, JPG, or PNG) using the button below\n"
                f"- Our system will verify your income against our CRM record\n"
                f"- If your declared salary ≥ ₹{salary:,}, we may approve up to "
                f"**₹{min(requested, int(approved * 1.5)):,.0f}** under the Conditional scheme\n\n"
                f"Please go ahead and upload your salary slip! 📎"
            )
            return msg, 'SALARY_SLIP'

        if path == 'PATH_2':
            msg = (
                f"Excellent choice, {name}! A co-borrower significantly boosts your eligibility. 👨‍👩‍👧\n\n"
                f"**How it works:**\n"
                f"- Both your incomes are combined for DTI calculation\n"
                f"- Combined DTI = (New EMI) / (Your Salary + Co-Borrower Salary) — much more headroom\n"
                f"- This could unlock the full **₹{requested:,.0f}**\n\n"
                f"**Co-borrower eligibility:**\n"
                f"- Must be a spouse, parent, sibling, or employed adult child\n"
                f"- Needs a valid PAN and salary proof\n\n"
                f"**Next steps** — our Senior Advisor will help arrange the joint application:\n\n"
                f"👤 **Mr. Arjun Mehta** · Senior Relationship Manager\n"
                f"📞 **+91-22-6789-1234** · 📧 **arjun.mehta@loanverse.ai**\n\n"
                f"In the meantime, would you like to proceed with the pre-approved "
                f"**₹{approved:,.0f}** instantly while you arrange the co-borrower documentation? 😊"
            )
            return msg, 'CO_BORROWER'

        if path == 'PATH_3':
            msg = (
                f"Smart move, {name}! Let's get you started with what's fully approved right now. 🚀\n\n"
                f"I'll proceed with **₹{approved:,.0f}** as your personal loan — "
                f"fully approved, ready to disburse.\n\n"
                f"**For the remaining ₹{requested - approved:,.0f}:**\n"
                f"- In 3–4 months, once this loan's repayment pattern is established, your DTI profile improves\n"
                f"- You can then apply for a **Home Improvement Loan** or **Top-Up Loan** for the balance\n"
                f"- Many customers complete both disbursements within 6 months\n\n"
                f"Let me generate your EMI options for ₹{approved:,.0f} right away! 📋"
            )
            return msg, 'SPLIT_LOAN'

        return "", None

    # ── Human escalation ──────────────────────────────────────────────────────

    @staticmethod
    def escalate_to_human(customer_name: str = 'there') -> str:
        """
        Generate a graceful human handoff message with named senior contact.
        """
        first_name = customer_name.split()[0] if customer_name else 'there'
        return (
            f"Thank you for your patience, {first_name}, and I sincerely respect "
            f"how thoroughly you've evaluated this. 🙏\n\n"
            f"I've taken this negotiation as far as our automated system allows. "
            f"At this point, I'd like to connect you with our **Senior Relationship Manager** "
            f"who has **full discretionary authority** to offer:\n"
            f"- Custom interest rate structures\n"
            f"- Higher loan limits beyond standard pre-approval\n"
            f"- Flexible repayment holidays and moratorium periods\n"
            f"- Bespoke product combinations\n\n"
            f"---\n"
            f"**🏢 Your Dedicated Senior Loan Advisor:**\n\n"
            f"👤 **Mr. Arjun Mehta** · Senior Relationship Manager\n"
            f"📞 **+91-22-6789-1234** · *(Mon–Sat, 9 AM–6 PM)*\n"
            f"📧 **arjun.mehta@loanverse.ai**\n"
            f"💬 **WhatsApp:** +91-98765-01234\n\n"
            f"---\n"
            f"Please mention **Reference Code `{first_name.upper()}-ESCALATE`** "
            f"and he'll have full visibility into your application so you won't have to "
            f"repeat yourself. He typically responds within **2 business hours**.\n\n"
            f"Is there anything else I can help you with in the meantime? 😊"
        )

