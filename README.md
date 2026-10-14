# BB Bloom 🍼

A baby tracker for sleeps, feeds, diapers, symptoms and medication, shared between caregivers.

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, pytest, Ruff, managed with [uv](https://docs.astral.sh/uv/)
- **Frontend:** React 19, TypeScript, Vite, TanStack Query, React Router, and an API client typed from the backend's OpenAPI schema

## Quick start

```bash
docker compose up --build
```

| What | Where |
|---|---|
| App | http://localhost:5173 |
| Interactive API docs (try every endpoint) | http://localhost:8000/docs |
| Postgres | `localhost:5432`, user/password `postgres`, db `bb_bloom` |

Migrations run automatically when the API container starts. Create an account in the app, add a baby, and start logging.

### Running pieces without Docker

You only need Postgres from Docker (`docker compose up db`), then:

```bash
# backend
cd backend
cp .env.example .env
uv sync                         # like `bundle install`; creates .venv
uv run alembic upgrade head     # like `rails db:migrate`
uv run fastapi dev app/main.py  # like `rails s`, with auto-reload

# frontend (another terminal)
cd frontend
npm install
npm run dev
```

## Project layout

```
backend/
  app/
    main.py          app setup, CORS, router registration  (≈ config/routes.rb + application.rb)
    config.py        settings from env vars                (≈ config/*.yml + ENV)
    db.py            engine, session, Base, timestamps
    deps.py          auth + "can this user see this baby?" (≈ before_action filters)
    security.py      password hashing and JWT tokens       (≈ has_secure_password)
    models/          SQLAlchemy models                     (≈ app/models)
    schemas/         Pydantic request/response shapes      (≈ strong params + serializers)
    routers/         endpoints                             (≈ controllers)
  alembic/versions/  migrations                            (≈ db/migrate)
  tests/             pytest                                (≈ spec/)
frontend/
  src/api/           typed client + generated schema.d.ts
  src/pages/         Login, Babies, Baby (dashboard)
  src/components/    LogSheet (the form for each event type)
  src/lib/           time formatting, event labels
```

## Rails → Python cheat sheet

| Rails | Here |
|---|---|
| `bundle install` / `bundle add x` | `uv sync` / `uv add x` (`uv add --dev x` for dev-only) |
| `rails console` | `uv run ipython`, then `from app.models import *` |
| `rails db:migrate` / `rollback` | `uv run alembic upgrade head` / `uv run alembic downgrade -1` |
| `rails g migration ...` | change a model, then `uv run alembic revision --autogenerate -m "..."`, and **read the generated file** |
| `rspec` | `uv run pytest` (`-k name` filters, `-x` stops at first failure) |
| `rubocop -a` | `uv run ruff check --fix . && uv run ruff format .` |
| `Model.where(...).order(...)` | `db.scalars(select(Model).where(...).order_by(...))` |
| `record.save!` | `db.add(record); db.commit()` |
| `dependent: :destroy` | `relationship(cascade="all, delete-orphan")` |
| `validates :x, ...` | Pydantic `Field(...)`, `@field_validator` |

Inside Docker, prefix commands with the container: `docker compose exec api uv run pytest`.

## How the pieces fit

**A request, end to end.** The React app calls `/api/babies/1/events`. Vite proxies `/api` to FastAPI. FastAPI runs the dependencies the endpoint asks for (`DbSession`, `CurrentUser`, `AccessibleBaby`), validates the body against a Pydantic schema, and the endpoint saves a SQLAlchemy model. The response is filtered through the `response_model` schema, so only declared fields leave the server.

**Event metadata.** Each event type has its own Pydantic metadata model (`app/schemas/event.py`), combined in a *discriminated union* on `event_type`. A diaper with `{"type": "soup"}` is a 422, and unknown keys are rejected. The database column stays a flexible JSONB. When you add a field to a metadata type, it's a schema change only, with no migration.

**`ended_at` = NULL** means "still running" for sleep and feeding (shown as a live timer with a Stop button) and "instantaneous" for the other types. `DURATION_EVENT_TYPES` in `app/models/enums.py` is the single place that defines this.

**Time zones.** Every timestamp column is `timestamptz`, and the API rejects datetimes without an offset (`AwareDatetime`). The browser sends UTC (`toISOString()`) and converts to local time only for display.

**Types shared with the frontend.** When the API changes, run the API and then `npm run gen:api` in `frontend/`. That regenerates `src/api/schema.d.ts`, and `npm run build` will flag every place in the UI the change breaks.

### Gotchas already handled (worth reading)

- `metadata` is a reserved attribute name on SQLAlchemy models, so `Event.details` maps to the `metadata` column. The API schema still calls it `metadata` (see `models/event.py` and `EventRead`).
- In Python, `0` is falsy. Check `is not None` rather than truthiness for values like `quantity_ml: 0`.
- Inaccessible babies return 404 rather than 403, so ids of other families' babies aren't revealed.
- Tests use a real Postgres database (JSONB) with a rolled-back transaction per test, so `db.commit()` in app code is safe inside tests.

## Status

**Built:** all six tables with constraints and the initial migration; sign up / log in / me; create and list babies (creator becomes owner); events: create, list (filter by type, time range, ongoing), get, update (stop a timer), delete; 16 API tests; a mobile-first dashboard with live timers, "last fed / changed / slept" summary, quick-log sheets and today's timeline; dark mode; GitHub Actions CI.

**Next, for practice** (the models and tables already exist):

1. **Invite a caregiver.** `POST /babies/{id}/caregivers` (owner only) creates a `Caregiving` with `accepted_at = NULL`; an accept endpoint sets it. `deps.get_baby_for_user` already ignores unaccepted invites.
2. **Milestones.** CRUD under `/babies/{id}/milestones`. Copy the events router structure; start with `photo_url` as a plain URL before tackling uploads.
3. **Reminders.** CRUD with a Pydantic validator mirroring the DB check constraints (each `schedule_kind` needs its own field), then a `GET /babies/{id}/reminders/due` that computes the next due time (e.g. last feeding + `relative_interval_minutes`).
4. **Notification preferences.** `PATCH /auth/me` validated by a Pydantic model for the JSONB.
5. **Stats.** Daily totals (sleep hours, ml fed, diaper count) with SQL aggregation via `func.sum` / `func.count` and `group_by`.
6. **Edit events in the UI.** The PATCH endpoint already supports it.

Each one follows the same loop: model (if needed) → migration → schema → router → tests → `npm run gen:api` → UI.
