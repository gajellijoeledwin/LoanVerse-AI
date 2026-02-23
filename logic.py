"""
LoanVerse AI - Core Business Logic
===================================
This module contains ALL mathematical calculations, underwriting rules, and data access layers.
The AI agent (Maya) is FORBIDDEN from doing any math - it must call these functions.

Features:
- Risk-Based Pricing (Interest rates based on Credit Score)
- Strict DTI Logic (Includes existing EMIs)
- Regulatory Compliance (Expiry dates, PII handling)
- Mock E-KYC Verification

Author: LoanVerse Team
Purpose: Tata Capital Techathon 2026
"""

import json
import re
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import os

# ============================================================================
# DATA LAYER - Mock Database Access
# ============================================================================

def normalize_phone(phone: str) -> str:
    """
    Normalize any Indian phone number format to a bare 10-digit string.
    Handles: '+91 92789 01234', '+919278901234', '91-9278901234',
             '9278901234', '(+91) 92789-01234', etc.
    """
    if not phone:
        return ""
    # Remove all non-digit characters first
    digits = re.sub(r'\D', '', str(phone))
    # Strip leading 91 country code if present (and result is 12 digits)
    if len(digits) == 12 and digits.startswith('91'):
        digits = digits[2:]
    # Strip leading 0 if present (STD trunk prefix)
    elif len(digits) == 11 and digits.startswith('0'):
        digits = digits[1:]
    return digits


def get_user(phone: str) -> Optional[Dict]:
    """
    Fetch user data from the mock customer database (customers.json).
    Normalizes both input phone and stored phones before comparing,
    so '+91 92789 01234' and '9278901234' both match the same record.
    """
    try:
        # Try different possible paths for the JSON file to prevent path errors
        possible_paths = [
            "data/customers.json",
            "../data/customers.json",
            "./data/customers.json"
        ]
        
        data_path = None
        for path in possible_paths:
            if os.path.exists(path):
                data_path = path
                break
        
        if not data_path:
            print("CRITICAL ERROR: customers.json not found.")
            return None
            
        with open(data_path, "r", encoding='utf-8') as f:
            users = json.load(f)
        
        # Normalize the input phone first
        normalized_input = normalize_phone(phone)
        if not normalized_input:
            return None
        
        # Find user by normalized phone (works for any stored format)
        user = next(
            (u for u in users if normalize_phone(u["phone"]) == normalized_input),
            None
        )
        return user
        
    except Exception as e:
        print(f"ERROR in get_user: {e}")
        return None


def get_user_with_name_check(phone: str, provided_name: str = None) -> Dict:
    """
    Fetch user data AND check whether the provided name matches the registered name.

    Returns a dict with:
      - 'user'            : the customer dict (or None if not found)
      - 'found'           : bool — whether the phone matched any record
      - 'name_match'      : bool — True if names match (or no name provided)
      - 'registered_name' : str  — the name on file (empty string if not found)
    """
    user = get_user(phone)
    if not user:
        return {"user": None, "found": False, "name_match": True, "registered_name": ""}

    registered_name = user.get("name", "")

    if not provided_name:
        # No name to compare against — treat as match
        return {"user": user, "found": True, "name_match": True, "registered_name": registered_name}

    # Case-insensitive, whitespace-normalised comparison
    name_match = provided_name.strip().lower() == registered_name.strip().lower()
    return {
        "user": user,
        "found": True,
        "name_match": name_match,
        "registered_name": registered_name,
    }

# ============================================================================
# FINANCIAL CALCULATIONS - Pure Math Functions
# ============================================================================

def calculate_emi(amount: float, tenure_months: int, rate: float = 10.99) -> int:
    """
    Calculate Equated Monthly Installment (EMI) using the reducing balance method.
    Formula: EMI = [P x R x (1+R)^N] / [(1+R)^N - 1]
    """
    if amount <= 0 or tenure_months <= 0:
        return 0
    
    # Convert annual rate to monthly rate
    r = rate / (12 * 100)
    
    # Calculate EMI using standard formula
    emi = (amount * r * ((1 + r) ** tenure_months)) / (((1 + r) ** tenure_months) - 1)
    
    return round(emi)


