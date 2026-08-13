# RepairLink: How to Run the Project

This guide assumes Linux or macOS. Windows users can use the equivalent activation command shown below. The project uses a local `.venv` directory so that its packages remain isolated from the global Python installation.

## 1. Clone the repository

```bash
git clone https://github.com/ThabangMmusi/RepairLink.git
cd RepairLink
```

## 2. Check Python

RepairLink requires Python 3.11 or newer.

```bash
python3 --version
```

## 3. Create an isolated virtual environment

```bash
python3 -m venv .venv
```

The `.venv` folder contains only this project’s installed packages. It is excluded from Git by `.gitignore` and must never be committed.

## 4. Activate the virtual environment

### Linux or macOS

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

After activation, the terminal should show `(.venv)` at the beginning of the prompt.

## 5. Upgrade packaging tools and install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Using `python -m pip` ensures that packages are installed into the active virtual environment.

## 6. Configure the environment

Copy the example configuration file:

```bash
cp .env.example .env
```

The default configuration uses a local SQLite database named `repairlink.db`. The `.env` file is ignored by Git because it may contain machine-specific settings.

## 7. Start the API

```bash
python -m uvicorn app.main:app --reload
```

Open the following pages in a browser:

| Page | URL |
|---|---|
| API home | http://127.0.0.1:8000/ |
| Health check | http://127.0.0.1:8000/health |
| Interactive Swagger documentation | http://127.0.0.1:8000/docs |
| Alternative ReDoc documentation | http://127.0.0.1:8000/redoc |

Stop the server with `Ctrl+C`.

## 8. Run the automated tests

Open another terminal, enter the repository, activate the environment, and run:

```bash
source .venv/bin/activate
python -m pytest
```

The tests use an in-memory SQLite database and do not modify the development database.

## 9. Test a report manually with cURL

Start the server first, then run:

```bash
curl -X POST http://127.0.0.1:8000/api/reports \\
  -H "Content-Type: application/json" \\
  -d '{
    "location": "Off-Campus Residence - Block A",
    "category": "electrical",
    "description": "The corridor light is not working and students cannot see safely.",
    "urgency": "high",
    "affects_multiple_people": true,
    "safety_risk": true
  }'
```

The response contains the report `id` and a tracking reference such as `RL-202608131030`.

## 10. Demonstrate the status workflow

Replace `1` with the report ID returned by the previous request:

```bash
curl -X PATCH http://127.0.0.1:8000/api/reports/1/status \\
  -H "Content-Type: application/json" \\
  -d '{"status":"received","note":"Report received for review."}'

curl -X PATCH http://127.0.0.1:8000/api/reports/1/status \\
  -H "Content-Type: application/json" \\
  -d '{"status":"assigned","note":"Assigned to maintenance."}'

curl -X PATCH http://127.0.0.1:8000/api/reports/1/status \\
  -H "Content-Type: application/json" \\
  -d '{"status":"in_progress","note":"Maintenance work has started."}'

curl -X PATCH http://127.0.0.1:8000/api/reports/1/status \\
  -H "Content-Type: application/json" \\
  -d '{"status":"resolved","note":"The fault was repaired."}'
```

Then view the report history:

```bash
curl http://127.0.0.1:8000/api/reports/1
```

## 11. Stop using the environment

```bash
deactivate
```

The `.venv` folder can be removed and recreated at any time:

```bash
rm -rf .venv
python3 -m venv .venv
```

## Troubleshooting

If `uvicorn` cannot be found, activate `.venv` and reinstall with `python -m pip install -e ".[dev]"`. If port `8000` is busy, run `python -m uvicorn app.main:app --reload --port 8001` and use port `8001` in the URLs. If the database must be reset during development, stop the server and delete `repairlink.db`; it will be recreated automatically on the next run.
