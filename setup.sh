#!/bin/bash

# E-commerce Recommendation System - Initial Setup Script

set -e

echo "🚀 Starting E-commerce Recommendation System Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found${NC}"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠ PostgreSQL is not in PATH (it's ok if running in Docker)${NC}"
fi

# Backend setup
echo -e "\n${YELLOW}Setting up Backend...${NC}"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install
source venv/bin/activate || . venv/Scripts/activate
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please update .env with your database credentials${NC}"
fi

cd ..

# Frontend setup
echo -e "\n${YELLOW}Setting up Frontend...${NC}"
cd frontend

echo "Installing dependencies..."
npm install

cd ..

echo -e "\n${GREEN}✓ Setup complete!${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Update backend/.env with your database credentials"
echo "2. Start PostgreSQL and Redis"
echo "3. Run database migrations:"
echo "   psql -U postgres -d ecommerce_recommendations -f database/migrations/001_init_schema.sql"
echo "   psql -U postgres -d ecommerce_recommendations -f database/migrations/002_sample_data.sql"
echo "4. Start backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "5. Start frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker:"
echo "   cd docker && docker-compose up -d"
echo ""
echo "API docs will be available at: http://localhost:8000/docs"
echo "Frontend will be available at: http://localhost:3000"
