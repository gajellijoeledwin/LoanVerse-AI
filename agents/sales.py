"""
LoanVerse AI - Sales Agent
===========================
Handles negotiation psychology and objection handling.

Author: LoanVerse Team
Purpose: Tata Capital Techathon 2026
"""

class SalesAgent:
    """Handles negotiation psychology."""
    
    @staticmethod
    def handle_rate_objection(credit_score: int) -> str:
        """
        Handle customer objections about interest rates.
        Uses dynamic responses based on credit score.
        """
        # Dynamic response based on score
        if credit_score >= 800:
            return f"I completely understand. However, because of your excellent score of {credit_score}, I've already unlocked our **Prime Rate of 10.5%** for you. This is significantly lower than credit cards (36-42%)."
        else:
            return f"I hear you. The rate of 11.5% is customized based on your current credit profile. By maintaining timely payments on this loan, you can actually improve your score for future borrowings."
