"""
LoanVerse AI - Conversation Templates
=====================================
Maya's dialogue scripts for each conversation phase.
Balances bank risk protection with customer empathy.

Author: LoanVerse Team
"""

from typing import Dict, Optional, List
from datetime import datetime


class ConversationTemplates:
    """
    Centralized repository of conversation scripts.
    Each template balances:
    - Bank Protection: Compliance, risk disclosure, verification
    - Customer Empathy: Celebration, explanation, alternatives
    """
    
    @staticmethod
    def get_time_greeting() -> str:
        """Get time-appropriate greeting."""
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning"
        elif hour < 17:
            return "Good afternoon"
        else:
            return "Good evening"
    
    # ========================================================================
    # PHASE 1: IDENTITY & TRUST BUILDING
    # ========================================================================
    
    @staticmethod
    def greeting_message(user_name: Optional[str] = None) -> str:
        """Initial greeting message."""
        greeting = ConversationTemplates.get_time_greeting()
        if user_name:
            return f"{greeting}, {user_name}! 👋 I'm Maya, your personal loan assistant."
        return f"{greeting}! 👋 I'm Maya, your personal loan assistant."
    
    @staticmethod
    def identity_verified(user_name: str, credit_score: int) -> str:
        """After successful identity verification."""
        return f"""✅ **Identity Verified!**

Welcome back, {user_name}! I've pulled your credit profile.

📊 **Your Credit Score: {credit_score}**  
{ConversationTemplates._get_score_commentary(credit_score)}

You have a pre-approved loan limit ready! Would you like to explore your options?"""
    
    @staticmethod
    def _get_score_commentary(score: int) -> str:
        """Get encouraging commentary based on score."""
        if score >= 800:
            return "🌟 Excellent! You qualify for our Prime rates."
        elif score >= 750:
            return "✨ Great! You're in the premium tier."
        elif score >= 700:
            return "👍 Good! You qualify for competitive rates."
        else:
            return "We can still work with this. Let's see what we can do."
    
    @staticmethod
    def consent_request(phone: str) -> str:
        """DPDP compliance - request consent."""
        return f"""🔒 **Data Privacy Notice** (Required by RBI)

To process your loan application, I need to:
• Fetch your credit report from CIBIL
• Verify your employment details
• Access your banking history

**Important:** This is a **soft inquiry** and will NOT affect your credit score.

Your data is encrypted and will only be used for loan processing.

Do I have your consent to proceed? (Yes/No)"""
    
    # ========================================================================
    # PHASE 2: DISCOVERY & NEED ASSESSMENT
    # ========================================================================
    
    @staticmethod
    def discovery_purpose(pre_approved_limit: float) -> str:
        """Ask about loan purpose."""
        limit_formatted = f"₹{pre_approved_limit:,.0f}"
        return f"""Great! I can see you qualify for a **pre-approved limit of {limit_formatted}**. 🎁

What brings you here today?

💍 **Wedding** - Celebrate your special day  
📚 **Education** - Invest in your future  
🏥 **Medical** - Healthcare expenses  
🏠 **Home Renovation** - Upgrade your space  
✈️ **Travel** - Dream vacation  
💼 **Business** - Entrepreneurial needs

Or just tell me in your own words what you need!"""
    
    @staticmethod
    def celebration_response(purpose: str) -> str:
        """Celebrate customer's purpose with empathy."""
        celebrations = {
            "wedding": "How wonderful! Congratulations on your upcoming wedding! 🎊💒",
            "education": "Excellent! Investing in education is one of the best decisions. 📚✨",
            "medical": "I understand. We're here to help during this challenging time. 🏥💙",
            "travel": "How exciting! Everyone deserves a break. ✈️🌍",
            "home": "Great choice! A comfortable home is so important. 🏠🔨",
            "business": "Fantastic! We love supporting entrepreneurs. 💼🚀"
        }
        return celebrations.get(purpose.lower(), "Thank you for sharing that with me! Let's find the right loan for you.")
    
    @staticmethod
    def ask_amount(purpose: str) -> str:
        """Ask for desired loan amount."""
        typical_ranges = {
            "wedding": "Wedding loans typically range from ₹1L to ₹5L",
            "education": "Education loans typically range from ₹2L to ₹10L",
            "medical": "Medical loans typically range from ₹50K to ₹3L",
            "travel": "Travel loans typically range from ₹50K to ₹2L",
            "home": "Home renovation loans typically range from ₹1L to ₹8L",
            "business": "Business loans typically range from ₹2L to ₹10L"
        }
        range_text = typical_ranges.get(purpose.lower(), "Typical amounts range from ₹50K to ₹10L")
        
        return f"""{range_text}.

How much funding do you need?"""
    
    # ========================================================================
    # PHASE 3: RISK ASSESSMENT & TRANSPARENT DISCLOSURE
    # ========================================================================
    
    @staticmethod
    def analyzing_profile() -> str:
        """Message shown while checking eligibility."""
        return """⚙️ **Analyzing your profile...**

Let me check:
✓ Credit worthiness
✓ Repayment capacity  
✓ Pre-approved offers
✓ Best available rate

This will take just a moment..."""
    
    @staticmethod
    def instant_approval_offer(
        amount: float,
        interest_rate: float,
        emi: float,
        tenure: int,
        credit_score: int,
        total_repayment: float,
        total_interest: float
    ) -> str:
        """Present instant approval with full transparency."""
        return f"""✅ **GREAT NEWS! You're INSTANTLY APPROVED!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 **YOUR PERSONALIZED OFFER**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Loan Amount:**      ₹{amount:,.0f}  
**Interest Rate:**    {interest_rate}% p.a. (Prime Rate for your score)  
**Monthly EMI:**      ₹{emi:,.0f}  
**Tenure:**           {tenure} months  
**Total Repayment:**  ₹{total_repayment:,.0f}  
**Total Interest:**   ₹{total_interest:,.0f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **WHY THIS RATE?**  
Your rate of {interest_rate}% is based on:
• Credit Score: {credit_score} ({ConversationTemplates._get_score_commentary(credit_score).replace('🌟 ', '').replace('✨ ', '').replace('👍 ', '')})
• Clean repayment history  
• Stable employment

This is **SIGNIFICANTLY LOWER** than:
• Credit Cards: 36-42% p.a.
• Gold Loans: 14-18% p.a.

⚠️ **IMPORTANT DISCLOSURES:**  
✓ This is an UNSECURED loan (no collateral needed)  
✓ Missing EMIs will affect your credit score  
✓ Processing fee: 1% (₹{amount * 0.01:,.0f}) deducted from disbursement  
✓ Prepayment allowed after 6 months (No penalty!)

Would you like to **proceed** with this offer, or would you like to **adjust** the amount/tenure?"""
    
    @staticmethod
    def conditional_approval(
        amount: float,
        emi: float,
        reason: str,
        required_document: str
    ) -> str:
        """Conditional approval requiring additional verification."""
        return f"""📋 **CONDITIONAL PRE-APPROVAL**

Good news! Your loan of ₹{amount:,.0f} can be processed, but I need one more thing.

**Why:** {reason}

**What I Need:** {required_document}

Once I receive this, I can move forward with:
• EMI: ₹{emi:,.0f}/month
• Instant disbursal within 24 hours

Would you like to upload the document now?"""
    
    @staticmethod
    def rejection_with_empathy(reason: str, score: int) -> str:
        """Rejection message with constructive guidance."""
        return f"""I understand this isn't the news you hoped for. 😔

**Current Status:** Unfortunately, I'm unable to approve the loan at this time.

**Reason:** {reason}

**But Here's the Good News:**  
This is NOT permanent. Your credit score of {score} can improve!

💡 **Steps to Qualify in Future:**
1. Pay existing EMIs on time for 6 months
2. Reduce credit card utilization below 30%
3. Avoid multiple loan inquiries

📞 **Alternative Options:**
• Secured loans (against FD/Gold) have easier approval
• A co-applicant can strengthen your application

Would you like me to check if you qualify for a secured loan instead?"""
    
    # ========================================================================
    # PHASE 4: NEGOTIATION
    # ========================================================================
    
    @staticmethod
    def handle_rate_objection(credit_score: int, rate: float) -> str:
        """Handle "rate is too high" objection.""" 
        base_rate = 6.5
        operating_cost = 2.0
        risk_premium = 2.5
        score_discount = -0.5 if credit_score >= 750 else 0
        
        return f"""I completely understand your concern about the rate.

Let me show you exactly how we arrived at {rate}%:

📊 **RATE BREAKDOWN:**
• Base Rate (RBI Repo):             {base_rate}%
• Bank Operating Cost:              {operating_cost}%  
• Risk Premium (unsecured loan):    {risk_premium}%
• Your Score Discount:              {score_discount}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**FINAL RATE:**                     {rate}%

✅ **GOOD NEWS:** You're already getting our **Prime Rate** because of your excellent score of {credit_score}!

💡 **TIP:** If you make all EMIs on time for this loan, your score will improve to 800+, qualifying you for 10.5% on future loans.

Would you like to proceed at {rate}%, or would you prefer a **smaller loan amount** to reduce the EMI burden?"""
    
    @staticmethod
    def handle_amount_increase(
        requested: float,
        limit: float,
        salary: float,
        current_emis: float
    ) -> str:
        """Handle customer requesting more than limit."""
        proposed_emi = requested * 0.033  # Rough 3.3% per month estimate
        dti_percent = ((proposed_emi + current_emis) / salary) * 100
        
        return f"""I appreciate you sharing that you need ₹{requested:,.0f}.

🔍 Let me check if that's feasible...

⚠️ **CHALLENGE IDENTIFIED:**  
Your current limit is ₹{limit:,.0f}.

Here's why:
• Salary on file: ₹{salary:,.0f}/month
• Existing EMIs: ₹{current_emis:,.0f}/month
• RBI Guidelines: Total EMI should not exceed 50-60% of income
• EMI for ₹{requested:,.0f} would be: ₹{proposed_emi:,.0f}/month
• **Your DTI:** {dti_percent:.1f}% of salary

🎯 **HERE ARE YOUR OPTIONS:**

**OPTION 1:** Take ₹{limit:,.0f} now
→ Build credit history with timely payments
→ Reapply for top-up after 6 months

**OPTION 2:** Provide salary slip showing higher income
→ If you earn ₹{requested / limit * salary:,.0f}+/month, I can unlock the higher limit

**OPTION 3:** Add a co-applicant (spouse/parent)
→ Combined income can support ₹{requested:,.0f} EMI

Which option works best for you?"""
    
    # ========================================================================
    # PHASE 5: FINAL ACCEPTANCE & SANCTION
    # ========================================================================
    
    @staticmethod
    def final_consent_checklist(emi: float, tenure: int, processing_fee: float) -> str:
        """Final consent before generating sanction letter."""
        return f"""🔐 **FINAL CONFIRMATION**

Before I generate your sanction letter, please confirm you understand:

✓ My Monthly EMI will be ₹{emi:,.0f} for {tenure} months
✓ I consent to the processing fee of ₹{processing_fee:,.0f}
✓ I will provide my bank account details for disbursement
✓ I authorize LoanVerse to report this loan to CIBIL
✓ Late payments will affect my credit score

Type **'CONFIRM'** to proceed with the sanction letter."""
    
    @staticmethod
    def sanction_success(amount: float) -> str:
        """Congratulations message after sanction generation."""
        return f"""🎊 **CONGRATULATIONS! Your loan is APPROVED!**

Your ₹{amount:,.0f} loan has been sanctioned!

📄 **Your Sanction Letter is Ready**  
[Download button will appear below]

📨 **NEXT STEPS:**
1. Download and e-sign the sanction letter
2. Upload: PAN Card + Bank Statement (last 3 months)
3. Funds will be disbursed within **24 hours** ⚡

🎁 **WELCOME BONUS:** Your first EMI is postponed by 15 days!

Is there anything else I can help clarify?"""
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format amount in Indian currency style."""
        return f"₹{amount:,.0f}"
    
    @staticmethod
    def get_fallback_response() -> str:
        """Generic fallback when intent is unclear."""
        return """I'm not quite sure I understood that. Could you rephrase?