def calculate_total_interest(amount: float, tenure_months: int, rate: float = 10.99) -> int:
    """Calculate total interest payable over the loan tenure."""
    emi = calculate_emi(amount, tenure_months, rate)
    total_payment = emi * tenure_months
    total_interest = total_payment - amount
    return round(total_interest)


def calculate_dti_ratio(monthly_emi: float, current_emis: float, monthly_salary: float) -> float:
    """
    Calculate Debt-to-Income (DTI) ratio including EXISTING LOANS.
    Formula: (New EMI + Existing EMIs) / Monthly Salary * 100
    
    This prevents users with high salaries but massive debt from getting approved.
    """
    if monthly_salary <= 0:
        return 100.0  # Infinite DTI - indicates no income or error
    
    total_obligation = monthly_emi + current_emis
    dti = (total_obligation / monthly_salary) * 100
    return round(dti, 2)


def calculate_dti_with_existing_loans(salary: float, proposed_emi: float, current_emis: float) -> dict:
    """
    Calculate Debt-to-Income ratio including existing EMIs
    This is CRITICAL for regulatory compliance
    """
    if salary <= 0:
        return {
            'salary': salary, 'proposed_emi': proposed_emi, 'current_emis': current_emis,
            'total_emi': proposed_emi + current_emis, 'dti': 100.0, 'available_income': 0, 'safe': False
        }
        
    total_emi = proposed_emi + current_emis
    dti = (total_emi / salary) * 100
    
    return {
        'salary': salary,
        'proposed_emi': proposed_emi,
        'current_emis': current_emis,
        'total_emi': total_emi,
        'dti': round(dti, 1),
        'available_income': salary - total_emi,
        'safe': dti < 50
    }


def calculate_safe_tenure(amount: float, salary: float, current_emis: float, rate: float = 13.5) -> int:
    """
    Calculates the minimum tenure (in months) required to keep the EMI safe (DTI <= 50%).
    Returns the exact number of months rounded up, or 0 if mathematically impossible.
    """
    import math
    max_safe_emi = (salary * 0.5) - current_emis
    if max_safe_emi <= 0:
        return 0
        
    r = rate / (12 * 100)
    
    # If the interest only payment is more than the max safe EMI, the loan can never be paid off
    if amount * r >= max_safe_emi:
        return 0
        
    X = max_safe_emi / (amount * r)
    
    # Derived from: X = (1+r)^n / ((1+r)^n - 1)
    try:
        n = math.log(X / (X - 1)) / math.log(1 + r)
        return math.ceil(n)
    except (ValueError, ZeroDivisionError):
        return 0



def calculate_safe_amount(salary: float, current_emis: float, rate: float = 13.5, tenure: int = 60) -> int:
    """Calculate the maximum loan amount that keeps DTI under 50%."""
    max_safe_emi = (salary * 0.5) - current_emis
    if max_safe_emi <= 0:
        return 0
        
    r = rate / (12 * 100)
    numerator = ((1 + r) ** tenure) - 1
    denominator = r * ((1 + r) ** tenure)
    
    safe_amount = max_safe_emi * (numerator / denominator)
    return int(round(safe_amount / 10000) * 10000)


def validate_amount_request(user_profile: dict, requested_amount: float) -> dict:
    """
    Smart validation considering existing loans.
    Returns status: INSTANT_APPROVE, CONDITIONAL, EXCEED_LIMIT, or OVER_CAPACITY.
    """
    limit = user_profile['limit']
    salary = user_profile['salary']
    current_emis = user_profile.get('current_emis', 0)
    
    # Case 1: Within pre-approved limit
    if requested_amount <= limit:
        return {
            'status': 'INSTANT_APPROVE',
            'message': 'No additional verification needed!',
            'require_salary': False
        }
    
    # Case 2: Above limit but need salary check
    elif requested_amount <= limit * 2:
        # Calculate if even POSSIBLE given existing EMIs
        proposed_emi = calculate_emi(requested_amount, 36, get_risk_based_rate(user_profile['score']))
        max_safe_emi = (salary * 0.5) - current_emis
        
        if proposed_emi <= max_safe_emi:
            return {
                'status': 'CONDITIONAL',
                'message': 'Need salary verification for this amount',
                'require_salary': True
            }
        else:
            # Mathematically impossible -> Can't even do 60 months? Let's check 60 months instead for flexibility
            # The prompt requested 36 months, but max affordable relies on 60 months for stretching. 
            safe_amount_60 = calculate_safe_amount(salary, current_emis, get_risk_based_rate(user_profile['score']), 60)
            
            # If even at 60 months the safe amount is less than requested
            if safe_amount_60 < requested_amount:
                return {
                    'status': 'OVER_CAPACITY',
                    'message': f'Max you can afford: ₹{safe_amount_60:,}',
                    'alternative_amount': safe_amount_60
                }
            else:
                # Can afford on 60 months but maybe not 36. We'll give conditional and let Goldilocks show options.
                return {
                    'status': 'CONDITIONAL',
                    'message': 'Need salary verification for this amount',
                    'require_salary': True
                }
    
    # Case 3: Way over limit
    else:
        return {
            'status': 'EXCEED_LIMIT',
            'message': f'Max available: ₹{limit * 2:,}',
            'alternative_amount': limit * 2
        }


