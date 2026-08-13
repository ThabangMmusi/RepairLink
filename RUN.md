# RepairLink: How to Run the Project

This guide covers Linux/macOS, Windows PowerShell, and Windows Git Bash. RepairLink uses a local `.venv` directory so its packages stay isolated from the global Python installation.

> Important: On Windows, do not use Linux commands such as `python3`, `source .venv/bin/activate`, or `.venv/bin/activate`. Windows virtual environments use `.venv\Scripts`.

## 1. Install Python on Windows if necessary

The message **“Python was not found; run without arguments to install from the Microsoft Store”** means Windows cannot find a usable Python executable through the current command. Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/windows/) and select **Add python.exe to PATH** during installation. Then close and reopen Git Bash or PowerShell.

You can check the installation with either command:

```powershell
py --version
python --version
```

The Windows `py` launcher is usually more reliable than `python`. The commands below use `py -3` for Windows.

## 2. Clone the repository

```bash
git clone https://github.com/ThabangMmusi/RepairLink.git
cd RepairLink
```

## 3. Create the isolated virtual environment

### Windows PowerShell

```powershell
py -3 -m venv .venv
```

### Windows Git Bash

```bash
py -3 -m venv .venv
```

If the `py` command is unavailable but `python` works, use:

```bash
python -m venv .venv
```

Do not continue until this command creates the `.venv` directory. If it does not, Python is not installed correctly or is not available on PATH.

## 4. Activate the virtual environment

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run this once for the current user and then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.venv\Scripts\Activate.ps1
```

### Windows Git Bash

```bash
source .venv/Scripts/activate
```

### Linux or macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

After activation, the terminal should begin with `(.venv)`. Confirm that the active Python belongs to the project environment:

### Windows Git Bash or PowerShell

```bash
python -c "import sys; print(sys.executable)"
```

The printed path should end with `.venv/Scripts/python.exe` or `.venv\\Scripts\\python.exe`.

### Linux or macOS

```bash
python -c "import sys; print(sys.executable)"
```

The printed path should end with `.venv/bin/python`.

## 5. Install dependencies inside `.venv`

Run this only after activation:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The upgrade command now runs inside `.venv`, so it does not need administrator permissions and does not modify the global Python installation. Do not use `sudo`, and do not use a global `pip.exe`.

If activation is not working, use the virtual-environment interpreter directly instead:

### Windows

```powershell
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

### Linux or macOS

```bash
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
```

## 6. Configure the environment

### Windows Git Bash or Linux/macOS

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

The default configuration uses a local SQLite database named `repairlink.db`. The `.env` file is ignored by Git because it may contain machine-specific settings.

## 7. Run the automated tests

With `.venv` activated:

```bash
python -m pytest
```

If activation is not working, call the environment interpreter directly:

### Windows

```powershell
.venv\Scripts\python.exe -m pytest
```

### Linux or macOS

```bash
.venv/bin/python -m pytest
```

The tests use an in-memory SQLite database and do not modify the development database.

## 8. Start the API

With `.venv` activated:

```bash
python -m uvicorn app.main:app --reload
```

If activation is not working:

### Windows

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### Linux or macOS

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

Open the following pages in a browser:

| Page | URL |
|---|---|
| API home | http://127.0.0.1:8000/ |
| Health check | http://127.0.0.1:8000/health |
| Interactive Swagger documentation | http://127.0.0.1:8000/docs |
| Alternative ReDoc documentation | http://127.0.0.1:8000/redoc |

Stop the server with `Ctrl+C`.

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

The `.venv` folder can be removed and recreated at any time. It is ignored by Git and must not be committed:

### Windows PowerShell

```powershell
Remove-Item -Recurse -Force .venv
py -3 -m venv .venv
```

### Windows Git Bash or Linux/macOS

```bash
rm -rf .venv
python3 -m venv .venv
```

## Troubleshooting

| Message | Cause | Fix |
|---|---|---|
| `Python was not found` | Python is missing or not on PATH | Install Python from python.org, enable PATH, reopen the terminal, and use `py -3` |
| `.venv/bin/activate: No such file` | A Linux activation command was used on Windows | Use `source .venv/Scripts/activate` in Git Bash or `.venv\Scripts\Activate.ps1` in PowerShell |
| `Access is denied` while installing `pip`, `ruff`, or another package | Installation was attempted globally | Activate `.venv` and use `python -m pip ...`, or use `.venv\Scripts\python.exe -m pip ...` directly |
| `No module named pytest` | Dependencies were not installed into the active environment | Activate `.venv`, then run `python -m pip install -e ".[dev]` |
| `No module named fastapi` | The server was started with global Python | Start it with `python -m uvicorn` after activation or `.venv\Scripts\python.exe -m uvicorn` |
| Port `8000` is busy | Another process is using the port | Run `python -m uvicorn app.main:app --reload --port 8001` |

The warnings about `~ip` indicate a damaged global pip installation. They are unrelated to RepairLink’s isolated environment. Do not repair the global installation to run this project; use the project’s `.venv` instead.
