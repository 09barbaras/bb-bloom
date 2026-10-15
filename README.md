# BB Bloom 🍼

A baby tracker for sleeps, feeds, diapers, symptoms and medication, shared between caregivers.

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, pytest, Ruff, managed with [uv](https://docs.astral.sh/uv/)
- **Frontend:** React 19, TypeScript, Vite, TanStack Query, React Router, and an API client typed from the backend's OpenAPI schema

## Running locally

Install the tools once: `brew install uv node`

```bash
# backend → http://localhost:8000/docs
cd backend
uv sync
uv run fastapi dev app/main.py
```

```bash
# frontend → http://localhost:5173
cd frontend
npm install
npm run dev
```
