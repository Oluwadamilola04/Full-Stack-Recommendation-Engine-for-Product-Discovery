# Quick Start

## Fastest path

From the project root:

```powershell
.\.venv\Scripts\python.exe backend\scripts\load_clean_data.py
.\run-all.bat
```

Open:

- Frontend: `http://127.0.0.1:5173`
- API docs: `http://127.0.0.1:8000/docs`

## What these commands do

### `load_clean_data.py`

- reads `clean_data.csv`
- resets the SQLite database
- inserts deduplicated products
- seeds users
- seeds interactions

### `run-all.bat`

- starts the FastAPI backend on port `8000`
- starts the stable fallback frontend on port `5173`

## If only the backend is needed

```powershell
.\run-backend.bat
```

## If only the frontend is needed

```powershell
.\run-frontend.bat
```

## If you want to test the React/Vite frontend

```powershell
.\run-react-frontend.bat
```

If Windows blocks `node.exe`, run:

```powershell
.\fix-node-block.bat
```

## Basic checks

- Backend health: `http://127.0.0.1:8000/health`
- Backend docs: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:5173`

## Common issue

If the frontend loads but says it cannot fetch data:

1. open `http://127.0.0.1:8000/health`
2. if health works, hard refresh the frontend with `Ctrl + F5`
3. if health fails, restart the backend
