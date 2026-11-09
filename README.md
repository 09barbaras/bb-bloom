# BB Bloom 🍼

A baby tracker for sleeps, feeds, diapers, symptoms and medication, shared between caregivers.

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, pytest, Ruff, managed with [uv](https://docs.astral.sh/uv/)
- **Frontend:** React 19, TypeScript, Vite, TanStack Query, React Router, and an API client typed from the backend's OpenAPI schema

## How the pieces fit

```
browser → frontend (Vite, :5173) ──/api/*──▶ backend (FastAPI, :8000) ──▶ Postgres (Docker, :5432)
```

The frontend dev server forwards every `/api` request to the backend, so the browser only ever talks to `localhost:5173`.

## First-time setup

Do this once on a new machine. Run the commands from the repo root unless a step says otherwise.

**1. Install the tools**

```bash
brew install uv node
```

Also install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and open it once, so the Docker engine is running.

**2. Start the database**

```bash
docker compose up -d --wait
```

This creates two databases: `bb_bloom` (development) and `bb_bloom_test` (tests).

**3. Set up the backend**

```bash
cd backend
cp .env.example .env        # local settings; the defaults match the Docker database
uv sync                     # creates .venv and installs dependencies
uv run alembic upgrade head # creates the tables in the dev database
cd ..
```

**4. Set up the frontend**

```bash
cd frontend
npm install
cd ..
```

**5. Check that everything works**

```bash
cd backend && uv run pytest   # should pass
```

Then follow "Daily development" below and open http://localhost:5173. The page should say `API: ok`.

## Daily development

Docker Desktop must be running. Then open **three terminal tabs**:

| Tab | Directory | Command | Open |
|---|---|---|---|
| Database | repo root | `docker compose up -d` | `localhost:5432` |
| Backend | `backend/` | `uv run fastapi dev app/main.py` | http://localhost:8000/docs |
| Frontend | `frontend/` | `npm run dev` | http://localhost:5173 |

The database tab only needs a command the first time each day. Both servers reload automatically when you save a file.

To stop: `Ctrl+C` in the backend and frontend tabs. Run `docker compose down` to stop the database (your data is kept).

## When to run what

| Situation | Run | From |
|---|---|---|
| Pulled new code, or switched branches | `uv sync`, `uv run alembic upgrade head` | `backend/` |
| Pulled new code and `package.json` changed | `npm install` | `frontend/` |
| Added or changed a database model | `uv run alembic revision --autogenerate -m "describe it"`, **read the generated file**, then `uv run alembic upgrade head` | `backend/` |
| Migration was wrong | `uv run alembic downgrade -1`, fix it, apply again | `backend/` |
| Added a backend dependency | `uv add <package>` (`uv add --dev <package>` for dev-only) | `backend/` |
| Added a frontend dependency | `npm install <package>` | `frontend/` |
| Before committing (backend) | `uv run ruff check --fix . && uv run ruff format . && uv run pytest` | `backend/` |
| Before committing (frontend) | `npm run lint && npm run build` | `frontend/` |
| Want a completely empty database | `docker compose down -v`, then `docker compose up -d --wait` and `uv run alembic upgrade head` (**deletes all data**) | repo root, then `backend/` |

## Frontend layout

- `src/router.tsx`: the list of routes. Add new pages here.
- `src/pages/`: one component per screen. `src/components/`: shared pieces such as the layout.
- `src/api/client.ts`: `api.get` / `api.post` for every backend call (relative `/api/...` URLs, errors become `ApiError`).
- `src/api/*.ts`: one hook per endpoint, built on TanStack Query (see `health.ts`).

## Continuous integration

GitHub Actions ([.github/workflows/ci.yml](.github/workflows/ci.yml)) runs on every pull request and every push to `main`:

- **backend:** Ruff lint and format check, `alembic upgrade head` and `pytest`, against a throwaway Postgres.
- **frontend:** `npm run lint` and `npm run build`.

These are the same commands as the "before committing" rows above, so if they pass locally they should pass in CI.

## Troubleshooting

- **`API: unreachable` on the page:** the backend isn't running. Start it in its own tab.
- **`connection refused` on port 5432:** the database isn't running. Open Docker Desktop and run `docker compose up -d`.
- **`relation ... does not exist`:** migrations haven't been applied. Run `uv run alembic upgrade head` in `backend/`.
- **Port already in use:** another copy of the server is still running. Stop it with `Ctrl+C`, or find it with `lsof -i :8000`.

## Git workflow

One short-lived branch per ticket, named like `feat/auth-login-api` or `chore/db-alembic`, merged into `main` through a pull request. Keep `main` working.
