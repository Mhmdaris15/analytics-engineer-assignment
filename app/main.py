"""
Main FastAPI application.
Entry point for the Analytics Engineer API server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api import invoices
from app.models.schemas import HealthResponse
from app.db.database import get_database
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Database type: {settings.database_type}")
    print(f"Debug mode: {settings.debug}")
    
    yield
    
    # Shutdown
    print("Shutting down application...")
    db = get_database()
    await db.close()
    print("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Analytics Engineer API - Mock Invoice Email Service
    
    This API simulates a real-world email service that returns invoice data with 
    intentional inconsistencies to test data engineering skills.
    
    ## Features
    
    - **Dynamic Data Generation**: Generates realistic invoice emails on-the-fly
    - **Intentional Inconsistencies**: Includes schema drift, missing fields, type errors, and duplicates
    - **Flexible Storage**: Supports both JSON file and MongoDB backends
    - **Testing Utilities**: Seed, clear, and retrieve stored data for testing
    
    ## Use Cases
    
    This API is designed for:
    - Testing data pipeline robustness
    - Practicing defensive programming techniques
    - Implementing schema detection and validation
    - Building ETL processes with real-world data quality challenges
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    invoices.router,
    tags=["Invoices"]
)


@app.get("/", response_model=HealthResponse)
async def root():
    """
    Root endpoint - Health check.
    
    Returns basic information about the API and its configuration.
    """
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        database_type=settings.database_type
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Used for monitoring and ensuring the service is running correctly.
    """
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        database_type=settings.database_type
    )


if __name__ == "__main__":
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
