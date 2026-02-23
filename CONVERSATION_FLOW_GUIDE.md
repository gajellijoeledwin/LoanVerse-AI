# 🧪 LoanVerse Testing & Conversation Guide

## ✅ Ideal Flow (The Happy Path)
**Scenario: User states amount first (The "Intent Redirect" Test)**

1. **User:** "I need 5 lakhs"
   * *System:* Detects amount, but checks `user_data`. It is None.
   * **Maya:** "I'd be happy to help with ₹5,00,000! To give you the best rate, may I have your mobile number first?"

2. **User:** "9848022334" (Ravi)
   * *System:* Fetches profile. Sets `user_data`.
   * **Maya:** "Welcome back, Ravi! I see you have a pre-approved limit of ₹5,00,000. Shall we proceed with the 5 lakhs you mentioned?"

3. **User:** "Yes, please"
   * *System:* Detects ACCEPTANCE. Runs Underwriting.
   * **Maya:** "Perfect. Checking eligibility... 🎉 Approved! Your EMI is ₹16,488. Should I generate the sanction letter?"

4. **User:** "Yes"
   * *System:* Generates PDF.
   * **Maya:** "Here is your Key Fact Statement (KFS). The offer is valid for 30 days."

---

## 📋 Test Scenarios by Persona

### ✅ Scenario 1: Instant Approval (Ravi Kumar)
**Phone:** 9848022334

**Flow:**
1. Select "Ravi Kumar" from persona dropdown
2. Type: "Hi, I need a loan of Rs. 5,00,000"
3. Maya should acknowledge amount and ask for consent
4. Type: "Yes"
5. Click "Verify Identity with Aadhaar"
6. System shows verified details
7. Click "Check Eligibility"
8. **Expected:** ✅ INSTANT APPROVAL
   - EMI: ₹16,488/month
   - Rate: 11.5% p.a.
   - Download sanction letter available

---

### ❌ Scenario 2: Hard Reject - Low Credit Score (Priya Sharma)
**Phone:** 9886011223

**Flow:**
1. Select "Priya Sharma" from persona dropdown
2. Type: "I need 3 lakh urgently"
3. Maya acknowledges and asks for consent
4. Type: "Yes"
5. Click "Verify Identity with Aadhaar"
6. Click "Check Eligibility"
7. **Expected:** ❌ HARD REJECT
   - Reason: Credit score 680 below minimum 700
   - Maya should provide constructive advice on improving score

---

### ⚠️ Scenario 3: Conditional Approval - Salary Required (Karan Malhotra)
**Phone:** 9820088990

**Flow:**
1. Select "Karan Malhotra" from persona dropdown
2. Type: "I need 8 lakh for home renovation"
3. Maya asks for consent
4. Type: "Yes"
5. Click "Verify Identity with Aadhaar"
6. Click "Check Eligibility"
7. **Expected:** ⚠️ CONDITIONAL APPROVAL
   - Requesting ₹8L exceeds ₹5L limit
   - System asks for salary verification
   - Maya guides: "Please provide your monthly salary"
8. Type: "80000"
9. **Expected:** ✅ APPROVED after salary check

---

### 💎 Scenario 4: VIP Prime Rate (Amit Gupta)
**Phone:** 9967033445

**Flow:**
1. Select "Amit Gupta" from persona dropdown
2. Type: "I want 10 lakhs"
3. **Expected:** Maya highlights VIP benefits
   - Credit Score: 820 (Excellent!)
   - Prime Rate: 10.5% p.a. (Best tier)
   - Pre-approved limit: ₹10,00,000
4. Continue with KYC and approval
5. **Expected:** Lower EMI due to premium rate

---

### ⛔ Scenario 5: DTI Rejection (Sneha Iyer)
**Phone:** 9810055667

