# Setup local

## Backend

```powershell
cd apps\api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

Edita `apps/api/.env` antes de usar IA real:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.1-8b-instant
MOCK_MODE=false
DATABASE_URL=sqlite:///./agentops.db
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
MAX_OUTPUT_TOKENS=1200
```

## Frontend

```powershell
cd apps\web
npm install
copy .env.example .env.local
npm run dev
```

## URLs

```text
Frontend: http://localhost:3000
Backend: http://localhost:8000
Health: http://localhost:8000/health
```