Or you can:
• Ask about **loan amount** or **EMI**
• Request to change **tenure** or **amount**
• Ask me to **explain** any terms"""

    @staticmethod
    def build_profile_presentation(user_profile: dict, purpose: str, ask_amount: bool = True) -> str:
        """
        Create personalized welcome message using ALL customer data fields
        """
        name = user_profile['name']
        score = user_profile['score']
        limit = user_profile['limit']
        city = user_profile['city']
        employment = user_profile['employment']
        current_loans = user_profile['current_loan_details']
        current_emis = user_profile['current_emis']
        
        from logic import get_risk_based_rate
        rate = get_risk_based_rate(score)
        
        # Score tier messaging
        if score >= 780:
            score_tier = "Exceptional! Top 10% in India"
            tier_emoji = "🏆"
        elif score >= 750:
            score_tier = "Excellent! Top 25% in India"
            tier_emoji = "⭐"
        elif score >= 720:
            score_tier = "Very Good! Above average"
            tier_emoji = "✓"
        elif score >= 700:
            score_tier = "Good! Qualifies for standard rates"
            tier_emoji = "✓"
        else:
            score_tier = "Fair - just below our preferred range"
            tier_emoji = "⚠️"
        
        response = f"""Thank you! Give me just a moment while I pull up your profile...

