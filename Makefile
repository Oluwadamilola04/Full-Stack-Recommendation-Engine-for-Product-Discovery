BACKEND_IMAGE=ecommerce-recommendation-backend:latest
FRONTEND_IMAGE=ecommerce-recommendation-frontend:latest

# Build images
docker build -f docker/Dockerfile.backend -t $(BACKEND_IMAGE) .
docker build -f docker/Dockerfile.frontend -t $(FRONTEND_IMAGE) .

# Push to registry (adjust registry URL)
push-backend:
	docker tag $(BACKEND_IMAGE) your-registry/$(BACKEND_IMAGE)
	docker push your-registry/$(BACKEND_IMAGE)

push-frontend:
	docker tag $(FRONTEND_IMAGE) your-registry/$(FRONTEND_IMAGE)
	docker push your-registry/$(FRONTEND_IMAGE)

# Start services
up:
	cd docker && docker-compose up -d

down:
	cd docker && docker-compose down

logs:
	cd docker && docker-compose logs -f

# Development
dev-backend:
	cd backend && pip install -r requirements.txt && uvicorn main:app --reload

dev-frontend:
	cd frontend && npm install && npm run dev

dev-all:
	$(MAKE) dev-backend & $(MAKE) dev-frontend

# Testing
test-backend:
	cd backend && pytest

test-frontend:
	cd frontend && npm test

# Database
db-migrate:
	psql -U ecommerce_user -d ecommerce_recommendations -f database/migrations/001_init_schema.sql
	psql -U ecommerce_user -d ecommerce_recommendations -f database/migrations/002_sample_data.sql

db-reset:
	dropdb ecommerce_recommendations
	createdb ecommerce_recommendations
	$(MAKE) db-migrate

.PHONY: push-backend push-frontend up down logs dev-backend dev-frontend dev-all test-backend test-frontend db-migrate db-reset