**Flow:**
1. Select "Sneha Iyer" from persona dropdown
2. Type: "I need 5 lakh"
3. Continue through KYC
4. Click "Check Eligibility"
5. **Expected:** ❌ REJECT - High DTI
   - Reason: Existing EMIs (₹35,000) + New loan would exceed 60% DTI
   - Maya explains financial safety concern

---

## ❌ Hallucination Check (The "No UI" Test)

Maya should NEVER mention UI elements. Test these tricky questions:

### Test 1: Amount Change Request
* **User:** "How do I change the amount?"
* **❌ Bad Maya:** "Use the slider on the right." 
* **✅ Good Maya:** "Of course! How much would you like to borrow instead?"

### Test 2: EMI Calculator
* **User:** "Where can I see the EMI?"
* **❌ Bad Maya:** "Check the EMI breakdown section on the right panel."
* **✅ Good Maya:** "Let me calculate that for you. For ₹5 lakhs at 11.5%, your EMI would be ₹16,488/month."

### Test 3: Tenure Change
* **User:** "Can I adjust the loan period?"
* **❌ Bad Maya:** "Use the tenure dropdown to select 2, 3, 4, or 5 years."
* **✅ Good Maya:** "Absolutely! How many years would you prefer - 2, 3, 4, or 5?"

### Test 4: Verification Process
* **User:** "How do I verify?"
* **❌ Bad Maya:** "Click the 'Verify Identity with Aadhaar' button."
* **✅ Good Maya:** "I'll verify your identity now. This will just take a moment."

---

## 🔄 Phase Transition Tests

### Test: Proper Phase Progression

**Expected Flow:**
1. **GREETING** → First message from Maya
2. **IDENTITY** → Asking for phone number
3. **CONSENT** → "Do I have your permission to proceed?"
4. **KYC** → Identity verification
5. **DISCOVERY** → Discussing loan amounts
6. **NEGOTIATION** → EMI options, tenure selection
7. **UNDERWRITING** → Eligibility check
8. **SANCTION** → PDF generation
9. **CLOSURE** → Thank you message

**How to Verify:**
Enable "Debug Info" in sidebar to see current phase

---

## 🎯 Edge Case Testing

### Edge 1: Multiple Amount Changes
1. User: "I need 5 lakhs"
2. User: "Actually, make it 3 lakhs"
3. User: "Wait, 7 lakhs"
4. **Expected:** Maya should acknowledge each change and update EMI calculator

### Edge 2: Consent Refusal
1. Maya: "Do I have your consent?"
2. User: "No"
3. **Expected:** Maya should politely close conversation, phase → CLOSURE

### Edge 3: Mid-Conversation Persona Switch
1. Start with Ravi Kumar
2. Switch to Priya Sharma mid-conversation
3. **Expected:** System resets, loads new user data

### Edge 4: Compliance Red Flag
1. User: "Can I take this loan for my husband?"
2. **Expected:** Maya should immediately refuse:
   - "Personal loans can strictly only be taken for your own use."
   - Process stops, compliance alert shown

---

## 📊 Persona Cheat Sheet (Quick Reference)

| Phone | Name | Score | Limit | Scenario | Expected Outcome |
|-------|------|-------|-------|----------|------------------|
| **9848022334** | Ravi Kumar | 750 | ₹5L | Standard | ✅ Instant Approval |
| **9886011223** | Priya Sharma | 680 | ₹0 | Low Score | ❌ Hard Reject |
| **9810055667** | Sneha Iyer | 740 | ₹6L | High EMIs | ❌ DTI Reject |
| **9967033445** | Amit Gupta | 820 | ₹10L | VIP | ✅ Prime Rate 10.5% |
| **9820088990** | Karan Malhotra | 725 | ₹5L | Above Limit | ⚠️ Conditional (needs salary) |
| **9654033221** | Meera Nair | 780 | ₹7L | Excellent | ✅ Premium Rate 11% |
| **9123455678** | Rajesh Patel | 710 | ₹3L | New Customer | ✅ Standard Rate 12% |
| **9321100998** | Ananya Singh | 800 | ₹8L | High Score | ✅ Premium Rate 10.5% |
| **9988077665** | Vikram Rao | 690 | ₹0 | Below Threshold | ❌ Soft Reject (20 pts away) |
| **9876555432** | Deepak Shah | 760 | ₹6L | Medical Emergency | ✅ Fast-track approval |

