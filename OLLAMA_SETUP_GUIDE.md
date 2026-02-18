# 🔧 Setting Up Ollama for Local LLM

## The Problem Was Fixed

The Google Gemini API integration has been **completely removed** and replaced with the original **Ollama (Llama 3.1)** local LLM setup.

## What Changed

### ✅ Fixed Files:
1. **`utils/context_project_match.py`** - Restored original Llama implementation
2. **`.env`** - Removed Gemini API key, kept Ollama URL only
3. **`requirements.txt`** - Removed `google-genai` dependency

### ❌ Removed:
- All Google Gemini API code
- Google Gemini dependencies
- API key requirements

### ✅ Restored:
- Original Ollama/Llama 3.1 integration
- Local LLM processing
- No external API dependencies

---

## How to Set Up Ollama (Local LLM)

### Step 1: Install Ollama

**Windows:**
1. Download from: https://ollama.com/download
2. Run the installer
3. Ollama will start automatically as a service

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Pull the Llama 3.1 Model

Open a terminal and run:
```bash
ollama pull llama3.1:8b
```

This will download the Llama 3.1 8B parameter model (~4.7GB).

**Note:** First download may take 5-10 minutes depending on your internet speed.

### Step 3: Verify Ollama is Running

**Check if Ollama is running:**
```bash
ollama list
```

You should see:
```
NAME              SIZE    MODIFIED
llama3.1:8b      4.7 GB  X minutes ago
```

**Test the model:**
```bash
ollama run llama3.1:8b "Hello, how are you?"
```

If you get a response, Ollama is working correctly! ✅

### Step 4: Verify API Endpoint

Ollama runs on `http://localhost:11434` by default.

**Test the API:**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

You should get a JSON response with the model's answer.

---

## Environment Configuration

Your `.env` file should now contain ONLY:

```env
OLLAMA_URL=http://localhost:11434/api/generate
```

**No API keys needed!** Everything runs locally. 🎉

---

## Starting the Application (Updated Steps)

### Step 1: Ensure Ollama is Running

Ollama should start automatically, but you can verify:

```bash
# Check if Ollama is running
ollama list

# If not running, start it (usually automatic)
# On Windows: Check system tray for Ollama icon
# On Mac/Linux: Run 'ollama serve' in background
```

### Step 2: Start the API Server

```bash
start_api.bat
```

Or manually:
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

✅ **No more "Missing API key" errors!**

### Step 3: Start the Frontend

```bash
cd frontend
npm run dev
```

### Step 4: Test the Application

1. Go to http://localhost:5173
2. Click Submit page
3. Enter test data
4. Click "Submit for Evaluation"
5. The LLM stage will now use **local Llama 3.1** instead of Gemini

---

## How It Works Now

### Evaluation Pipeline with Ollama:

```
User Submission
    ↓
Stage 1: Coursera Verification (5-10 sec)
    ↓
Stage 2: LinkedIn Quick Match (5-10 sec)
    ↓
Stage 3: Ollama Llama 3.1 (Local LLM) (30-60 sec)
    ↓
Result: PASS / FAIL / INVALID
```

**Note:** The LLM stage is now slower (30-60 seconds) because it runs locally on your machine, but it's **completely free** and **private**!

---

## Performance Considerations

### Local LLM (Ollama):
- ✅ **Free** - No API costs
- ✅ **Private** - Data stays on your machine
- ✅ **Reliable** - No API rate limits
- ⚠️ **Slower** - 30-60 seconds per evaluation
- ⚠️ **Requires** - Good CPU/GPU and 8GB+ RAM

### System Requirements:
- **Minimum**: 8GB RAM, modern CPU
- **Recommended**: 16GB RAM, GPU with 6GB+ VRAM
- **Storage**: ~5GB for the model

### Tips for Better Performance:
1. Close unnecessary applications
2. Use GPU if available (Ollama auto-detects)
3. Run on a machine with good cooling (model uses CPU/GPU intensively)

---

## Troubleshooting

### Issue 1: "Ollama request failed"

**Solution:**
```bash
# Check if Ollama is running
ollama list

# If not running, start it
ollama serve
```

### Issue 2: Model not found

**Solution:**
```bash
# Pull the model again
ollama pull llama3.1:8b
```

### Issue 3: Very slow responses

**Possible causes:**
- CPU is being used instead of GPU
- System is under heavy load
- Model needs to warm up (first request is slower)

**Solutions:**
- Close other applications
- Wait for first request to complete (caches model)
- Check if GPU is being used: Model loads faster with GPU

### Issue 4: Connection refused on port 11434

**Solution:**
- Restart Ollama: `ollama serve`
- Check if another service is using port 11434
- Windows: Check if Ollama service is running in Services

---

## Alternative Models

You can use other models if llama3.1:8b is too slow:

**Faster (smaller) models:**
```bash
ollama pull llama3.1:3b  # Faster, less accurate
```

**Better (larger) models:**
```bash
ollama pull llama3.1:70b  # More accurate, much slower
```

**To change the model**, edit `utils/context_project_match.py`:
```python
MODEL_NAME = "llama3.1:3b"  # Change this line
```

---

## Comparison: Ollama vs Gemini

| Feature | Ollama (Local) | Gemini (API) |
|---------|----------------|--------------|
| **Cost** | Free | Pay per request |
| **Privacy** | Fully private | Data sent to Google |
| **Speed** | 30-60 sec | 5-10 sec |
| **Reliability** | Depends on your machine | Depends on API |
| **Setup** | Requires installation | Just API key |
| **Internet** | Not required | Required |

---

## Quick Commands Reference

```bash
# Install Ollama
Windows: Download from ollama.com
Mac: brew install ollama
Linux: curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.1:8b

# List models
ollama list

# Run model interactively
ollama run llama3.1:8b

# Start Ollama server
ollama serve

# Test API
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Hello",
  "stream": false
}'
```

---

## Updated Documentation

The following docs have been updated to reflect Ollama usage:

- ✅ `COMPLETE_SYSTEM_GUIDE.md` - Updated LLM section
- ✅ `STARTUP_GUIDE.md` - Added Ollama setup
- ✅ Requirements and dependencies
- ✅ Environment configuration

---

## Summary

**What you need to do:**

1. ✅ Install Ollama
2. ✅ Pull llama3.1:8b model
3. ✅ Verify Ollama is running
4. ✅ Start API server (no more errors!)
5. ✅ Start frontend
6. ✅ Test the application

**That's it!** No API keys, no external dependencies, everything runs locally! 🚀

---

## Need Help?

If you encounter issues:
1. Make sure Ollama is installed and running
2. Verify the model is downloaded: `ollama list`
3. Test the API endpoint: `curl http://localhost:11434/api/generate ...`
4. Check API server logs for errors
5. Ensure port 11434 is not blocked by firewall

The system should now work perfectly with local LLM! 🎉