def get_risk_based_rate(credit_score: int) -> float:
    """
    Determines interest rate based on credit score buckets.
    Risk-Based Pricing Model (Compliance Requirement).
    """
    if credit_score >= 800:
        return 10.50  # Prime Rate (VIP)
    elif credit_score >= 750:
        return 11.50  # Standard Rate
    elif credit_score >= 700:
        return 13.50  # Sub-Prime / Risk Premium
    else:
        return 15.00  # High Risk (usually rejected)


def generate_goldilocks_options(amount: float, rate: float, salary: float, current_emis: float) -> dict:
    """
    Generate 3 distinct options with DTI analysis for each.
    Calculates specific DTI remaining and total out-of-pocket metrics.
    """
    options = {
        'aggressive': {
            'tenure': 24,
            'emi': calculate_emi(amount, 24, rate),
            'total_interest': calculate_total_interest(amount, 24, rate)
        },
        'balanced': {
            'tenure': 36,
            'emi': calculate_emi(amount, 36, rate),
            'total_interest': calculate_total_interest(amount, 36, rate)
        },
        'relaxed': {
            'tenure': 60,
            'emi': calculate_emi(amount, 60, rate),
            'total_interest': calculate_total_interest(amount, 60, rate)
        }
    }
    
    # Calculate DTI for each option (including existing EMIs)
    # Only if salary is > 0
    valid_salary = salary if salary > 0 else 1 # avoid division by zero
    for option_key, option in options.items():
        total_emi = option['emi'] + current_emis
        dti = (total_emi / valid_salary) * 100
        option['dti'] = round(dti, 1) if salary > 0 else None
        option['available_income'] = salary - total_emi if salary > 0 else None
        option['total_emi'] = total_emi
        
        # Add a label mapping for easier presentation
        if option_key == 'aggressive':
            option['label'] = "Fast (24 months)"
        elif option_key == 'balanced':
            option['label'] = "Balanced (36 months)"
        else:
            option['label'] = "Extended (60 months)"
            
    return options

