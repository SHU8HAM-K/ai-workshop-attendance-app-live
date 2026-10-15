# Attendance integration contract

The browser uses relative `/api/v1` URLs and always includes credentials. In development, Vite proxies `/api` to `http://backend:8000` inside Compose. In production, FastAPI serves the built frontend from the same origin.

The backend must mount attendance business routes under `/api/v1` and include them in the authenticated router group. The shared expected resources are `workshops`, `students`, `sessions`, and `attendance`. Public routes are limited to health and authentication. An unauthenticated request to `/api/v1/workshops` should return `401`.

PostgreSQL is selected in the development stack through `MYAPP_DATABASE_URL=postgresql+asyncpg://...`. Attendance tables must be created through Alembic, not application startup. The backend container starts only after the database health check succeeds.

Google OAuth starts at `/api/v1/auth/google/login` and returns to `/api/v1/auth/google/callback`. For local Compose, the callback registered in Google Cloud must be `http://localhost:5173/api/v1/auth/google/callback`, unless `MYAPP_WEB_HOST_PORT` is changed. The frontend origin is intentional because Vite proxies the callback to FastAPI and keeps the session cookie same-origin.

Run static verification from the repository root:

```powershell
python scripts/verify_attendance_integration.py
```

After starting the development stack, run live checks:

```powershell
python scripts/verify_attendance_integration.py --live
```

The live check expects the protected workshops endpoint to return `401` without a session. A real browser sign-in is still required to validate Google's consent redirect and the authenticated `200` response because that step depends on project credentials and a registered callback URI.
