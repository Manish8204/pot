# Setup Instructions for "Explain My Failure"

## Prerequisites
- Python 3.8+ installed
- OpenRouter API key (get one at https://openrouter.ai/)

## Step 1: Configure Environment Variables

1. Navigate to the `backend` folder
2. Open `.env` file and replace `your_key_here` with your actual OpenRouter API key:
   ```
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
   OPENROUTER_MODEL=mistralai/mixtral-8x7b-instruct
   ```

## Step 2: Install Dependencies

```powershell
pip install -r backend/requirements.txt
```

## Step 3: Start the Backend API

Open a PowerShell terminal and run:

```powershell
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Test the Backend

Open a **new** PowerShell terminal and test:

**Health check:**
```powershell
curl http://localhost:8000/health
```

**Test analysis endpoint:**
```powershell
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{\"description\":\"I failed an interview after cramming LeetCode for 2 weeks. I could solve medium problems but froze during the actual interview when asked about system design.\"}'
```

Or use PowerShell's `Invoke-RestMethod`:
```powershell
$body = @{
    description = "I failed an interview after cramming LeetCode for 2 weeks. I could solve medium problems but froze during the actual interview when asked about system design."
    effort_level = 8
    preparation_hours = 40
    confidence_before = 7
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/analyze -Method POST -Body $body -ContentType "application/json"
```

## Step 5: Start the Frontend

Open **another** PowerShell terminal and run:

```powershell
cd frontend
python -m http.server 4173
```

## Step 6: Access the Application

Open your browser and visit:
```
http://localhost:4173
```

The frontend will automatically connect to the backend at `http://localhost:8000`.

## Troubleshooting

### "Failed to fetch" error
- Make sure the backend is running on port 8000
- Check that `OPENROUTER_API_KEY` is set correctly in `backend/.env`
- Verify CORS is enabled (it should be with `allow_origins=["*"]`)

### Backend won't start
- Check that all dependencies are installed: `pip install -r backend/requirements.txt`
- Verify Python version: `python --version` (should be 3.8+)
- Check if port 8000 is already in use

### API returns errors
- Verify your OpenRouter API key is valid
- Check backend logs for detailed error messages
- Ensure the model name is correct (default: `mistralai/mixtral-8x7b-instruct`)