[Checking credit bureaus...]

Perfect! Welcome back, **{name}**! 👋

I can see you're calling from **{city}** and you've maintained {'excellent' if score >= 750 else 'good'} credit. Here's what I found:

━━━━━━━━━━━━━━━━━━━━━
📊 **YOUR FINANCIAL PROFILE**
━━━━━━━━━━━━━━━━━━━━━

💳 **Credit Score:** {score} {tier_emoji}
   {score_tier}

💰 **Pre-Approved Limit:** ₹{limit:,}
   (Instant approval for amounts up to this)

📈 **Your Interest Rate:** {rate}% per annum
   {'(Our best rate for your score range!)' if score >= 780 else '(Standard rate for your score tier)'}

✅ **Approval Status:** Pre-Qualified
   (No additional documents needed for ≤₹{limit:,})

👔 **Employment:** {employment}
"""
        
        # Affordability Math explicitly shown to the user
        salary = user_profile.get('salary', 0)
        max_dti_emi = (0.60 * salary) - current_emis if salary > 0 else 0
        
        # Approximate max eligible amount (assuming 60 months at current rate)
        r = rate / (12 * 100)
        n = 60
        max_eligible_amount = max_dti_emi * (((1 + r)**n - 1) / (r * (1 + r)**n)) if r > 0 else 0
        max_eligible_amount = round(max_eligible_amount / 10000) * 10000
        
        response += f"━━━━━━━━━━━━━━━━━━━━━\n"
        response += f"🧮 **AFFORDABILITY & LIMITS**\n"
        response += f"━━━━━━━━━━━━━━━━━━━━━\n"
        if salary > 0:
            response += f"• **Monthly Income:** ₹{salary:,}/month\n"
        if current_emis > 0:
            response += f"• **Current EMIs:** ₹{current_emis:,}/month ({current_loans})\n"
        else:
            response += f"• **Current EMIs:** ₹0/month (Clean slate!)\n"
            
        response += f"• **Pre-Approved Instant Limit:** ₹{limit:,}\n"
        if max_eligible_amount > limit:
            response += f"• **Max Capacity (DTI Based):** Up to ₹{max_eligible_amount:,.0f} with income proof\n\n"
        else:
            response += f"• **Max Capacity (DTI Based):** ₹{max_eligible_amount:,.0f}\n\n"
        
        # Premium customer routing
        if score >= 780 and user_profile.get('salary', 0) >= 100000:
            response += f"""💡 **Premium Customer Status:**
