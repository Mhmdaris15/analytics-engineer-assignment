"""
API routes for invoice operations.
Provides endpoints to fetch, generate, and manage invoice data.
"""

import random
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime

from app.models.schemas import InvoiceResponse, StatsResponse
from app.utils.generator import generator
from app.db.database import get_database
from app.core.config import settings


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
    )
):
    """
    Get a batch of invoice emails with intentional inconsistencies.
    
    This endpoint simulates the behavior of fetching emails from a mail service.
    Each call may return a different number of records with varying data quality issues.
    
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


@router.get("/invoices/stored", response_model=InvoiceResponse)
async def get_stored_invoices():
    """
    Retrieve all invoices stored in the database.
    
    This endpoint returns previously generated and stored invoices.
    Useful for testing data persistence and deduplication strategies.
    
    Returns:
    - JSON array of all stored invoice emails
    """
    db = get_database()
    invoices = await db.get_all_invoices()
    
    return InvoiceResponse(
        data=invoices,
        count=len(invoices),
        generated_at=datetime.utcnow()
    )


@router.delete("/invoices/stored")
async def clear_stored_invoices():
    """
    Clear all stored invoices from the database.
    
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
        le=100,
        description="Number of invoices to seed"
    )
):
    """
    Seed the database with a batch of invoices.
    
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
