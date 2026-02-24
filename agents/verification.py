"""
LoanVerse AI - Verification Agent
==================================
Worker Agent: Handles KYC validation, CRM lookups, and phone
verification. Acts as the gatekeeper before any financial
decisions are made.

Author: LoanVerse Team
Purpose: Tata Capital Techathon 2026
"""

import re
from typing import Dict, Optional


class VerificationAgent:
    """
    Verification Worker Agent — the Identity & KYC Gatekeeper.

    Responsibilities:
    1. Validate and normalize Indian 10-digit phone numbers
    2. Look up customer profile from Mock CRM (customers.json)
    3. Perform Mock E-KYC verification
    4. Format customer profile for Maya to present to the user

    In production, each method would call external APIs:
    - UIDAI (Aadhaar verification)
    - NSDL/UTI (PAN verification)
    - Internal CRM/CBS (Core Banking System)
    """

    # ─────────────────────────────────────────────────────────
    # 1. Phone Validation
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def validate_phone(raw_input: str) -> Optional[str]:
        """
        Validate and normalize an Indian mobile number.

        Accepts formats:
        - "9876543210"
        - "+91 9876543210"
        - "+919876543210"
        - "09876543210"
        - "98765 43210"
        - "9876-543-210"

        Returns:
            10-digit normalized phone string, or None if invalid.
        """
        if not raw_input:
            return None

        # Strip all spaces, dashes, dots, parentheses
        digits = re.sub(r"[\s\-\.\(\)]", "", raw_input)

        # Remove country code prefixes
        if digits.startswith("+91"):
            digits = digits[3:]
        elif digits.startswith("91") and len(digits) == 12:
            digits = digits[2:]
        elif digits.startswith("0") and len(digits) == 11:
            digits = digits[1:]

        # Must be 10 digits, starting with 6–9 (Indian mobile range)
        if re.fullmatch(r"[6-9]\d{9}", digits):
            return digits

        return None

    # ─────────────────────────────────────────────────────────
    # 2. CRM Lookup
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def lookup_crm(phone: str) -> Optional[Dict]:
        """
        Query Mock CRM (customers.json) for customer profile.

        In production: calls internal Core Banking System REST API.
        GET /api/v1/customers/phone/{phone}

        Args:
            phone: Normalized 10-digit phone number.

        Returns:
            Customer dict with profile data, or None if not found.

        Example Return:
        {
            'phone': '9876543210',
            'name': 'Ravi Kumar',
            'age': 32,
            'city': 'Bangalore',
            'address': '123 MG Road, Bangalore, Karnataka 560001',
            'pan': 'ABCDE1234F',
            'score': 780,
            'limit': 500000,
            'salary': 75000,
            'current_emis': 0,
            'employment': 'Software Engineer, 4 years at TCS',
        }
        """
        from logic import get_user
        return get_user(phone)

    # ─────────────────────────────────────────────────────────
    # 3. E-KYC (Mock)
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def perform_kyc(phone: str) -> Dict:
        """
        Perform Mock E-KYC verification against UIDAI + NSDL APIs.

        In production:
        - UIDAI Aadhaar OTP verification
        - NSDL PAN verification
        - CKYC registry cross-check

        For demo: reads from Mock CRM and returns KYC status.

        Returns:
            dict with kyc_status, is_verified, documents.
        """
        from logic import get_user, verify_kyc as logic_verify_kyc
        user = get_user(phone)
        if not user:
            return {
                "kyc_status": "NOT_FOUND",
                "is_verified": False,
                "message": "Customer not found in CRM."
            }

        kyc_result = logic_verify_kyc(phone)
        return {
            "kyc_status": "COMPLETE",
            "is_verified": True,
            "pan": user.get("pan", "N/A"),
            "name": user.get("name", "N/A"),
            "raw": kyc_result
        }

    # ─────────────────────────────────────────────────────────
    # 4. Profile Formatter (for Master Agent)
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def format_profile(user: Dict, credit_score: int) -> str:
        """
        Format customer profile into a structured summary string
        for the Master Agent to present to the user.

        Args:
            user: Customer dict from lookup_crm()
            credit_score: Score fetched by UnderwritingAgent (out of 900)

        Returns:
            Markdown-formatted profile summary string.
        """
        from logic import get_risk_based_rate

        score = user.get("score", credit_score)
        rate = get_risk_based_rate(score)

        # Credit score rating label
        if score >= 750:
            rating = "Excellent ⭐"
            score_note = "Top 25% in India"
        elif score >= 700:
            rating = "Good 👍"
            score_note = "Qualifies for most products"
        else:
            rating = "Fair ⚠️"
            score_note = "Below our minimum threshold"

        existing = user.get("current_emis", 0)
        loan_status = (
            f"₹{existing:,}/month existing EMIs"
            if existing > 0
            else "No existing loans"
        )

        return f"""━━━━━━━━━━━━━━━━━━━━━
📊 **YOUR FINANCIAL PROFILE**
━━━━━━━━━━━━━━━━━━━━━

💳 **Credit Score:** {score} / 900 (CIBIL) — {rating}
   {score_note}

💰 **Pre-Approved Limit:** ₹{user.get('limit', 0):,}
   (Instant approval for amounts up to this)

📈 **Your Interest Rate:** {rate}% per annum
   (Risk-based pricing for your score tier)

✅ **Approval Status:** Pre-Qualified

👔 **Employment:** {user.get('employment', 'N/A')}

📋 **Current Obligations:** {loan_status}

━━━━━━━━━━━━━━━━━━━━━"""

    # ─────────────────────────────────────────────────────────
    # 5. Name Mismatch Check
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def check_name_match(provided_name: str, registered_name: str) -> bool:
        """
        Loose name matching — allows partial names.
        e.g., "Ravi" matches "Ravi Kumar".

        Returns:
            True if names match (or either is a substring of the other).
        """
        if not provided_name or not registered_name:
            return True  # Skip check if name not provided

        p = provided_name.strip().lower()
        r = registered_name.strip().lower()
        return p in r or r in p
