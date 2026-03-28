"""Main FastAPI application for E-commerce Recommendation System"""

from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api.v1 import router as api_v1_router
from app.models.product import Product

ROOT_DIR = Path(__file__).resolve().parents[1]
STATIC_FRONTEND_DIR = ROOT_DIR / "frontend" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Application starting up...")
    Base.metadata.create_all(bind=engine)
    if settings.AUTO_LOAD_DEMO_DATA:
        db = SessionLocal()
        try:
            product_count = db.query(func.count(Product.id)).scalar() or 0
        finally:
            db.close()
        if product_count == 0:
            print("No products found. Loading demo dataset...")
            from scripts.load_clean_data import main as load_demo_data

            load_demo_data()
    yield
    # Shutdown
    print("Application shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="E-commerce Recommendation System API",
    description="End-to-end recommendation engine for e-commerce",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_v1_router, prefix="/api/v1")


if STATIC_FRONTEND_DIR.exists():
    app.mount("/static-frontend", StaticFiles(directory=STATIC_FRONTEND_DIR), name="static_frontend")


@app.get("/api-info")
async def api_info():
    """Basic API metadata endpoint."""
    return {
        "message": "Welcome to E-commerce Recommendation System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if STATIC_FRONTEND_DIR.exists():

    @app.get("/")
    async def frontend_index():
        """Serve the frontend entry page."""
        return FileResponse(STATIC_FRONTEND_DIR / "index.html")

    @app.get("/app.js")
    async def frontend_app_js():
        return FileResponse(STATIC_FRONTEND_DIR / "app.js")

    @app.get("/styles.css")
    async def frontend_styles():
        return FileResponse(STATIC_FRONTEND_DIR / "styles.css")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
