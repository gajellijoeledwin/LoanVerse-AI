# LoanVerse AI - Setup Instructions

## 🚀 Quick Start (Without API Key)

The app is now running in **DEMO MODE** without requiring a Gemini API key!

You can test all the UI features:
- ✅ Sidebar simulators (Traffic Source & User Personas)
- ✅ Chat interface with basic responses
- ✅ Loan amount slider
- ✅ E-KYC verification
- ✅ Eligibility checking
- ✅ PDF sanction letter generation

## 🔑 To Enable Full AI Features

Set your Gemini API key as an environment variable:

### Windows PowerShell:
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

### Windows CMD:
```cmd
set GEMINI_API_KEY=your-api-key-here
```

### Get Your API Key:
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy and set it as shown above
4. Restart the Streamlit app

## 🎯 Testing the App

1. **Select a Persona** from the sidebar (e.g., "Ravi Kumar")
2. **Type in chat**: "Hi, I need a loan"
3. **Provide phone**: Type the auto-filled number or "9848022334"
4. **Give consent**: Type "Yes"
5. **Click**: "Verify Identity with Aadhaar"
6. **Adjust slider** or type amount in chat
7. **Click**: "Check Eligibility"
8. **Download** the sanction letter if approved!

## 📝 Current Status

- ✅ App is running at http://localhost:8501
- ⚠️ Running in DEMO MODE (no API key detected)
- ✅ All UI features functional
- ✅ Backend logic working (DTI, risk-based pricing, etc.)
- ⚠️ AI responses are basic fallbacks (set API key for full AI)

Enjoy testing LoanVerse AI!
