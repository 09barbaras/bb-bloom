# Python 3.13 with uv preinstalled
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Keep the virtualenv outside /app so mounting the source code in
# docker-compose doesn't hide it.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install dependencies first (cached unless pyproject.toml/uv.lock change),
# like copying the Gemfile before the app in a Rails Dockerfile.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
