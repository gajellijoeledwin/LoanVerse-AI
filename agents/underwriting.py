"""
LoanVerse AI - Underwriting Agent
===================================
Worker Agent: Fetches credit score from Mock Credit Bureau API
and validates loan eligibility using the 4-rule underwriting engine.

Author: LoanVerse Team
Purpose: Tata Capital Techathon 2026
"""

from typing import Optional, Dict


class UnderwritingAgent:
    """
    Underwriting Worker Agent — the Risk Engine.
    
    Responsibilities:
    1. Fetch credit score (out of 900) from the Mock Credit Bureau API
    2. Apply 4-rule eligibility decision matrix
    3. Return structured decision to Master Agent
    
    THE 4 RULES:
    - Rule 1: Credit Score < 700 → HARD REJECT
    - Rule 2: Amount ≤ Pre-Approved Limit → INSTANT APPROVE (+ DTI safety check)
    - Rule 3: Amount ≤ 2x Limit → CONDITIONAL (salary slip required, EMI ≤ 50% salary)
    - Rule 4: Amount > 2x Limit → HARD REJECT
    """

    @staticmethod
    def fetch_credit_score(phone: str) -> Dict:
        """
        Mock Credit Bureau API — fetches credit score (out of 900).
        
        In production: calls CIBIL / Equifax / Experian REST API.
        For demo: reads score from the dummy CRM (customers.json).
        
        Args:
            phone: 10-digit Indian mobile number (normalized)
            
        Returns:
            dict with score, max_score (900), bureau_ref, found
        """
        from logic import get_user, normalize_phone
        from datetime import datetime

        user = get_user(phone)
        if not user:
            return {
                "found": False,
                "score": None,
                "max_score": 900,
                "bureau": "CIBIL Mock",
                "timestamp": datetime.now().isoformat(),
                "ref": "NOT_FOUND"
            }

        # Mock bureau reference number
        ref = f"CIBIL/{datetime.now().strftime('%Y%m%d')}/{normalize_phone(phone)[-4:]}"

        return {
            "found": True,
            "score": user["score"],
            "max_score": 900,
            "bureau": "CIBIL Mock",
            "timestamp": datetime.now().isoformat(),
            "ref": ref
        }

    @staticmethod
    def evaluate(phone: str, requested_amount: float,
                 monthly_salary: Optional[float] = None) -> Dict:
        """
        Run the 4-rule underwriting engine.
        
        Args:
            phone: Customer's mobile number
            requested_amount: Loan amount requested (₹)
            monthly_salary: Verified monthly salary (₹), required for CONDITIONAL path
            
        Returns:
            dict with 'status' key: APPROVE / REJECT / CONDITIONAL / USER_NOT_FOUND
        """
        from logic import check_eligibility
        return check_eligibility(phone, requested_amount, monthly_salary)

    @staticmethod
    def get_eligibility_summary(phone: str, requested_amount: float) -> str:
        """
        Human-readable eligibility summary for Master Agent logs/traces.
        """
        credit = UnderwritingAgent.fetch_credit_score(phone)
        if not credit["found"]:
            return "❌ Customer not found in CRM."

        score = credit["score"]
        result = UnderwritingAgent.evaluate(phone, requested_amount)
        status = result.get("status", "UNKNOWN")

        status_map = {
            "APPROVE": f"✅ APPROVED | Score: {score}/900 | Type: {result.get('type', 'N/A')}",
            "REJECT": f"❌ REJECTED | Score: {score}/900 | Reason: {result.get('reason', 'N/A')}",
            "CONDITIONAL": f"⚠️ CONDITIONAL | Score: {score}/900 | Requires: Salary Slip Upload",
        }
        return status_map.get(status, f"Unknown status: {status}")
