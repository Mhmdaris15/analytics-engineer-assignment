"""
Main FastAPI application.
Entry point for the Analytics Engineer API server.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api import invoices, auth
from app.models.schemas import HealthResponse
from app.db.database import get_database
import uvicorn

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Database type: {settings.database_type}")
    print(f"Debug mode: {settings.debug}")
    print(f"Authentication: {'Enabled' if settings.enable_auth else 'Disabled'}")
    if settings.enable_auth:
        print(f"  Valid API Keys: {len(settings.valid_api_keys)} configured")
    
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
    - **Bearer Token Authentication**: Optional JWT-based security (configurable)
    
    ## Authentication
    
    Authentication is **disabled by default** for easy testing. 
    
    To enable authentication:
    1. Set `ENABLE_AUTH=True` in your .env file
    2. Generate a token using `/auth/token` endpoint with a valid API key
    3. Use the token in Authorization header: `Bearer <your-token>`
    
    Demo API Keys (when auth is enabled):
    - `demo-api-key-12345`
    - `test-key-67890`
    
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

# Add rate limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
    auth.router,
    tags=["Authentication"]
)

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