def get_goldilocks_options(amount: float, annual_rate: float, user_salary: float = None, current_emis: float = 0) -> dict:
    """
    Generate 3 distinct EMI options for customer choice (Goldilocks Strategy).
    This FORCES Maya to have a conversation, not just approve instantly.
    
    Psychology principles:
    - Option 1 (Aggressive): Makes Option 2 look reasonable by comparison
    - Option 2 (Balanced): What we want them to pick (anchored as "recommended")
    - Option 3 (Relaxed): Safety net for low-income customers
    
    Based on MAYA_PLAYBOOK.md sales psychology framework.
    
    Args:
        amount: Loan amount requested
        annual_rate: Interest rate (e.g., 11.5)
        user_salary: Monthly salary (optional, for DTI calculation)
        current_emis: Existing monthly EMI obligations (Bug 2 fix: include in DTI)
    
    Returns:
        dict with 'aggressive', 'balanced', 'relaxed' keys, each containing:
            - label: Display name
            - tenure: Months
            - emi: Monthly payment
            - total_interest: Total interest payable
            - pitch: Why choose this option
            - dti_percentage: % of salary INCLUDING existing EMIs (if salary provided)
            - popularity: Social proof percentage
            - savings_vs_relaxed: Savings compared to longest tenure
    """
    
    # Tenure options (in months)
    aggressive_tenure = 24   # 2 years - Fast repayment
    balanced_tenure = 36     # 3 years - Sweet spot (most popular)
    relaxed_tenure = 60      # 5 years - Lowest EMI burden
    
    # Calculate EMIs for each tenure
    aggressive_emi = calculate_emi(amount, aggressive_tenure, annual_rate)
    balanced_emi = calculate_emi(amount, balanced_tenure, annual_rate)
    relaxed_emi = calculate_emi(amount, relaxed_tenure, annual_rate)
    
    # Calculate total interest payable
    aggressive_interest = calculate_total_interest(amount, aggressive_tenure, annual_rate)
    balanced_interest = calculate_total_interest(amount, balanced_tenure, annual_rate)
    relaxed_interest = calculate_total_interest(amount, relaxed_tenure, annual_rate)
    
    # DTI percentages INCLUDING existing EMIs (Bug 2 fix: was new_emi/salary only)
    if user_salary and user_salary > 0:
        aggressive_dti = ((aggressive_emi + current_emis) / user_salary * 100)
        balanced_dti   = ((balanced_emi   + current_emis) / user_salary * 100)
        relaxed_dti    = ((relaxed_emi    + current_emis) / user_salary * 100)
    else:
        aggressive_dti = balanced_dti = relaxed_dti = None
    
    return {
        "aggressive": {
            "label": "Fast Repayment",
            "tenure": aggressive_tenure,
            "emi": aggressive_emi,
            "total_interest": aggressive_interest,
            "pitch": "Pay off fastest, save maximum interest",
            "dti_percentage": round(aggressive_dti, 1) if aggressive_dti else None,
            "popularity": "15%",  # Social proof: minority choose this
            "savings_vs_relaxed": round(relaxed_interest - aggressive_interest, 2)
        },
        "balanced": {
            "label": "Recommended",
            "tenure": balanced_tenure,
            "emi": balanced_emi,
            "total_interest": balanced_interest,
            "pitch": "Most popular choice - comfortable payments",
            "dti_percentage": round(balanced_dti, 1) if balanced_dti else None,
            "popularity": "68%",  # Social proof: majority choose this (anchoring)
            "savings_vs_relaxed": round(relaxed_interest - balanced_interest, 2)
        },
        "relaxed": {
            "label": "Extended",
            "tenure": relaxed_tenure,
            "emi": relaxed_emi,
            "total_interest": relaxed_interest,
            "pitch": "Lowest monthly burden for maximum cash flow",
            "dti_percentage": round(relaxed_dti, 1) if relaxed_dti else None,
            "popularity": "17%",  # Social proof: small group choose this
            "savings_vs_relaxed": 0  # No savings vs itself
        }
    }


# ============================================================================
# MOCK E-KYC LAYER
# ============================================================================

def verify_kyc(phone: str, pan_input: str = "ABCDE1234F") -> Dict:
    """
    Simulates E-KYC verification against NSDL/UIDAI via Mock CRM.
    """
    user = get_user(phone)
    if not user:
        return {"status": "FAILED", "reason": "User not found in Government Database"}
    
    # Simulate a successful match
    return {
        "status": "VERIFIED",
        "name": user['name'],
        "aadhaar_last_4": "XXXX", 
        "pan": user.get('pan', pan_input), # Fetch real PAN from JSON if available
        "address": user.get('address', 'Unknown Address'),
        "city": user.get('city', 'Unknown City')
    }

# ============================================================================
# UNDERWRITING ENGINE - The 4 Commandments
# ============================================================================

