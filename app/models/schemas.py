"""
Data models for invoice emails and invoice data.
Flexible structure to allow for schema drift and inconsistencies.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class InvoiceData(BaseModel):
    """
    Invoice data model with flexible schema to handle inconsistencies.
    Core fields are defined, but additional fields are allowed.
    """
    invoice_id: Optional[str] = None
    amount: Optional[Union[float, str, int]] = None  # Can be number or string
    currency: Optional[str] = None
    date: Optional[str] = None
    vendor_name: Optional[str] = None
    status: Optional[str] = None
    
    # Optional fields that may appear (schema drift)
    due_date: Optional[str] = None
    project_code: Optional[str] = None
    tax_amount: Optional[Union[float, str]] = None
    line_items: Optional[List[Dict[str, Any]]] = None
    approver: Optional[str] = None
    
    class Config:
        # Allow additional fields not defined in the model
        extra = "allow"


class EmailInvoice(BaseModel):
    """
    Email message containing invoice data.
    Represents the structure of emails received from vendors.
    """
    message_id: str
    subject: str
    sender: str
    received_at: Optional[Union[str, datetime]] = None  # Can be invalid
    body: str
    invoice_data: Optional[Union[InvoiceData, Dict[str, Any]]] = None
    
    class Config:
        extra = "allow"


class InvoiceResponse(BaseModel):
    """Response model for invoice endpoints."""
    data: List[EmailInvoice]
    count: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    version: str
    database_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatsResponse(BaseModel):
    """Statistics response."""
    total_invoices: int
    database_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