As a high-income, 780+ score customer, you unlock our lowest prime rates, 
priority 12-hour processing, and VIP routing. You have massive borrowing capacity! 🎉
"""
        # Educational moment about their score
        elif score >= 780:
            response += f"""💡 **What Your {score} Score Means:**
Your exceptional credit gives you:
• Lowest possible interest rate ({rate}%)
• Highest approval limits
• Fastest processing
• Best loan terms

You're in the elite tier! 🎉
"""
        elif score >= 750:
            response += f"""💡 **What Your {score} Score Means:**
Your excellent credit gives you:
• Competitive interest rate ({rate}%)
• High approval limits
• Quick processing

Great job maintaining your credit! ⭐
"""
        elif score < 700:
            response += f"""💡 **About Your {score} Score:**
Your score is just below our 700 threshold. Here's what that means:
• You're only {700 - score} points away from better rates
• Current rate: {rate}% (vs {rate - 2}% for 750+ scores)
• With 6 months of on-time payments, you could jump to 720+

I'll still try to get you the best terms available today!
"""
        
        if ask_amount:
            response += f"""━━━━━━━━━━━━━━━━━━━━━

Now, for your **{purpose}** - how much exactly are you looking to borrow?

(Keep in mind your ₹{limit:,} pre-approved limit for instant approval!)"""
        
        return response

    @staticmethod
    def build_needs_analysis_response(user_profile: dict, requested_amount: float, purpose: str, amount_validation_res: dict, proposed_emi: float, total_emi: float, dti: float, safe: bool) -> str:
        """
        Empathic needs analysis using validation and DTI data
        """
        salary = user_profile['salary']
        current_emis = user_profile.get('current_emis', 0)
        score = user_profile['score']
        status = amount_validation_res.get('status')
        name = user_profile['name']
        
        response = f"Got it - ₹{int(requested_amount):,} for your {purpose}.\n\nLet me check your affordability...\n\n"
        
        # Empathic Rejection Case
        if not safe and score < 700:
            response += f"""━━━━━━━━━━━━━━━━━━━━━
