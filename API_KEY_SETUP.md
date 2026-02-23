# 🔑 How to Fix: "Having trouble connecting"

## Why Maya Can't Connect

Maya is running in **DEMO MODE** because the Gemini API key is not configured.

Required: You need a **free** Google Gemini API key.

---

## ⚡ Quick Fix (3 Steps)

### Step 1: Get Your Free API Key
1. Go to: **https://aistudio.google.com/app/apikey**
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)

### Step 2: Create `.env` File
In your project folder, create a file named `.env` (NOT `.env.example`):

```
GEMINI_API_KEY=AIzaSy...your-actual-key-here
```

### Step 3: Restart Streamlit
```powershell
# Stop current server (Ctrl+C in terminal)
# Then run:
python -m streamlit run app.py
```

---

## ✅ How to Verify It Works

After restarting:
1. Type: "I need 5 lakhs"
2. **If working:** Maya gives intelligent response
3. **If still broken:** Maya says "I'm having trouble connecting"

---

## Alternative: Set Environment Variable

If you don't want a `.env` file:

```powershell
# Set for current session only
$env:GEMINI_API_KEY="AIzaSy...your-key"

# Then run Streamlit
python -m streamlit run app.py
```

---

##  Troubleshooting

**Error: "404 models/gemini-pro"**
- Your API key is invalid or expired
- Get a new one from https://aistudio.google.com/app/apikey

**Error: "403 Forbidden"**  
- API key doesn't have permission
- Create a new API key with correct project

**Still demo mode after adding key?**
- Check `.env` file name (no `.txt` extension!)
- Check no spaces in `GEMINI_API_KEY=value`
- Restart Streamlit

---

## Current Status

❌ No `.env` file found  
❌ No `GEMINI_API_KEY` environment variable  
✅ App runs but in demo mode  

**Next:** Follow Step 1-3 above to enable full AI!
