# Explain My Failure — Brutally Honest AI Reflection Agent

An end-to-end FastAPI + Pydantic AI application that performs structured, unsweetened root-cause analysis of personal failures and returns a validated plan you can act on immediately.

## Stack
- Backend: FastAPI, Pydantic AI, OpenRouter (Mixtral by default), Loguru
- Frontend: Static HTML/CSS/JS (dark, minimal, polished)
- Deployment: Render/Railway/Fly.io for API, Vercel/Netlify for frontend

## API
Run locally:
```bash
cd backend
python -m venv .venv && .venv/Scripts/activate  # Windows
pip install -r requirements.txt
set OPENROUTER_API_KEY=your_key
uvicorn app.main:app --reload --port 8000
```

POST `http://localhost:8000/analyze`
```json
{
  "description": "I bombed a systems interview after cramming all week...",
  "effort_level": 6,
  "preparation_hours": 12,
  "confidence_before": 7
}
```
Returns a `FailureAnalysis` payload with root cause, patterns, hard truth, corrective actions, 7-day plan, and warnings.

Health check: `GET /health`

## Frontend
Serve locally:
```bash
cd frontend
python -m http.server 4173
```
Visit http://localhost:4173 and ensure `API_BASE` points to your backend (defaults to `http://localhost:8000`).

## Deployment
- Backend (Render example):
  - Create a new Web Service from this repo
  - Build command: `pip install -r backend/requirements.txt`
  - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - Root directory: `backend`
  - Environment: set `OPENROUTER_API_KEY`, optionally `OPENROUTER_MODEL`
- Frontend (Vercel/Netlify):
  - Deploy `frontend` as a static site
  - Set `API_BASE` environment variable to your backend URL if needed

## Notes
- The agent uses Pydantic AI with retries and strict validation against `FailureAnalysis`
- All cross-origin requests are allowed by default for demo; tighten for production
