# Setup Guide

## Recommended setup

This project is currently easiest to run on Windows with the provided batch files and the repo-local virtual environment.

## Prerequisites

- Python installed
- project `.venv` available
- Node.js installed if you want to test the React frontend

## Standard local setup

### 1. Load the dataset

```powershell
.\.venv\Scripts\python.exe backend\scripts\load_clean_data.py
```

### 2. Start backend + frontend

```powershell
.\run-all.bat
```

### 3. Open the app

- `http://127.0.0.1:5173`
- `http://127.0.0.1:8000/docs`

## Simple shareable hosting

For the easiest shareable demo, deploy the project as **one Render web service** instead of splitting frontend and backend.

This repo includes `render.yaml`, and the backend can serve the fallback frontend directly.

### What this gives you

- one public URL
- frontend + API from the same service
- automatic demo dataset loading on startup

### Deployment steps

1. Push the repo to GitHub
2. Open Render
3. Create a new **Blueprint**
4. Select this repository
5. Let Render deploy the service from `render.yaml`
6. Open the generated URL

### Demo routes after deployment

- `/` - frontend
- `/docs` - API docs
- `/health` - health check

## Individual services

### Backend only

```powershell
.\run-backend.bat
```

### Stable frontend only

```powershell
.\run-frontend.bat
```

### React/Vite frontend only

```powershell
.\run-react-frontend.bat
```

## Dataset loading details

The loader script:

- reads `clean_data.csv`
- rebuilds the local SQLite database
- inserts products
- estimates display-ready prices in Naira
- seeds users
- seeds interactions

Run it again any time you want a fresh state:

```powershell
.\.venv\Scripts\python.exe backend\scripts\load_clean_data.py
```

## Backend configuration

Environment file:

- `backend/.env`

Important settings include:

- database URL
- CORS origins
- debug mode

The current local setup is configured to use SQLite by default.

## React frontend note

Some Windows machines block Node child-process creation, which breaks Vite/esbuild with `spawn EPERM`.

If that happens:

1. use the stable fallback frontend with `run-frontend.bat`
2. optionally run:

```powershell
.\fix-node-block.bat
```

That helper attempts to disable the Windows mitigation blocking `node.exe`.

## Verification checklist

### Backend health

Open:

- `http://127.0.0.1:8000/health`

Expected:

```json
{"status":"healthy"}
```

### Frontend

Open:

- `http://127.0.0.1:5173`

You should see the catalog page and seeded-user recommendation tester.

## Troubleshooting

### Frontend says it cannot reach the backend

- confirm `http://127.0.0.1:8000/health`
- restart `run-backend.bat`
- hard refresh the browser with `Ctrl + F5`

### Python command points to the Microsoft Store alias

Use the repo interpreter directly:

```powershell
.\.venv\Scripts\python.exe
```

### PowerShell blocks activation scripts

You do not need to activate the venv. Run the interpreter directly instead.

### React frontend shows a blank page

Use:

```powershell
.\run-frontend.bat
```

Then test React separately with:

```powershell
.\run-react-frontend.bat
```
