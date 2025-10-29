"""
API routes for invoice operations.
Provides endpoints to fetch, generate, and manage invoice data.
"""

import random
import math
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Depends, Request
from datetime import datetime

from app.models.schemas import InvoiceResponse, PaginatedInvoiceResponse, StatsResponse
from app.utils.generator import generator
from app.db.database import get_database
from app.core.config import settings
from app.core.security import verify_api_key_header, optional_auth


router = APIRouter()


@router.get("/invoices", response_model=InvoiceResponse)
async def get_invoices(
    count: Optional[int] = Query(
        None, 
        ge=1, 
        le=20,
        description="Number of invoices to generate (overrides random count)"
    ),
    store: bool = Query(
        False,
        description="Whether to store generated invoices in database"
    ),
    authenticated: bool = Depends(verify_api_key_header) if settings.enable_auth else Depends(lambda: True)
):
    """
    Get a batch of invoice emails with intentional inconsistencies.
    
    This endpoint simulates the behavior of fetching emails from a mail service.
    Each call may return a different number of records with varying data quality issues.
    
    **Authentication:** Required if ENABLE_AUTH=True in settings
    
    Query Parameters:
    - count: Specify exact number of invoices (1-20). If not provided, generates random count.
    - store: If true, saves generated invoices to the configured database.
    
    Returns:
    - JSON array of email objects containing invoice data
    - Each object may have schema drift, missing fields, type inconsistencies, or duplicates
    """
    # Determine how many invoices to generate
    if count is None:
        count = random.randint(
            settings.min_invoices_per_request,
            settings.max_invoices_per_request
        )
    
    # Generate invoice batch with inconsistencies
    invoices = generator.generate_batch(
        count=count,
        duplicate_rate=settings.duplicate_rate
    )
    
    # Optionally store in database
    if store:
        db = get_database()
        success = await db.save_invoices(invoices)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store invoices in database"
            )
    
    return InvoiceResponse(
        data=invoices,
        count=len(invoices),
        generated_at=datetime.utcnow()
    )


@router.get("/invoices/stored", response_model=PaginatedInvoiceResponse)
async def get_stored_invoices(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(100, ge=1, le=500, description="Number of items per page (max 500)"),
    authenticated: bool = Depends(verify_api_key_header) if settings.enable_auth else Depends(lambda: True)
):
    """
    Retrieve stored invoices with pagination and rate limiting.
    
    **Security Features:**
    - ✅ Pagination: Maximum 500 items per request
    - ✅ Rate Limiting: 30 requests per minute per IP
    - ✅ Prevents fetching entire database at once
    
    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 100, max: 500)
    
    **Rate Limit:** 30 requests/minute per IP address
    
    **Example:**
    - Get first page: `GET /invoices/stored?page=1&page_size=100`
    - Get second page: `GET /invoices/stored?page=2&page_size=100`
    
    Returns:
    - Paginated list of stored invoices with metadata
    - Total count and pagination info
    """
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    
    # Apply rate limiting: 30 requests per minute
    limiter = Limiter(key_func=get_remote_address)
    limiter.limit("30/minute")(get_stored_invoices)
    
    db = get_database()
    
    # Get total count
    total = await db.get_invoice_count()
    
    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    # Validate page number
    if page > total_pages and total > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Page {page} does not exist. Total pages: {total_pages}"
        )
    
    # Get paginated data
    invoices = await db.get_paginated_invoices(skip=skip, limit=page_size)
    
    return PaginatedInvoiceResponse(
        data=invoices,
        count=len(invoices),
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
        generated_at=datetime.utcnow()
    )


@router.delete("/invoices/stored")
async def clear_stored_invoices(
    authenticated: bool = Depends(verify_api_key_header) if settings.enable_auth else Depends(lambda: True)
):
    """
    Clear all stored invoices from the database.
    
    **Authentication:** Required if ENABLE_AUTH=True in settings
    
    Useful for resetting the database state during testing.
    
    Returns:
    - Success message
    """
    db = get_database()
    success = await db.clear_invoices()
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to clear invoices from database"
        )
    
    return {
        "message": "All stored invoices cleared successfully",
        "timestamp": datetime.utcnow()
    }


@router.get("/invoices/stats", response_model=StatsResponse)
async def get_invoice_stats():
    """
    Get statistics about stored invoices.
    
    Returns:
    - Total count of invoices in database
    - Database type being used
    - Timestamp of query
    """
    db = get_database()
    count = await db.get_invoice_count()
    
    return StatsResponse(
        total_invoices=count,
        database_type=settings.database_type,
        timestamp=datetime.utcnow()
    )


@router.post("/invoices/seed")
async def seed_database(
    count: int = Query(
        10,
        ge=1,
        le=1000,
        description="Number of invoices to seed"
    ),
    authenticated: bool = Depends(verify_api_key_header) if settings.enable_auth else Depends(lambda: True)
):
    """
    Seed the database with a batch of invoices.
    
    **Authentication:** Required if ENABLE_AUTH=True in settings
    
    Useful for quickly populating the database with test data.
    
    Query Parameters:
    - count: Number of invoices to generate and store (1-100)
    
    Returns:
    - Success message with count
    """
    invoices = generator.generate_batch(
        count=count,
        duplicate_rate=settings.duplicate_rate
    )
    
    db = get_database()
    success = await db.save_invoices(invoices)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to seed database"
        )
    
    return {
        "message": f"Successfully seeded database with {count} invoices",
        "count": count,
        "timestamp": datetime.utcnow()
    }
