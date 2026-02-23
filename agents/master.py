"""
LoanVerse AI - Master Agent (Maya)
===================================
The Orchestrator - Routes tasks to specialized Worker Agents.
Tracks conversation state, detects intent, and enforces compliance (DPDP/RBI).

Features:
- Robust Regex for Indian numerical slang (50k, 1.5L)
- DPDP Consent Gate (Explicit permission check)
- Hub-and-Spoke Routing to Worker Agents
- Compliance "Mule Hunter" for fraud detection

Author: LoanVerse Team
Purpose: Tata Capital Techathon 2026
"""

import re
from typing import Dict, Optional, List, Tuple, Any
from enum import Enum
import time

# ============================================================================
# STATE MACHINE & INTENTS
# ============================================================================

class ConversationPhase(Enum):
    """
    Tracks the strict 7-Phase consultative flow.
    """
    PHASE_1_WARM_OPENING = "warm_opening"
    PHASE_2_PURPOSE_DISCOVERY = "purpose_discovery"
    PHASE_3_VERIFICATION = "verification"
    PHASE_4_NEEDS_ANALYSIS = "needs_analysis"
    PHASE_5_OPTIONS_PRESENTATION = "options_presentation"
    PHASE_6_CONFIRMATION = "confirmation"
    PHASE_7_DOCUMENTATION = "documentation"

class Intent(Enum):
    """
    User intent classification.
    """
    GREETING = "greeting"
    LOAN_REQUEST = "loan_request"
    AMOUNT_CHANGE = "amount_change"
    TENURE_CHANGE = "tenure_change"
    PROVIDE_PHONE = "provide_phone"
    PROVIDE_SALARY = "provide_salary"
    RATE_NEGOTIATION = "rate_negotiation"
    ACCEPTANCE = "acceptance"
    REJECTION = "rejection"
    QUESTION = "question"
    UNKNOWN = "unknown"

# ============================================================================
# MASTER AGENT (MAYA)
# ============================================================================

