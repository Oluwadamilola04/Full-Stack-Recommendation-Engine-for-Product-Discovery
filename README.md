# E-commerce Recommendation System

An end-to-end recommendation system built with FastAPI, SQLite, lightweight ML models, and a frontend for exploring products and testing personalized recommendations.

## What this project does

- Loads a richer e-commerce dataset from `clean_data.csv`
- Builds a product catalog with images, brands, tags, descriptions, ratings, and review counts
- Estimates realistic demo prices in Nigerian Naira for display in the UI
- Seeds demo users and realistic interactions for recommendation testing
- Serves recommendation APIs for:
  - `hybrid`
  - `collaborative`
  - `content`
  - `similar products`
  - `trending products`
- Provides a working frontend fallback on `http://127.0.0.1:5173`

## Current stack

- **Backend:** FastAPI + SQLAlchemy
- **Database:** SQLite
- **ML layer:** custom collaborative, content-based, and hybrid models in `ml/models`
- **Frontend:** React source is included, while the default runtime uses `frontend/static` because some Windows setups block Vite child-process spawning

## Run the project

### 1. Load the dataset

From the project root:

```powershell
.\.venv\Scripts\python.exe backend\scripts\load_clean_data.py
```

This:

- loads `clean_data.csv`
- deduplicates products
- resets the local SQLite database
- seeds users
- seeds interactions for recommendation testing
- estimates product prices in Naira for demo display

### 2. Start everything

```powershell
.\run-all.bat
```

### 3. Open the app

- Frontend: `http://127.0.0.1:5173`
- Backend docs: `http://127.0.0.1:8000/docs`
- Backend health: `http://127.0.0.1:8000/health`

## Run options

- `run-all.bat` - starts backend + frontend
- `run-backend.bat` - starts only the API
- `run-frontend.bat` - starts the stable static frontend fallback
- `run-react-frontend.bat` - explicitly tests the React/Vite frontend
- `fix-node-block.bat` - attempts to remove the Windows mitigation blocking `node.exe`

## Shareable demo deployment

The simplest shareable setup for this project is a **single free Render web service**.

This repo now includes:

- `render.yaml`
- backend routes that can serve `frontend/static`
- automatic demo data loading on startup when `ECRS_AUTO_LOAD_DEMO_DATA=true`

That means one hosted service can:

- serve the frontend
- serve the API
- auto-seed the demo dataset

### Expected result

After deployment, your public link works like a normal site:

- homepage at `/`
- API docs at `/docs`
- health at `/health`

### Render deployment steps

1. Push this repo to GitHub
2. Create a Render account
3. Choose **New +** -> **Blueprint**
4. Connect your GitHub repo
5. Render will detect `render.yaml`
6. Deploy the `recommendhub-demo` service
7. Open the generated Render URL

### Important demo note

The free/simple version is optimized for **demo sharing**, not long-term production persistence. The dataset auto-loads at startup so the public demo stays usable even if the service restarts.

## Frontend note

The project currently defaults to the static fallback frontend because some Windows environments block Vite/esbuild with `spawn EPERM`.

If you want to test the React frontend:

```powershell
.\run-react-frontend.bat
```

If that fails due to the Windows Node block:

```powershell
.\fix-node-block.bat
```

## Recommendation flow

1. Products are loaded from the dataset into SQLite
2. Users and interactions are seeded
3. The backend builds:
   - a content-based model from product metadata
   - a collaborative model from interaction history
   - a hybrid ranking layer
4. The frontend requests recommendations and renders results

## Key API endpoints

### Health

- `GET /health`

### Products

- `GET /api/v1/products/`
- `GET /api/v1/products/{product_id}`

### Users

- `GET /api/v1/users/`
- `GET /api/v1/users/{user_id}`

### Interactions

- `POST /api/v1/interactions/`
- `GET /api/v1/interactions/user/{user_id}`

### Recommendations

- `GET /api/v1/recommendations/user/{user_id}?strategy=hybrid`
- `GET /api/v1/recommendations/user/{user_id}?strategy=collaborative`
- `GET /api/v1/recommendations/user/{user_id}?strategy=content`
- `GET /api/v1/recommendations/similar/{product_id}`
- `GET /api/v1/recommendations/trending`

## Project structure

```text
backend/
  app/
    api/
    core/
    models/
    schemas/
    services/
  scripts/
frontend/
  src/        # React source
  static/     # Working fallback frontend
ml/
  models/
database/
  migrations/
docs/
```

## Portfolio positioning

This project is strong portfolio material because it shows:

- full-stack development
- backend API design
- applied recommendation systems
- data ingestion and transformation
- user interaction modeling
- debugging and fallback engineering on Windows

### Good title ideas

- **Hybrid E-commerce Recommendation System**
- **Full-Stack Recommendation Engine for Product Discovery**
- **Personalized Shopping Recommender with FastAPI and ML**

### What to highlight on your CV or portfolio

- Built a recommendation engine combining collaborative, content-based, and hybrid ranking
- Designed a FastAPI backend with product, user, interaction, and recommendation endpoints
- Ingested and transformed a real product dataset into a working recommendation workflow
- Seeded interaction data to simulate personalization and cold-start behavior
- Delivered a frontend experience for browsing products and testing recommendation outputs
- Added a fallback frontend/runtime path to keep the project working despite OS-specific Node restrictions

### Suggested portfolio write-up

> Built an end-to-end e-commerce recommendation system using FastAPI, SQLite, and custom ML ranking models. The project supports content-based, collaborative, and hybrid recommendations, ingests a real product catalog dataset, seeds user interactions for personalization, and exposes a browsable frontend plus documented REST APIs.

## Testing

### Backend

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest
```

### React source type-check

```powershell
cd frontend
"C:\Program Files\nodejs\node.exe" .\node_modules\typescript\bin\tsc --noEmit
```

## Troubleshooting

### Frontend says it cannot reach the backend

Check:

- `http://127.0.0.1:8000/health`

If that does not open, restart:

```powershell
.\run-backend.bat
```

### Frontend shows old errors

Hard refresh the browser:

```text
Ctrl + F5
```

### React/Vite frontend fails on Windows

Try:

```powershell
.\fix-node-block.bat
```

If needed, use the stable fallback with:

```powershell
.\run-frontend.bat
```

