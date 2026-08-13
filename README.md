# RepairLink

**RepairLink** is a single-user RESTful maintenance reporting and tracking system for off-campus students. It allows a student to report campus or residence problems, receive a reference number, track progress, reopen unresolved issues, and provide feedback after resolution.

## Project purpose

Maintenance problems are often reported through informal messages that are difficult to track. RepairLink provides one consistent service for recording problems such as electrical faults, plumbing issues, damaged furniture, security concerns, internet failures, and cleaning problems.

The project is implemented with **Python, FastAPI, SQLAlchemy, SQLite, and Pytest**. The API automatically exposes interactive documentation at `http://127.0.0.1:8000/docs`.

## Main workflow

```text
Submit report → Receive reference → Track status → Resolution → Feedback or reopen
```

## Features

| Feature | Description |
|---|---|
| Report submission | Captures location, category, description, urgency, safety risk, and affected people |
| Priority calculation | Calculates a transparent priority score and label |
| Duplicate detection | Prevents similar open reports at the same location within 24 hours |
| Status workflow | Supports submitted, received, assigned, in-progress, resolved, and reopened states |
| History | Records every status change and note |
| Feedback | Allows a student to rate a resolved report |
| Dashboard | Summarises total, open, resolved, reopened, and rated reports |
| Validation | Returns structured errors for invalid input and missing records |

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/reports` | Create a maintenance report |
| `GET` | `/api/reports` | List reports |
| `GET` | `/api/reports/{id}` | View a report and its history |
| `PATCH` | `/api/reports/{id}/status` | Move a report through the workflow |
| `POST` | `/api/reports/{id}/reopen` | Reopen a resolved report |
| `POST` | `/api/reports/{id}/feedback` | Add feedback after resolution |
| `GET` | `/api/reports/dashboard/summary` | View summary statistics |
| `GET` | `/api/locations` | List supported locations |
| `GET` | `/api/categories` | List categories and urgency values |

## Repository structure

```text
RepairLink/
├── app/
│   ├── core.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/reports.py
│   └── services/report_service.py
├── tests/test_reports.py
├── REPORT.md
├── RUN.md
├── pyproject.toml
├── .env.example
└── .gitignore
```

Read [RUN.md](RUN.md) for the complete setup procedure and [REPORT.md](REPORT.md) for the assignment report draft.

> Windows users should follow the Windows PowerShell or Windows Git Bash section in [RUN.md](RUN.md). In particular, Windows uses `.venv\\Scripts` rather than `.venv/bin`, and dependencies must be installed through the virtual-environment interpreter to avoid global pip permission errors.
