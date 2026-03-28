# Start Here

If you just want the project running, use this order:

## 1. Load the dataset

```powershell
.\.venv\Scripts\python.exe backend\scripts\load_clean_data.py
```

## 2. Start the app

```powershell
.\run-all.bat
```

## 3. Open these URLs

- Frontend: `http://127.0.0.1:5173`
- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## What is already set up

- backend API
- SQLite database
- dataset loader
- seeded demo users
- seeded user interactions
- hybrid recommendation pipeline
- stable frontend fallback

## Important note

The project includes a React frontend source tree, but the default runtime uses the fallback frontend in `frontend/static` because some Windows environments block Vite child-process creation.

If you want to test the React frontend explicitly:

```powershell
.\run-react-frontend.bat
```

If Windows blocks it:

```powershell
.\fix-node-block.bat
```