def check_eligibility(phone: str, requested_amount: float, 
                      monthly_salary: Optional[float] = None) -> Dict:
    """
    The Core Underwriting Logic.
    
    THE 4 COMMANDMENTS:
    1. Credit Score < 700 → HARD REJECT
    2. Amount ≤ Pre-Approved Limit → INSTANT APPROVAL (Subject to Safety DTI Check)
    3. Amount ≤ 2x Limit → CONDITIONAL APPROVAL (Salary Check + DTI <= 50%)
    4. Amount > 2x Limit → HARD REJECT
    """
    
    # Step 0: Fetch User Data
    user = get_user(phone)
    if not user:
        return {
            "status": "USER_NOT_FOUND",
            "reason": "No pre-approved offer found for this number.",
            "limit": 0, "max_eligible": 0
        }
    
    # Extract user attributes
    credit_score = user['score']
    pre_approved_limit = user['limit']
    current_emis = user.get('current_emis', 0) # Default to 0 if missing
    salary_on_file = user.get('salary', 0)
    
    # RULE 1: Credit Score Gatekeeping
    if credit_score < 700:
        return {
            "status": "REJECT",
            "reason": f"Credit score of {credit_score} is below our minimum requirement of 700.",
            "user_name": user['name'],
            "credit_score": credit_score,
            "limit": pre_approved_limit,
            "max_eligible": 0
        }

    # Determine Dynamic Interest Rate
    interest_rate = get_risk_based_rate(credit_score)
    
    # RULE 2: Instant Approval (Sweet Spot)
    if requested_amount <= pre_approved_limit:
        # Bug 3 fix: Use 60-month EMI for DTI check (most lenient — gives customer best chance).
        # If they can't afford even the 60-month option, they truly can't afford this loan.
        emi_for_dti = calculate_emi(requested_amount, 60, interest_rate)
        emi_standard = calculate_emi(requested_amount, 36, interest_rate)
        
        # SAFETY CHECK: Even for pre-approved, check if Existing Debt + New Loan > 60% DTI
        # This catches the "Debt Trap" scenario (High Income, High Debt)
        dti = calculate_dti_ratio(emi_for_dti, current_emis, salary_on_file)
        
        if dti > 60:
             return {
                "status": "REJECT",
                "reason": f"Although pre-approved, your existing EMIs (₹{current_emis:,}) plus this new loan would exceed 60% of your income even on the longest tenure.",
                "dti": dti,
                "current_emis": current_emis
             }

        return {
            "status": "APPROVE",
            "type": "INSTANT",
            "reason": f"Loan of ₹{requested_amount:,.0f} is within your pre-approved limit.",
            "user_name": user['name'],
            "approved_amount": requested_amount,
            "emi": emi_standard,   # Standard 36-month EMI for display
            "tenure_months": 36,
            "interest_rate": interest_rate,
            "limit": pre_approved_limit,
            "max_eligible": pre_approved_limit,
            "pan": user.get('pan', 'NA')
        }
    
    # RULE 3: Conditional Approval (Requires Salary Verification)
    if requested_amount <= (2 * pre_approved_limit):
        
        # If salary input not provided via chat yet, request it
        if monthly_salary is None:
            return {
                "status": "CONDITIONAL",
                "reason": f"₹{requested_amount:,.0f} exceeds your limit of ₹{pre_approved_limit:,.0f}. Please provide your salary slip to verify repayment capacity.",
                "user_name": user['name'],
                "limit": pre_approved_limit,
                "max_eligible": 2 * pre_approved_limit,
                "needs": "SALARY_SLIP"
            }
        
        # Salary provided - check DTI ratio using the SPECIFIC interest rate
        # Bug 3 fix: Use 60-month EMI for DTI gate (most lenient); still show 36-month EMI in results
        emi_for_dti = calculate_emi(requested_amount, 60, interest_rate)
        emi = calculate_emi(requested_amount, 36, interest_rate)
        dti = calculate_dti_ratio(emi_for_dti, current_emis, monthly_salary)
        
        # DTI must be ≤ 50% for high-value loans (using lenient 60-month basis)
        if dti > 50:
            return {
                "status": "REJECT",
                "reason": f"Based on your salary (₹{monthly_salary}) and existing obligations (₹{current_emis}), the new EMI exceeds our 50% DTI limit.",
                "user_name": user['name'],
                "emi": emi, "dti": dti,
                "monthly_salary": monthly_salary,
                "limit": pre_approved_limit,
                "max_eligible": 0
            }
        
        return {
            "status": "APPROVE",
            "type": "SALARY_VERIFIED",
            "reason": f"Approved ₹{requested_amount:,.0f} after salary verification. Your DTI is healthy at {dti:.1f}%.",
            "user_name": user['name'],
            "approved_amount": requested_amount,
            "emi": emi,
            "dti": dti,
            "tenure_months": 36,
            "interest_rate": interest_rate,
            "monthly_salary": monthly_salary,
            "limit": pre_approved_limit,
            "max_eligible": 2 * pre_approved_limit,
            "pan": user.get('pan', 'NA')
        }
    
    # RULE 4: Hard Cap Exceeded
    max_possible = 2 * pre_approved_limit
    return {
        "status": "REJECT",
        "reason": f"₹{requested_amount:,.0f} exceeds our maximum lending limit of ₹{max_possible:,.0f} (2x your pre-approved limit).",
        "user_name": user['name'],
        "limit": pre_approved_limit,
        "max_eligible": max_possible,
        "requested": requested_amount
    }