---

## 🚀 Demo Presentation Flow

**For showcasing to stakeholders:**

### Act 1: The Perfect Customer (3 mins)
1. Select "Amit Gupta" (820 score)
2. Show greeting, consent flow
3. Demonstrate KYC animation
4. Show VIP rate (10.5%)
5. Generate sanction letter PDF
6. **Highlight:** Seamless UX, personalized rates

### Act 2: The Sales Challenge (2 mins)
1. Select "Karan Malhotra"
2. User requests ₹8L (above ₹5L limit)
3. Show conditional approval flow
4. Maya asks for salary
5. Provide salary, get approved
6. **Highlight:** Smart underwriting, not just approve/reject

### Act 3: The Compliance Hero (1 min)
1. Fresh conversation
2. User: "My wife is forcing me to take this loan"
3. Show compliance block
4. **Highlight:** RBI/DPDP adherence, fraud prevention

### Act 4: The Empathetic Rejection (2 mins)
1. Select "Priya Sharma" (680 score)
2. Show rejection with constructive advice
3. Maya explains how to improve score
4. **Highlight:** Customer-first approach, financial literacy

---

## 🐛 Known Issues & Workarounds

### Issue 1: Slider Spam Messages
**Symptom:** Moving slider triggers chat messages even before verification
**Fix:** Only verified users trigger chat messages on slider change

### Issue 2: Phase Desync
**Symptom:** master_agent.phase ≠ st.session_state.phase
**Fix:** Both updated together in all phase transitions

### Issue 3: Persona Auto-fill Not Working
**Symptom:** Selecting persona doesn't load user data
**Fix:** Persona selector now auto-loads phone + user data + sets CONSENT phase

---

## ✅ Pre-Demo Checklist

Before presenting:
- [ ] Gemini API key is set (check environment variable)
- [ ] All personas load correctly from `customers.json`
- [ ] Sanction letter PDFs generate without errors
- [ ] EMI calculator updates in real-time
- [ ] Maya doesn't mention UI elements in responses
- [ ] Compliance blocks work (test with "husband" keyword)
- [ ] All 10 personas have been tested at least once
- [ ] Browser cache cleared for fresh session
- [ ] Debug info sidebar tested and working

---

## 📝 Testing Notes Template

Use this for systematic testing:

```
Date: _______
Tester: _______
Persona Tested: _______

Flow Steps:
1. [ ] Persona selection works
2. [ ] Greeting appropriate for traffic source
3. [ ] Phone number auto-filled
4. [ ] Consent requested
5. [ ] KYC verification successful
6. [ ] Amount negotiation works
7. [ ] EMI calculator syncs with chat
8. [ ] Eligibility check shows correct result
9. [ ] Sanction letter downloads
10. [ ] No UI hallucinations detected

Issues Found:
- 
- 

Overall Rating: ☆☆☆☆☆
```

---

## 🎓 Training New Users

**3-Minute Quick Start:**
1. "Welcome! This is Maya, an AI loan officer."
2. "Select 'Ravi Kumar' from the sidebar."
3. "Type: 'I need 5 lakh for my daughter's wedding'"
4. "Watch Maya guide you through the process."
5. "Click buttons when Maya prompts you."
6. "Download your loan approval letter!"

**Key Points to Highlight:**
- ✅ Pre-approved offers (no credit check needed)
- ✅ Risk-based pricing (better score = better rate)
- ✅ Instant decisions (no waiting days)
- ✅ Compliance-first (blocks fraud automatically)
- ✅ Transparent pricing (no hidden fees)

---

**End of Testing Guide**

*Last Updated: 2026-02-09*
*Version: 1.0*
