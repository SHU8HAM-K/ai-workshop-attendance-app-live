# AI Workshop Attendance App — Session Chat Summary

## Participant

- **Name:** Shubham Kumar
- **Organization:** Schoolnet India Limited
- **Project:** AI Workshop Attendance App
- **Dashboard:** Schoolnet Workshop Attendance Dashboard

## Project objective

Build a browser-based dashboard for managing workshops, sessions, students, attendance, participation time, and downloadable attendance reports.

## Requirements discussed

- Provide a secure administrator sign-in flow, including a development login for local use.
- Create and manage workshops and their sessions.
- Add students to workshops.
- Mark each student as Present, Absent, or Unmarked.
- Record participation time in minutes.
- Display useful attendance totals and summaries.
- Export attendance reports as CSV files.
- Store application data persistently in SQLite.
- Provide a responsive interface that works in a desktop browser.
- Run locally on Windows using Git Bash, Make, Python, Uvicorn, and Vite.

## Work completed during the session

1. Reviewed and completed the FastAPI backend and React/Vite frontend.
2. Implemented workshop, session, student, attendance, participation-time, totals, and CSV-export workflows.
3. Added backend validation and aligned the frontend with the API contract.
4. Created a Windows-friendly `Makefile` workflow:
   - `make venv` creates `.venv` and installs Python and frontend dependencies.
   - `make run-dev` starts the FastAPI API and Vite development server.
5. Fixed the development sign-in Internal Server Error by correcting the backend working directory and database/migration path behavior.
6. Verified the development login and current-user endpoints.
7. Ran backend tests, frontend tests, type/lint checks, integration checks, and a production build.
8. Committed the completed application and pushed it to GitHub.

## How to run the project

Open Git Bash in the project directory and run:

```bash
make venv
make run-dev
```

Open the frontend URL printed in the terminal, normally:

```text
http://localhost:5173
```

The FastAPI service normally runs at:

```text
http://127.0.0.1:8000
```

## Verification results

- Backend test suite: **61 tests passed**
- Frontend test suite: **13 tests passed**
- Integration checks: **21 checks passed**
- Production frontend build: **passed**
- Development sign-in: **verified successfully**

## Repository

[AI Workshop Attendance App on GitHub](https://github.com/SHU8HAM-K/ai-workshop-attendance-app-live)

## Time summary

- **Estimated time without AI:** 24 hours
- **Actual time taken with AI:** 4 hours
- **Estimated time saved:** 20 hours

## Final result

The application is complete, runs locally through the Makefile workflow, supports the required attendance-management features, and is available in the GitHub repository.