class MasterAgent:
    """
    Maya - The Master Agent and Orchestrator.
    Responsible for maintaining state and routing to Worker Agents.
    """
    
    def __init__(self, traffic_source: str = "Direct Visit"):
        self.traffic_source = traffic_source
        self.phase = ConversationPhase.PHASE_1_WARM_OPENING
        self.conversation_history = []
        self.user_context = {
            "phone": None,
            "name": None,
            "verified": False,
            "consent_given": False
        }
        
    def get_contextual_greeting(self) -> str:
        """Generate traffic-aware greeting message."""
        greetings = {
            "Direct Visit": "Hello! I'm Maya, your AI Relationship Manager. How can I assist you with a personal loan today?",
            "📧 Email: Wedding Loan": "Welcome back! 💍 I see you clicked our Wedding Loan email. Your ₹5L pre-approved offer is ready. Shall we explore?",
            "📱 Ad: Pre-Approved Offer": "Hi there! 🎉 You've been pre-selected for a special loan offer. I can unlock your rate in 2 minutes. Ready?",
            "📧 Email: Home Renovation": "Welcome! 🏡 Let's turn your dream home into reality. What improvements are you planning?",
            "📱 Ad: Medical Emergency": "Hello. I understand this might be urgent. We're here to help with medical expenses. Checking your limit now..."
        }
        return greetings.get(self.traffic_source, greetings["Direct Visit"])
    
    def analyze_input(self, user_input):
        """Analyze input for intent and entities."""
        intent = self.detect_intent(user_input)
        entities = {}
        
        # Extract basic entities
        amount = self.extract_amount(user_input)
        if amount:
            entities['amount'] = amount
            
        phone = self.extract_phone(user_input)
        if phone:
            entities['phone'] = phone
            
        return intent, entities
            
    def detect_intent(self, user_message: str) -> Intent:
        """
        Classify user intent using pattern matching (Rule-based NLU).
        """
        msg = user_message.lower()
        
        # High Priority: Phone Numbers
        if re.search(r'\b[6-9]\d{9}\b', msg): return Intent.PROVIDE_PHONE
        
        # Explicit Acceptance/Rejection
        if any(w in msg for w in ['yes', 'yeah', 'yep', 'ok', 'okay', 'proceed', 'agree', 'sure']): return Intent.ACCEPTANCE
        if any(w in msg for w in ['no', 'nope', 'cancel', 'refuse', 'stop', 'don\'t']): return Intent.REJECTION
        
        # Financial Intents
        # Handle "5L", "50k", "1Cr" using Regex to avoid false positives on 'l' letter
        financial_pattern = r'\d+\s*(l|lakh|cr|crore|k|thousand)'
        financial_keywords = ['lakh', 'crore', '₹', 'rupees', 'loan']
        
        if re.search(financial_pattern, msg) or any(w in msg for w in financial_keywords) or re.search(r'\d{3,}', msg): 
            if 'loan' in msg and 'need' in msg: return Intent.LOAN_REQUEST
            return Intent.AMOUNT_CHANGE
            
        if any(w in msg for w in ['year', 'month', 'tenure', 'duration']): return Intent.TENURE_CHANGE
        if any(w in msg for w in ['salary', 'income', 'earning', 'ctc']): return Intent.PROVIDE_SALARY
        if any(p in msg for p in ['rate', 'interest', 'high', 'expensive', 'lower']): return Intent.RATE_NEGOTIATION
        
        # Conversational Intents
        if any(w in msg for w in ['hi', 'hello', 'hey', 'namaste']): return Intent.GREETING
        if '?' in msg: return Intent.QUESTION
        
        return Intent.UNKNOWN
    
    def extract_amount(self, user_message: str) -> Optional[float]:
        """
        Extract loan amount from user input.
        Handles: 50k, 5L, 10 lakhs, 2.5 crore, Hinglish slang, word numbers, INR prefix.
        """
        msg = user_message.lower()
        
        # Word number mappings (English and Hindi)
        word_to_num = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'fifty': 50, 'hundred': 100,
            'ek': 1, 'do': 2, 'teen': 3, 'char': 4, 'paanch': 5, 'panch': 5,
            'chhe': 6, 'saat': 7, 'aath': 8, 'nau': 9, 'das': 10,
            'dedh': 1.5, 'dhai': 2.5, 'sawa': 1.25, 'paune': 0.75
        }
        
        # Multiplier mappings
        multipliers = {
            'thousand': 1000, 'hajar': 1000, 'hazaar': 1000, 'k': 1000,
            'lakh': 100000, 'lac': 100000, 'l': 100000, 'peti': 100000,
            'crore': 10000000, 'cr': 10000000, 'khokha': 10000000
        }

        # 1. Compound Pattern: "1 lakh 50 thousand" (Must be first!)
        compound_match = re.search(r'(\d+)\s*(?:lakh|l)\s*(\d+)\s*(?:thousand|k)', msg)
        if compound_match:
            lakhs = int(compound_match.group(1))
            thousands = int(compound_match.group(2))
            return (lakhs * 100000.0) + (thousands * 1000.0)

        # 2. Word Combinations: "dedh lakh", "paanch peti"
        for word, num in word_to_num.items():
            for unit, mult in multipliers.items():
                if len(unit) == 1: continue # Skip single letters for words
                pattern = f"\\b{word}\\s+{unit}\\b"
                if re.search(pattern, msg):
                    return num * mult
        
        # 3. Digit + Unit Patterns ("50k", "5L", "1.5 Cr")
        # Strict boundary \b is crucial to avoid "loan" -> "l"
        # Added plurals: lakhs, crores, lacs
        MAX_LOAN_AMOUNT = 10000000  # ₹1 crore maximum
        
        patterns = [
            (r'(\d+\.?\d*)\s*(cr|crore|crores|khokha)\b', 10000000),
            (r'(\d+\.?\d*)\s*(l|lakh|lakhs|lac|lacs|peti)\b', 100000),
            (r'(\d+\.?\d*)\s*(k|thousand|thousands|hajar|hazaar)\b', 1000)
        ]
        
        for pattern, mult in patterns:
            match = re.search(pattern, msg)
            if match:
                amount = float(match.group(1)) * mult
                # Cap at max loan amount
                if amount > MAX_LOAN_AMOUNT:
                    return MAX_LOAN_AMOUNT
                return amount
        
        # 4. Word + Thousand ("fifty thousand")
        for word, num in word_to_num.items():
            if re.search(f"\\b{word}\\s+thousand\\b", msg):
                return num * 1000.0

        # Pattern 5: "one and half lakh", "one and half crore"
        if 'one and half' in msg or 'and half' in msg:
            if 'lakh' in msg or 'lac' in msg:
                return 1.5 * 100000
            elif 'crore' in msg or 'cr' in msg:
                return 1.5 * 10000000
        
        # 6. Improved Plain Number Extraction (Handle "INR 5,00,000")
        # Remove commas for easier parsing
        clean_msg = msg.replace(',', '')
        
        # Pattern A: Explicit Currency ("inr 500000", "rs 500000", "₹500000")
        currency_match = re.search(r'(?:inr|rs|₹)\.?\s*(\d+)', clean_msg)
        if currency_match:
            return float(currency_match.group(1))
            
        # Pattern B: Standalone large number (likely loan amount)
        # Exclude 10-digit phone numbers (starts with 6-9)
        # Match 5+ digits (10000+) to be safe for loan context
        plain_matches = re.finditer(r'\b(\d{5,})\b', clean_msg)
        for match in plain_matches:
            num_str = match.group(1)
            num = float(num_str)
            
            # Simple heuristic: If it's a 10 digit number starting with 6-9, it's a phone, skip it.
            if len(num_str) == 10 and num_str[0] in '6789':
                continue
            
            # Cap unrealistic amounts at ₹1 crore (10 million)
            MAX_LOAN_AMOUNT = 10000000  # ₹1 crore
            if num > MAX_LOAN_AMOUNT:
                return MAX_LOAN_AMOUNT
                
            return num
        
        # 7. Pure Hindi Loan Phrases (no explicit numbers)
        # Common in rural/semi-urban areas or very simple literacy users
        # Return default amount (5 lakhs) when user indicates they need a loan
        hindi_loan_phrases = [
            'paisa chahiye', 'loan chahiye', 'udhar chahiye',
            'paise chahiye', 'help loan', 'need loan'
        ]
        if any(phrase in msg for phrase in hindi_loan_phrases):
            # Return default loan amount (5 lakhs = 500000)
            return 500000.0
        
        return None
    
    def extract_phone(self, user_message: str) -> Optional[str]:
        """Extract valid Indian phone number from user input.
        Handles formats like:
          - '9278901234'           (bare 10-digit)
          - '+91 92789 01234'      (international with spaces)
          - '+919278901234'        (international without spaces)
          - '91-9278901234'        (country code with dash)
          - '092789 01234'         (with leading 0)
        """
        import re as _re
        # Step 1: normalise the message — strip country prefix variants so we
        # can match the plain 10-digit number in one clean pass.
        # Remove '+91', '91' (when followed by a space/dash) or leading '0'
        cleaned = _re.sub(r'(?:^\+91|\+91|^91(?=\s|-)|(?<=\s)91(?=\s))', '', user_message).strip()
        # Remove all remaining separators (spaces, dashes, dots, parentheses)
        # only in regions that look like a phone cluster
        # Try to match a 10-digit Indian mobile number starting with 6-9
        match = _re.search(r'(?<!\d)([6-9]\d{9})(?!\d)', _re.sub(r'[\s\-.]', '', cleaned))
        if match:
            return match.group(1)
        # Fallback: try original message without normalisation
        match = _re.search(r'\b([6-9]\d{9})\b', user_message)
        return match.group(1) if match else None

    
    def extract_salary(self, user_message: str) -> Optional[float]:
        """Extract salary info."""
        msg = user_message.lower()
        k_match = re.search(r'(\d+)\s*k', msg)
        if k_match: return float(k_match.group(1)) * 1000
        num_match = re.search(r'(?:salary|income|earning|ctc).*?(\d{4,})', msg.replace(',', ''))
        if num_match: return float(num_match.group(1))
        return None
    
    def enforce_compliance(self, user_message: str) -> Optional[str]:
        """
        'Mule Hunter' - Compliance Guardrail.
        Detects coercion, fraud, crypto, and age violations.
        """
        msg = user_message.lower()
        
        # Coercion red flags
        coercion_flags = [
            'my husband', 'my wife', 'forcing me', 'help someone else', 
            'commission', 'my boss', 'someone else', 'for my friend',
            'making me', 'told me to'
        ]
        if any(flag in msg for flag in coercion_flags):
            return "⚠️ **Compliance Alert:** For your security, personal loans can strictly only be taken for your own use. I cannot proceed with this application."
        
        # Fraud red flags
        fraud_flags = [
            'fake', 'forge', 'forged', 'fabricate', 'false salary', 
            'false document', 'edit the pdf', 'edit pdf', 'edit document',
            'fake pan', 'fake id'
        ]
        if any(flag in msg for flag in fraud_flags):
            return "⚠️ **Compliance Alert:** I cannot assist with any fraudulent documentation. This violates our lending policies and legal regulations."
        
        # Bribery red flags
        bribery_flags = [
            'pay you extra', 'bribe', 'extra money for you', "i'll pay you",
            'give you something', 'reward you', 'tip you', 'pay extra',
            'money for approval', 'commission for you', 'extra for approval'
        ]
        if any(flag in msg for flag in bribery_flags):
            return "⚠️ **Compliance Alert:** I cannot accept any bribes, tips, or extra payments. All loan decisions are made by our automated underwriting system based purely on creditworthiness."

        # Crypto Policy
        if any(w in msg for w in ['bitcoin', 'crypto', 'usdt', 'eth', 'btc']):
            return "⚠️ **Policy Alert:** We do not accept cryptocurrency for EMI payments or loan disbursements. Only Indian Rupees (INR) via banking channels are supported."

        # Age Policy
        age_match = re.search(r'\b(\d{1,2})\s*(?:years|yrs)\s*old', msg)
        if age_match:
            age = int(age_match.group(1))
            if age < 18:
                return "⚠️ **Eligibility Alert:** You must be at least 21 years old to apply for a loan. We cannot proceed."
        
        return None

    def route_to_agent(self, intent: Intent, user_message: str, context: Dict) -> Tuple[str, Dict]:
        """
        THE BRAIN: Routes tasks based on Conversation Phase & Intent.
        """
        
        # PHASE: IDENTITY -> CONSENT
        if self.phase == ConversationPhase.PHASE_3_VERIFICATION:
            if intent == Intent.PROVIDE_PHONE:
                phone = self.extract_phone(user_message)
                if phone:
                    return ("master_agent", {
                        "action": "request_consent",
                        "phone": phone
                    })
        
        # PHASE: CONSENT -> KYC
        if self.phase == ConversationPhase.PHASE_3_VERIFICATION:
            if intent == Intent.ACCEPTANCE:
                return ("verification_agent", {
                    "action": "perform_kyc",
                    "phone": context.get('phone_buffer')
                })
            elif intent == Intent.REJECTION:
                return ("master_agent", {"action": "consent_denied"})
        
        # PHASE: NEGOTIATION (Core Loop)
        if self.phase == ConversationPhase.PHASE_4_NEEDS_ANALYSIS or self.phase == ConversationPhase.PHASE_2_PURPOSE_DISCOVERY:
            
            # Rate Negotiation
            if intent == Intent.RATE_NEGOTIATION:
                return ("sales_agent", {
                    "action": "handle_rate_objection",
                    "credit_score": context.get('credit_score', 750)
                })
            
            # Loan Structuring
            if intent == Intent.LOAN_REQUEST or intent == Intent.AMOUNT_CHANGE:
                amount = self.extract_amount(user_message)
                if amount:
                    return ("sales_agent", {
                        "action": "negotiate_amount",
                        "requested_amount": amount,
                        "limit": context.get('limit', 0)
                    })
            
            # Final Acceptance -> Underwriting
            if intent == Intent.ACCEPTANCE:
                return ("underwriting_agent", {
                    "action": "check_eligibility",
                    "phone": context.get('phone'),
                    "amount": context.get('current_amount'),
                    "salary": context.get('salary_input')
                })
        
        # PHASE: VERIFICATION (Conditional Approval)
        if self.phase == ConversationPhase.PHASE_5_OPTIONS_PRESENTATION:
            if intent == Intent.PROVIDE_SALARY:
                salary = self.extract_salary(user_message)
                if salary:
                    return ("underwriting_agent", {
                        "action": "check_eligibility",
                        "phone": context.get('phone'),
                        "amount": context.get('current_amount'),
                        "salary": salary
                    })

        # Default Fallback
        return ("master_agent", {"action": "conversational_response"})
    
    def build_agent_workflow_trace(self, agent_name: str) -> List[Dict]:
        """Generates the visual 'Thinking...' steps for st.status"""
        traces = {
            "master_agent": [
                {"msg": "🧠 Master Agent: Analyzing intent...", "sleep": 0.3}
            ],
            "verification_agent": [
                {"msg": "⚙️ Master Agent: Routing to Verification...", "sleep": 0.5},
                {"msg": "🔍 Verification Agent: Connecting to Mock CRM Server...", "sleep": 0.8},
                {"msg": "✅ Identity Verified: Name & Address Match.", "sleep": 0.5}
            ],
            "sales_agent": [
                {"msg": "🧠 Master Agent: Identifying financial parameters...", "sleep": 0.3},
                {"msg": "💼 Sales Agent: Calculating optimization options...", "sleep": 0.6}
            ],
            "underwriting_agent": [
                {"msg": "⚙️ Master Agent: Handover to Risk Engine...", "sleep": 0.4},
                {"msg": "📡 Underwriting Agent: Fetching Credit Bureau API...", "sleep": 0.7},
                {"msg": "📊 Decision Engine: Running DTI & Risk Models...", "sleep": 0.6}
            ]
        }
        return traces.get(agent_name, [])

# ============================================================================
# WORKER AGENTS (LOGIC SIMULATORS)
# ============================================================================

class SalesAgent:
    """Handles negotiation psychology."""
    @staticmethod
    def handle_rate_objection(credit_score: int) -> str:
        # Dynamic response based on score
        if credit_score >= 800:
            return f"I completely understand. However, because of your excellent score of {credit_score}, I've already unlocked our **Prime Rate of 10.5%** for you. This is significantly lower than credit cards (36-42%)."
        else:
            return f"I hear you. The rate of 11.5% is customized based on your current credit profile. By maintaining timely payments on this loan, you can actually improve your score for future borrowings."

class VerificationAgent:
    """Handles Mock KYC."""
    @staticmethod
    def perform_kyc(phone: str) -> Dict:
        # Logic is imported dynamically to prevent circular imports in some IDEs
        # In a real app, this calls the logic layer
        return {"action": "verify_kyc_logic", "phone": phone}