⚠️ **AFFORDABILITY ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━

Your Current Situation:
• Monthly Salary: ₹{salary:,}
• Existing EMIs: ₹{current_emis:,}
• Proposed New EMI: ₹{int(proposed_emi):,} (for ₹{int(requested_amount):,})
• **Total EMIs: ₹{int(total_emi):,}** ({dti}% of income) ⚠️

━━━━━━━━━━━━━━━━━━━━━

{name}, I need to be honest with you:

Adding ₹{int(proposed_emi):,} EMI to your existing ₹{current_emis:,} would leave you with very 
little per month for everything else.

That's financially very risky. RBI guidelines cap EMIs at 50% of income 
to protect borrowers like you from over-leveraging.

━━━━━━━━━━━━━━━━━━━━━
💡 **HERE'S MY ADVICE:**
━━━━━━━━━━━━━━━━━━━━━

**Option 1: Smaller Amount**
If we reduce the amount, we can make the EMI safer.

**Option 2: Loan Consolidation** (Better choice!)
Consolidate your existing loans + this new need.
• Single lower EMI
• Better rate on consolidated amount
• Cleaner finances

**Option 3: Wait 6-12 Months**
If your existing loans are paying down, your capacity will increase.

Which option makes most sense for your situation?"""
            return response
            
        # Clean Slate / Easy Approval Case
        elif current_emis == 0 and safe:
            response += f"""━━━━━━━━━━━━━━━━━━━━━
✅ **EXCELLENT SITUATION!**
━━━━━━━━━━━━━━━━━━━━━

Your Profile:
• Monthly Salary: ₹{salary:,}
• Current EMIs: ₹0 (Clean slate! 🎉)
• Proposed EMI: ₹{int(proposed_emi):,} (for ₹{int(requested_amount):,})
• **DTI Ratio: {dti}%** ✅ (Very comfortable!)

━━━━━━━━━━━━━━━━━━━━━

{name}, you're in an excellent position!

With zero existing loans and ₹{int(salary/1000)}k salary, this loan is very 
comfortable for you.

Let me show you three repayment options..."""
            return response
            
        # Education Loan Check
        elif 'education loan' in str(user_profile.get('current_loan_details', '')).lower() and safe:
            response += f"""{name}, I see you have an education loan with ₹{current_emis:,} monthly EMI.

Good news: Since you've been paying this on time (your {score} score proves it!), 
lenders see this as POSITIVE credit history. Education loans are viewed 
favorably!

For your ₹{int(requested_amount):,} request:
• Your total EMIs would be: ₹{int(total_emi):,}
• That's only {dti}% of your ₹{int(salary/1000)}k salary
• Leaves ₹{int(salary - total_emi):,} for living expenses

This loan will be very manageable. Let me show you the options..."""
            return response
            
        # Standard Approval Case
        elif safe:
            response += f"""━━━━━━━━━━━━━━━━━━━━━
✅ **AFFORDABILITY CHECK**
━━━━━━━━━━━━━━━━━━━━━

Your Profile:
• Monthly Salary: ₹{salary:,}
• Existing EMIs: ₹{current_emis:,}
• Proposed EMI: ₹{int(proposed_emi):,}
• **Total DTI Ratio: {dti}%** ✅ (Under safe 50% limit)

