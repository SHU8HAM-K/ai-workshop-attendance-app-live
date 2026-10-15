# Schoolnet Workshop Attendance

An authenticated workshop operations app for creating workshops and sessions,
enrolling students, recording present/absent attendance and participation time,
and exporting a session register as CSV. It uses a layered FastAPI backend, a
React SPA, Postgres, and Docker for development and production.

For a zero-configuration local start on Windows, open Git Bash in the project
directory and run:

```bash
make venv
make run-dev
```

`make venv` creates `.venv`, installs the Python and Node dependencies, and
creates `.env` from the example when needed. `make run-dev` applies the SQLite
migrations, starts FastAPI on port 8000, and starts Vite on port 5173. Press
`Ctrl+C` to stop both servers.

Open `http://localhost:5173` and use the development sign-in button. Create a
workshop, add at least one session and student, then use the Attendance tab to
save or export the register.

`make dev` gives you Vite with hot reload on :5173, the API on :8000, interactive
docs at :8000/docs and a debugger port on :5678. `make help` lists everything.

---

## What's in the box

| | |
|---|---|
| **Backend** | FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic v2, structlog |
| **Frontend** | React 19, TypeScript (strict), Vite 7, Tailwind 4, TanStack Query 5, Zustand 5, React Router |
| **Database** | Postgres 17 in compose; in-memory SQLite for tests |
| **Sign-in** | Google sign-in (OpenID Connect), a one-click dev login, signed session cookie |
| **PWA** | Installable, offline app shell, auto-updating service worker (`vite-plugin-pwa`) |
| **Storage** | S3 adapter, LocalStack profile for local AWS mocks |
| **Quality** | ruff, mypy `strict`, pytest (4 tiers, coverage ratchet), vitest + Testing Library, a CI-enforced dependency-rule check |
| **Deploy** | One image: the SPA is built and served by FastAPI. No nginx, no CORS, one origin |

Everything is wired and verified — `make check` is green on a fresh clone.

---

## Sign-in

Every page and every `/api/v1` route except `/auth/*` needs a signed-in user.
A fresh clone shows a "Sign in as the dev user" button, so nothing needs setting up.

To turn on Google:

1. In Google Cloud console, create an OAuth client of type "Web application".
2. Add the redirect URI `<MYAPP_PUBLIC_URL>/api/v1/auth/google/callback`.
   In dev that is `http://localhost:5173/api/v1/auth/google/callback`.
3. Set `MYAPP_GOOGLE_CLIENT_ID` and `MYAPP_GOOGLE_CLIENT_SECRET` in `.env`.

Set `MYAPP_ALLOWED_EMAIL_DOMAINS='["example.com"]'` to let only one domain in.
In prod, set `MYAPP_SESSION_SECRET` to a long random string. The app refuses to
start sign-in with the dev secret or the dev login in staging and prod.

## PWA

`npm run build` writes a web app manifest and a service worker. The built app
can be installed from the browser and opens offline. The dev server has no
service worker, so hot reload is not affected. Replace the placeholder icons in
`frontend/public/` (made by `scripts/make_icons.py`) and the name and colours in
`frontend/vite.config.ts`.

---

## The one-image deploy

In **development** Vite serves the SPA on :5173 and proxies `/api` to FastAPI on
:8000. In **production** the SPA is built to static files and served by FastAPI
itself, so a deployment is a single container on a single port.

That means: no CORS in production, no separate static host, no second thing to
deploy, and deep links like `/files` survive a refresh because FastAPI's
catch-all returns `index.html`. Because the frontend always calls a relative
`/api/v1/...`, the same code works in both.

```bash
make up      # builds the production image and runs it — http://localhost:8000
```

Run that before you ship. It is the only configuration that exercises the path
where FastAPI serves the SPA.

---

## Layout

```
backend/src/myapp/
  domain/         business entities and rules — imports nothing external
  ports/          abstract interfaces (ABCs) — imports domain only
  adapters/       concrete implementations — SQLAlchemy, S3, and their fakes
  services/       one method per use case — takes ports, never adapters
  entrypoints/    HTTP routes, schemas, middleware — thin
  bootstrap.py    the composition root: the only file that picks adapters
  config/         settings, database engine, logging
backend/tests/    unit / service / integration / e2e — one per layer
frontend/src/
  features/       one folder per feature: api, hooks, page, tests
  components/     shared UI
  stores/         Zustand — client-only state
  lib/api.ts      the only place that talks to the network
```

**Dependencies point inward, toward the domain.** `services` may not import
`adapters`; `domain` may not import anything external at all. This is enforced —
`scripts/check_dependency_rule.py` runs in `make lint` and in CI, and fails the
build with the exact file and line.

---

## Documentation

Read in this order:

| Doc | Read it when |
|---|---|
| [docs/architecture.md](docs/architecture.md) | First. What each layer is for, and how to decide where code goes |
| [docs/adding-a-feature.md](docs/adding-a-feature.md) | Building anything. A step-by-step recipe following one real feature end to end |
| [docs/backend.md](docs/backend.md) | Writing backend code. The normative checklist — layering, async, database, logging |
| [docs/frontend.md](docs/frontend.md) | Writing frontend code. TanStack Query vs Zustand, components, file layout |
| [docs/testing.md](docs/testing.md) | Writing tests. Which of the four tiers a test belongs in |
| [docs/debugging.md](docs/debugging.md) | Something is broken. Debugger, ports, logs, the usual traps |
| [docs/performance.md](docs/performance.md) | Something is slow, or you're about to launch. N+1, profiling, benchmarks, load tests |
| [docs/database.md](docs/database.md) | Deciding what storage you need. Postgres is the default, not a requirement — SQLite is one env var, and no-database is a documented removal |
| [docs/blocks.md](docs/blocks.md) | Adding auth, RBAC, an LLM, notifications — the copy-paste block convention |

Guidelines are enforced, not just written down: `make lint` runs the dependency
rule and the file-length check alongside ruff/mypy/tsc, and **`/review`** in
Claude Code reviews a diff against `docs/backend.md` and `docs/frontend.md` for
the things a script can't see — N+1 queries, rules that drifted out of the
domain, server state copied into Zustand, tests at the wrong tier.

[CLAUDE.md](CLAUDE.md) holds the same rules in the form coding agents need.

---

## The example feature

The template ships with a working **Notes** feature — create, list, edit,
archive, restore, delete — implemented all the way through every layer, plus a
file upload demonstrating a non-database adapter. It exists to be copied and then
deleted.

It is the executable specification for the architecture: a rich domain entity
with rules on it, a port, two adapters (real and fake), a service, a route, a
Pydantic schema, a Query hook, a Zustand store, and tests at all four tiers.
[docs/adding-a-feature.md](docs/adding-a-feature.md) walks through it file by
file and lists exactly what to delete when you're done.

---

## Common commands

```bash
make dev                       # dev stack with hot reload
make up-aws                    # dev stack + LocalStack (S3/SQS/SNS/Secrets Manager)
make up                        # production image locally
make check                     # lint + typecheck + dependency rule + all tests
make test-be / make test-fe    # one side only
make migration m="add orders"  # autogenerate a migration (then read it)
make migrate                   # apply migrations
make format                    # auto-fix
make clean                     # remove artefacts, caches and volumes
```

Local development without Docker also works — `make install`, then
`cd backend && uv run myapp` and `cd frontend && npm run dev`. It defaults to a
SQLite file so nothing else needs to be running.
