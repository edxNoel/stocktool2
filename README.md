# AI Stock Analyzer (Basic)

Minimal monorepo containing:
- FastAPI backend served as a Vercel Serverless Function (`api/index.py`)
- Next.js frontend that calls `/api/analyze` (no external backend URL)
- `vercel.json` and `requirements.txt` for Vercel deployment

## Local dev
- Backend: `uvicorn api.index:app --reload --port 8000`
- Frontend: `cd frontend && npm install && npm run dev`

## Deploy to Vercel
1. Push this repository to GitHub.
2. Create a new project in Vercel and connect the repo.
3. Add environment variables (optional):
   - `OPENAI_API_KEY` (if you want AI summarization)
4. Deploy. Frontend calls `/api/analyze`.
