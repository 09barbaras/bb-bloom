from fastapi import APIRouter, FastAPI

app = FastAPI(title="BB Bloom API")

api = APIRouter(prefix="/api")


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api)