Everything looks good, {name}. You have healthy remaining income for living expenses. 
Let's look at your options..."""
            return response
            
        # Graceful Conditional Pass (Fails 36 months, but passes 60 months)
        elif not safe and status == 'CONDITIONAL':
            response += f"""━━━━━━━━━━━━━━━━━━━━━
⚠️ **TENURE EXTENSION REQUIRED**
━━━━━━━━━━━━━━━━━━━━━

Your Profile:
• Monthly Salary: ₹{salary:,}
• Existing EMIs: ₹{current_emis:,}

{name}, a standard 3-year loan pushes your Debt-to-Income (DTI) to {dti}%, which exceeds our safety threshold of 50%.
However, I've run the numbers and see that we **can** make this ₹{int(requested_amount):,} amount work if we extend the repayment tenure!

Let me show you your extended options..."""
            return response

        # Fallback Over Capacity (If conditionally failed DTI above)
        else:
            safe_amt = amount_validation_res.get('alternative_amount', 0)
            response += f"""⚠️ **AFFORDABILITY ANALYSIS**
            
I've checked the numbers, and adding this loan would push your Debt-to-Income (DTI) to {dti}%, which exceeds our safety threshold of 50%.
The maximum safe amount you can borrow right now is ₹{safe_amt:,}. Would you like to proceed with this amount instead?"""
            return response


    @staticmethod
    def build_goldilocks_presentation(options: dict) -> str:
        """
        Generate Goldilocks presentation showing exactly how much of their salary remains.
        """
        response = ""
        
        # Safe checking if DTI isn't calculated because salary wasn't populated
        import copy
        opts = copy.deepcopy(options)
        
        agg = opts['aggressive']
        bal = opts['balanced']
        rel = opts['relaxed']
        
        response += f"""━━━━━━━━━━━━━━━━━━━━━
📋 **OPTION 1: {agg['label']}**
━━━━━━━━━━━━━━━━━━━━━
EMI: ₹{int(agg['emi']):,}/month"""
        if agg.get('total_emi'):
            response += f"\n**Total EMIs:** ₹{int(agg['total_emi']):,} ({agg['dti']}% of salary) ✓"
            response += f"\nAvailable for other expenses: ₹{int(agg['available_income']):,}/month"
            
        response += f"\n\n━━━━━━━━━━━━━━━━━━━━━\n📋 **OPTION 2: {bal['label']}** ⭐\n━━━━━━━━━━━━━━━━━━━━━\nEMI: ₹{int(bal['emi']):,}/month"
        if bal.get('total_emi'):
            response += f"\n**Total EMIs:** ₹{int(bal['total_emi']):,} ({bal['dti']}% of salary) ✓"
            response += f"\nAvailable for other expenses: ₹{int(bal['available_income']):,}/month"
            
        response += f"\n\n━━━━━━━━━━━━━━━━━━━━━\n📋 **OPTION 3: {rel['label']}**\n━━━━━━━━━━━━━━━━━━━━━\nEMI: ₹{int(rel['emi']):,}/month"
        if rel.get('total_emi'):
            response += f"\n**Total EMIs:** ₹{int(rel['total_emi']):,} ({rel['dti']}% of salary) ✓"
            response += f"\nAvailable for other expenses: ₹{int(rel['available_income']):,}/month"
            
        response += f"\n\n━━━━━━━━━━━━━━━━━━━━━\n\n💡 **Maya's Recommendation:** Option 2\n\nThis keeps your debt burden comfortable while offering reasonable interest savings. Which option works best for your situation?"
        return response

    @staticmethod
    def build_confirmation_message(user_profile: dict, chosen_option: dict, purpose: str, amount: float) -> str:
        """
        Personalized confirmation using employment and location data
        """
        name = user_profile['name']
        city = user_profile['city']
        employment = user_profile['employment']
        
        from logic import get_risk_based_rate
        rate = get_risk_based_rate(user_profile['score'])
        
        response = f"""Perfect choice, {name}!

━━━━━━━━━━━━━━━━━━━━━
✅ **YOUR LOAN SUMMARY**
━━━━━━━━━━━━━━━━━━━━━

📋 **Loan Details:**
• Borrower: {name}
• Location: {city}
• Employment: {employment}
• Loan Purpose: {purpose.capitalize()}
• Amount: ₹{int(amount):,}
• Interest Rate: {rate}% p.a.
• Tenure: {chosen_option.get('tenure', 36)} months
• EMI: ₹{int(chosen_option.get('emi', 0)):,}

━━━━━━━━━━━━━━━━━━━━━
"""
        # Add location/purpose specific advice
        if "Mumbai" in city:
            response += """
💡 **Mumbai-Specific Tip:**
Consider keeping ₹50k as a buffer - living expenses in Mumbai can have unexpected surprises!
"""
        elif "Bangalore" in city and "Engineer" in employment:
            response += """
💡 **Bangalore Tech Tip:**
With your tech sector job, you likely get bonuses. Consider prepaying 
any bonus amount to finish the loan faster and save on interest!
"""
        elif "medical" in purpose.lower():
            response += """
🏥 **Medical Loan Advice:**
I've marked this as a medical priority. Keep a buffer for follow-up tests and post-op care.
"""
        
        response += "\nShall I generate your official Sanction Letter?"
        return response

# Export singleton instance
templates = ConversationTemplates()
