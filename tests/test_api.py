"""
Unit tests for the Analytics Engineer API.
Run with: pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self):
        """Test root health check."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test dedicated health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestInvoiceGeneration:
    """Test invoice generation endpoints."""
    
    def test_generate_invoices_default(self):
        """Test generating invoices with default count."""
        response = client.get("/invoices")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data
        assert isinstance(data["data"], list)
        assert data["count"] == len(data["data"])
    
    def test_generate_invoices_with_count(self):
        """Test generating specific number of invoices."""
        count = 5
        response = client.get(f"/invoices?count={count}")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == count
        assert len(data["data"]) == count
    
    def test_generate_invoices_invalid_count(self):
        """Test generating invoices with invalid count."""
        response = client.get("/invoices?count=0")
        assert response.status_code == 422  # Validation error
    
    def test_invoice_structure(self):
        """Test that generated invoices have expected structure."""
        response = client.get("/invoices?count=1")
        assert response.status_code == 200
        data = response.json()
        
        if data["data"]:
            invoice = data["data"][0]
            assert "message_id" in invoice
            assert "subject" in invoice
            assert "sender" in invoice
            assert "received_at" in invoice
            assert "body" in invoice
            assert "invoice_data" in invoice


class TestDatabaseOperations:
    """Test database operations."""
    
    def test_get_stats(self):
        """Test getting database statistics."""
        response = client.get("/invoices/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_invoices" in data
        assert "database_type" in data
    
    def test_seed_database(self):
        """Test seeding the database."""
        count = 5
        response = client.post(f"/invoices/seed?count={count}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["count"] == count
    
    def test_get_stored_invoices(self):
        """Test retrieving stored invoices."""
        response = client.get("/invoices/stored")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data
        assert isinstance(data["data"], list)
    
    def test_clear_database(self):
        """Test clearing the database."""
        response = client.delete("/invoices/stored")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestDataInconsistencies:
    """Test that data inconsistencies are present."""
    
    def test_inconsistencies_present(self):
        """Test that generated data contains various inconsistencies."""
        # Generate a larger batch to increase likelihood of inconsistencies
        response = client.get("/invoices?count=20")
        assert response.status_code == 200
        data = response.json()
        
        invoices = data["data"]
        
        # Track inconsistencies found
        found_issues = {
            'missing_invoice_id': False,
            'missing_currency': False,
            'string_amount': False,
            'extra_fields': False
        }
        
        base_fields = {'invoice_id', 'amount', 'currency', 'date', 'vendor_name', 'status'}
        
        for invoice in invoices:
            invoice_data = invoice.get('invoice_data', {})
            
            # Check for missing fields
            if not invoice_data.get('invoice_id'):
                found_issues['missing_invoice_id'] = True
            
            if not invoice_data.get('currency'):
                found_issues['missing_currency'] = True
            
            # Check for string amounts
            if isinstance(invoice_data.get('amount'), str):
                found_issues['string_amount'] = True
            
            # Check for extra fields (schema drift)
            extra_fields = set(invoice_data.keys()) - base_fields
            if extra_fields:
                found_issues['extra_fields'] = True
        
        # We expect to find at least some inconsistencies in 20 invoices
        # (though not guaranteed due to randomness)
        assert any(found_issues.values()), "No inconsistencies found in sample data"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
