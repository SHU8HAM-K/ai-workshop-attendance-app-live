#!/usr/bin/env python3
"""Verify the frontend, FastAPI, OAuth, and Postgres integration contract.

The static checks need no services or third-party packages. Pass ``--live``
after starting the dev compose stack to also probe the browser-facing Vite URL
and the backend health/auth endpoints.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def read(relative: str) -> str:
    path = ROOT / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


def contains(relative: str, pattern: str, detail: str) -> Check:
    content = read(relative)
    return Check(relative, bool(content and re.search(pattern, content, re.MULTILINE)), detail)


def static_checks() -> list[Check]:
    checks = [
        contains("frontend/src/lib/api.ts", r'BASE\s*=\s*["\']/api/v1["\']', "API base is /api/v1"),
        contains("frontend/src/lib/api.ts", r'credentials:\s*["\']include["\']', "session cookie is sent"),
        contains("frontend/vite.config.ts", r'["\']/api["\']\s*:\s*\{[^}]*target:\s*apiTarget', "Vite proxies /api"),
        contains("docker-compose.dev.yml", r'VITE_API_PROXY:\s*http://backend:8000', "frontend targets backend service"),
        contains("docker-compose.dev.yml", r'MYAPP_DATABASE_URL:\s*postgresql\+asyncpg://', "backend uses async Postgres"),
        contains("docker-compose.dev.yml", r'MYAPP_PUBLIC_URL:\s*http://localhost:', "OAuth callback uses browser origin"),
        contains("backend/src/myapp/config/settings.py", r'google_client_id:\s*str', "Google client ID setting exists"),
        contains("backend/src/myapp/config/settings.py", r'google_client_secret:\s*str', "Google client secret setting exists"),
        contains("backend/src/myapp/entrypoints/api/routes/auth.py", r'@router\.get\("/\{provider\}/callback"', "OIDC callback route exists"),
        contains("backend/src/myapp/entrypoints/api/router.py", r'Depends\(auth\.current_user\)', "business routes have auth gate"),
    ]

    frontend = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in (ROOT / "frontend/src").rglob("*.ts*")
    )
    backend = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in (ROOT / "backend/src").rglob("*.py")
    )
    migrations = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in (ROOT / "backend/alembic/versions").glob("*.py")
    )
    for resource in ("workshop", "student", "session", "attendance"):
        checks.append(Check(f"frontend:{resource}", resource in frontend.lower(), f"frontend references {resource}"))
        checks.append(Check(f"backend:{resource}", resource in backend.lower(), f"backend implements {resource}"))
    checks.append(
        Check(
            "migrations:attendance",
            "attendance" in migrations.lower() and "student" in migrations.lower(),
            "Alembic migration creates attendance domain tables",
        )
    )

    # Cross-layer payload compatibility. These fields are the product contract,
    # not merely evidence that similarly named modules exist on both sides.
    schema = read("backend/src/myapp/entrypoints/api/schemas/attendance.py").lower()
    routes = read("backend/src/myapp/entrypoints/api/routes/attendance.py").lower()
    frontend_types = read("frontend/src/features/workshops/types.ts").lower()
    shared_fields = (
        "title",
        "topic",
        "facilitator_name",
        "facilitator_email",
        "location",
        "status",
        "student_count",
        "session_count",
        "student_id",
        "institution",
        "minutes_attended",
    )
    missing_backend = [field for field in shared_fields if field in frontend_types and field not in schema]
    checks.append(
        Check(
            "contract:shared-fields",
            not missing_backend,
            "backend schema contains frontend fields"
            + (f"; missing {', '.join(missing_backend)}" if missing_backend else ""),
        )
    )
    frontend_wraps_sheet = "interface attendancesheet" in frontend_types
    backend_wraps_sheet = "attendancesheet" in schema and "response_model=attendancesheet" in routes
    checks.append(
        Check(
            "contract:attendance-envelope",
            frontend_wraps_sheet == backend_wraps_sheet,
            "frontend and backend agree whether attendance is a sheet envelope",
        )
    )
    return checks


def get(url: str) -> tuple[int, str, dict[str, str]]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read().decode("utf-8", "replace"), dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace"), dict(exc.headers)


def live_checks(web_url: str, api_url: str) -> list[Check]:
    checks: list[Check] = []
    probes = [
        ("Vite frontend", f"{web_url}/", {200}),
        ("Backend health", f"{api_url}/health", {200}),
        ("Auth providers through Vite", f"{web_url}/api/v1/auth/providers", {200}),
        ("Protected API through Vite", f"{web_url}/api/v1/workshops", {401}),
    ]
    for name, url, expected in probes:
        try:
            status, body, _ = get(url)
            checks.append(Check(name, status in expected, f"{url} returned {status}; expected {sorted(expected)}; body={body[:120]!r}"))
        except (OSError, TimeoutError) as exc:
            checks.append(Check(name, False, f"{url} unavailable: {exc}"))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="probe running dev services")
    parser.add_argument("--web-url", default="http://localhost:5173")
    parser.add_argument("--api-url", default="http://localhost:8000")
    args = parser.parse_args()

    checks = static_checks()
    if args.live:
        checks.extend(live_checks(args.web_url.rstrip("/"), args.api_url.rstrip("/")))
    for check in checks:
        print(f"[{'PASS' if check.ok else 'FAIL'}] {check.name}: {check.detail}")
    failed = sum(not check.ok for check in checks)
    print(f"\n{len(checks) - failed}/{len(checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
