"""The FastAPI application: `uv run fastapi dev` (or uvicorn app.main:app) starts it.

Interactive API docs: http://localhost:8000/docs
"""

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, babies, events

app = FastAPI(title="BB Bloom API", version="0.1.0")

# Lets the browser call the API from the React dev server's origin.
# (Vite also proxies /api in development, so this mainly matters if you
# point the frontend straight at the API.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Everything lives under /api, the same prefix the frontend uses.
api = APIRouter(prefix="/api")
api.include_router(auth.router)
api.include_router(babies.router)
api.include_router(events.router)


@api.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api)