# ============================================================================
# NEGOTIATION HELPERS
# ============================================================================

def suggest_counter_offer(phone: str, rejected_amount: float) -> Dict:
    """Suggest an alternative amount if rejected."""
    user = get_user(phone)
    if not user: return {"suggested_amount": 0, "reason": "User not found"}
    
    max_eligible = 2 * user['limit']
    credit_score = user['score']
    rate = get_risk_based_rate(credit_score)
    
    # If they asked for more than 2x, suggest 2x (if DTI allows)
    if rejected_amount > max_eligible:
        return {
            "suggested_amount": max_eligible,
            "reason": f"While ₹{rejected_amount:,.0f} isn't possible, I can offer you ₹{max_eligible:,.0f} subject to salary verification.",
            "requires": "SALARY_SLIP"
        }
    
    # If DTI failed, reverse engineer max EMI (45% of salary as safe zone)
    # Using salary from file as the baseline
    salary = user.get('salary', 50000) 
    current_emis = user.get('current_emis', 0)
    
    # Max EMI they can afford = (Salary * 0.50) - Existing EMIs
    max_affordable_emi = (salary * 0.50) - current_emis
    
    if max_affordable_emi <= 0:
        return {
            "suggested_amount": 0,
            "reason": "Your existing obligations are too high to support a new loan right now."
        }

    # Reverse EMI Logic to find Principal
    # P = EMI * ((1+r)^n - 1) / (r * (1+r)^n)
    r = rate / (12 * 100)
    n = 36 # Default 3 years
    numerator = ((1 + r) ** n) - 1
    denominator = r * ((1 + r) ** n)
    
    suggested_amount = max_affordable_emi * (numerator / denominator)
    suggested_amount = round(suggested_amount / 10000) * 10000 # Round to nearest 10k
    
    return {
        "suggested_amount": int(suggested_amount),
        "reason": f"Based on your existing commitments, ₹{int(suggested_amount):,} is a comfortable loan amount for you.",
        "emi": calculate_emi(suggested_amount, 36, rate)
    }

def get_loan_amount_options(phone: str) -> Tuple[int, int, int]:
    """Generate 3 loan amount options: Conservative (50%), Sweet Spot (Limit), Maximum (150%).
    
    DEPRECATED: This is an old function kept for backward compatibility.
    For EMI plan options, use get_goldilocks_options() instead.
    """
    user = get_user(phone)
    if not user: return (50000, 100000, 200000)
    limit = user['limit']
    return (int(limit * 0.5), limit, int(limit * 1.5))

# ============================================================================
# SANCTION LETTER DATA PREPARATION
# ============================================================================

def prepare_sanction_data(phone: str, approved_amount: float, 
                         tenure_months: int = 36, rate: float = 10.99) -> Dict:
    """Prepare data for PDF generation, including valid-until date and KFS details."""
    user = get_user(phone)
    if not user: return {}
    
    emi = calculate_emi(approved_amount, tenure_months, rate)
    total_interest = calculate_total_interest(approved_amount, tenure_months, rate)
    total_payment = (emi * tenure_months)
    
    loan_id = f"LV{datetime.now().strftime('%Y%m%d')}{phone[-4:]}"
    today = datetime.now()
    valid_until = today + timedelta(days=30) # Offer valid for 30 days
    
    return {
        "loan_id": loan_id,
        "customer_name": user['name'],
        "phone": phone,
        "pan": user.get('pan', 'XXXX'),
        "address": user.get('address', 'Registered Address'),
        "city": user.get('city', 'India'),
        "date_issued": today.strftime("%d %B %Y"),
        "valid_until": valid_until.strftime("%d %B %Y"),  # Compliance Field
        "approved_amount": approved_amount,
        "interest_rate": rate,
        "tenure_months": tenure_months,
        "tenure_years": tenure_months // 12,
        "emi": emi,
        "total_interest": total_interest,
        "total_payment": total_payment,
        "credit_score": user['score'],
        "pre_approved_limit": user['limit']
    }