# Project Overview

## Summary

This project is a full-stack e-commerce recommendation system designed to demonstrate:

- API design with FastAPI
- recommendation logic across multiple strategies
- product dataset ingestion and normalization
- interaction-driven personalization
- frontend delivery under real environment constraints

## What has been built

### Backend

- FastAPI application with versioned REST endpoints
- SQLAlchemy models and Pydantic schemas
- SQLite-backed local development setup
- recommendation service layer
- product, user, interaction, and recommendation APIs

### Recommendation engine

- content-based model from catalog metadata
- collaborative filtering from user interactions
- hybrid scoring layer
- popularity/trending fallback
- similar-product recommendations

### Data layer

- loader for `clean_data.csv`
- product deduplication by `ProdID`
- brand, tags, images, description, category, ratings, and review count support
- seeded users and interactions for demo personalization

### Frontend

- React source in `frontend/src`
- stable fallback frontend in `frontend/static`
- product browsing
- recommendation testing by seeded user
- interaction capture from product pages

## Current operating model

- Recommended local database: SQLite
- Recommended startup path: batch scripts at repo root
- Recommended frontend runtime: static fallback
- Optional frontend runtime: React/Vite when Windows allows Node child-process spawning

## Why this project is portfolio-worthy

- it solves a real product recommendation problem
- it shows both ML-style ranking logic and product engineering
- it includes debugging and resilience work, not just ideal-path code
- it demonstrates that you can ship around environment constraints instead of getting stuck
