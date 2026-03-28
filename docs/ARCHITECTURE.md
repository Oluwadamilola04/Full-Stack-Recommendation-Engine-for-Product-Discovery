# Architecture

## High-level system

The application has four main parts:

1. **Dataset ingestion**
2. **Backend API**
3. **Recommendation engine**
4. **Frontend**

## 1. Dataset ingestion

Source file:

- `clean_data.csv`

Loader:

- `backend/scripts/load_clean_data.py`

Responsibilities:

- read the raw dataset
- remove duplicate product rows
- normalize product fields
- write products into SQLite
- seed users
- seed user-product interactions

## 2. Backend API

Entry point:

- `backend/main.py`

Core modules:

- `backend/app/core`
- `backend/app/api`
- `backend/app/models`
- `backend/app/schemas`
- `backend/app/services`

Responsibilities:

- expose REST endpoints
- manage DB sessions and settings
- load and return products
- record interactions
- generate recommendations

## 3. Recommendation engine

Files:

- `ml/models/content_based.py`
- `ml/models/collaborative_filtering.py`
- `ml/models/hybrid.py`
- `backend/app/services/recommender.py`

### Content-based model

Uses product metadata such as:

- name
- brand
- category
- category_raw
- description
- tags

### Collaborative model

Uses seeded and recorded user interactions such as:

- view
- click
- add_to_cart
- purchase

### Hybrid model

Combines:

- content similarity
- collaborative predictions
- popularity fallback

## 4. Frontend

### Stable runtime

- `frontend/static/index.html`
- `frontend/static/app.js`
- `frontend/static/styles.css`

This is the default runtime because it avoids Vite/esbuild issues on restricted Windows setups.

### React source

- `frontend/src`

This remains the main source tree for the richer frontend implementation and can be tested with `run-react-frontend.bat`.

## Request flow

### Personalized recommendations

1. User opens the frontend
2. Frontend requests users/products from the API
3. User selects a seeded profile
4. User triggers a recommendation request
5. Backend loads interactions and products
6. Recommender combines signals
7. API returns ranked items
8. Frontend renders recommendation cards

### Similar products

1. Frontend opens a product page
2. Backend uses content-based similarity
3. Similar products are returned from product metadata

## Storage model

### Current local database

- SQLite

### Main entities

- `users`
- `products`
- `user_product_interactions`
- `recommendation_cache`

## Operational note

The project originally targeted a more infrastructure-heavy setup, but the current working local architecture is optimized for portability and demo reliability:

- SQLite instead of requiring PostgreSQL
- no Redis dependency for the local happy path
- fallback frontend to keep the app usable even when Vite is blocked
