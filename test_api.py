"""
Simple test script to demonstrate API usage.
Run this after starting the server to verify functionality.
"""

import requests
import json
from typing import List, Dict, Any


BASE_URL = "http://localhost:8000"


def print_separator(title: str = ""):
    """Print a visual separator."""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)
    print()


def test_health_check():
    """Test the health check endpoint."""
    print_separator("Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_generate_invoices(count: int = 3):
    """Test generating invoices."""
    print_separator(f"Generating {count} Invoices")
    response = requests.get(f"{BASE_URL}/invoices?count={count}")
    data = response.json()
    
    print(f"Generated: {data['count']} invoices")
    print(f"Generated at: {data['generated_at']}")
    
    # Show first invoice as example
    if data['data']:
        print("\nFirst Invoice:")
        print(json.dumps(data['data'][0], indent=2))
    
    return data['data']


def analyze_inconsistencies(invoices: List[Dict[str, Any]]):
    """Analyze and report inconsistencies in invoice data."""
    print_separator("Inconsistency Analysis")
    
    issues = {
        'missing_invoice_id': 0,
        'missing_amount': 0,
        'missing_currency': 0,
        'string_amount': 0,
        'invalid_datetime': 0,
        'null_values': 0,
        'extra_fields': 0
    }
    
    base_fields = {'invoice_id', 'amount', 'currency', 'date', 'vendor_name', 'status'}
    
    for invoice in invoices:
        invoice_data = invoice.get('invoice_data', {})
        
        # Check missing critical fields
        if not invoice_data.get('invoice_id'):
            issues['missing_invoice_id'] += 1
        if not invoice_data.get('amount'):
            issues['missing_amount'] += 1
        if not invoice_data.get('currency'):
            issues['missing_currency'] += 1
        
        # Check amount type
        amount = invoice_data.get('amount')
        if isinstance(amount, str):
            issues['string_amount'] += 1
        if amount is None:
            issues['null_values'] += 1
        
        # Check datetime
        received_at = invoice.get('received_at')
        if received_at and 'invalid' in str(received_at).lower():
            issues['invalid_datetime'] += 1
        
        # Check for extra fields (schema drift)
        extra = set(invoice_data.keys()) - base_fields
        if extra:
            issues['extra_fields'] += 1
            print(f"  Found extra fields: {extra}")
    
    print("\nIssues Found:")
    for issue, count in issues.items():
        if count > 0:
            print(f"  - {issue.replace('_', ' ').title()}: {count}")


def test_store_invoices(count: int = 5):
    """Test storing invoices."""
    print_separator(f"Storing {count} Invoices")
    response = requests.get(f"{BASE_URL}/invoices?count={count}&store=true")
    print(f"Status Code: {response.status_code}")
    print(f"Stored: {response.json()['count']} invoices")


def test_get_stored_invoices():
    """Test retrieving stored invoices."""
    print_separator("Retrieving Stored Invoices")
    response = requests.get(f"{BASE_URL}/invoices/stored")
    data = response.json()
    print(f"Retrieved: {data['count']} invoices")
    return data['data']


def test_get_stats():
    """Test getting statistics."""
    print_separator("Database Statistics")
    response = requests.get(f"{BASE_URL}/invoices/stats")
    stats = response.json()
    print(json.dumps(stats, indent=2))


def test_seed_database(count: int = 10):
    """Test seeding the database."""
    print_separator(f"Seeding Database with {count} Invoices")
    response = requests.post(f"{BASE_URL}/invoices/seed?count={count}")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_clear_database():
    """Test clearing the database."""
    print_separator("Clearing Database")
    response = requests.delete(f"{BASE_URL}/invoices/stored")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  ANALYTICS ENGINEER API - TEST SUITE")
    print("=" * 80)
    
    try:
        # Test health check
        test_health_check()
        
        # Generate and analyze invoices
        invoices = test_generate_invoices(count=10)
        analyze_inconsistencies(invoices)
        
        # Test database operations
        test_clear_database()
        test_seed_database(count=15)
        test_get_stats()
        
        stored = test_get_stored_invoices()
        if stored:
            print(f"\nSample stored invoice:")
            print(json.dumps(stored[0], indent=2))
        
        print_separator("All Tests Completed Successfully!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print("   Please ensure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    main()
