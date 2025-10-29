# API Usage Examples

This file contains example requests and responses for the Analytics Engineer API.

## Example 1: Generate Random Invoices

### Request
```bash
GET http://localhost:8000/invoices
```

### Response
```json
{
  "data": [
    {
      "message_id": "msg_001",
      "subject": "Invoice INV-1001",
      "sender": "vendor-a@company.com",
      "received_at": "2024-01-15T10:30:00Z",
      "body": "Please find invoice INV-1001 for $1,500.00 dated 2024-01-14",
      "invoice_data": {
        "invoice_id": "INV-1001",
        "amount": 1500.0,
        "currency": "USD",
        "date": "2024-01-14",
        "vendor_name": "Vendor A Inc.",
        "status": "paid"
      }
    },
    {
      "message_id": "msg_002",
      "subject": "URGENT: Invoice INV-1002",
      "sender": "vendor-c@services.com",
      "received_at": "2024-01-16T09:45:00Z",
      "body": "Invoice details: INV-1002 for $980.00",
      "invoice_data": {
        "invoice_id": "INV-1002",
        "amount": "$980.00",
        "currency": "USD",
        "date": "2024-01-15",
        "vendor_name": "Vendor C Services",
        "status": "pending",
        "due_date": "2024-02-15",
        "project_code": "PROJ-X1"
      }
    }
  ],
  "count": 2,
  "generated_at": "2024-01-18T10:00:00Z"
}
```

## Example 2: Generate Specific Count with Storage

### Request
```bash
GET http://localhost:8000/invoices?count=5&store=true
```

### Response
```json
{
  "data": [ /* 5 invoice objects */ ],
  "count": 5,
  "generated_at": "2024-01-18T10:05:00Z"
}
```

## Example 3: Data Inconsistency Examples

### Missing Invoice ID
```json
{
  "message_id": "msg_008",
  "subject": "INV-1008",
  "sender": "vendor-g@data.com",
  "received_at": "2024-01-18T12:00:00Z",
  "body": "Monthly subscription",
  "invoice_data": {
    "amount": 299.99,
    "currency": "USD",
    "date": "2024-01-18",
    "vendor_name": "Vendor G Data Co."
  }
}
```

### String Amount with Symbols
```json
{
  "invoice_data": {
    "invoice_id": "INV-1003",
    "amount": "$1,250.50",
    "currency": "USD",
    "date": "2024-01-16",
    "vendor_name": "Vendor C Services"
  }
}
```

### Invalid Amount
```json
{
  "invoice_data": {
    "invoice_id": "INV-1005",
    "amount": "TWO THOUSAND",
    "currency": "USD",
    "date": "2024-01-16",
    "vendor_name": "Vendor D Technologies"
  }
}
```

### Null Amount
```json
{
  "invoice_data": {
    "invoice_id": "INV-1007",
    "amount": null,
    "currency": "USD",
    "date": "2024-01-18",
    "vendor_name": "Vendor F Test"
  }
}
```

### Missing Currency
```json
{
  "invoice_data": {
    "invoice_id": "INV-1004",
    "amount": 1250.0,
    "date": "2024-01-16",
    "vendor_name": "Unknown Vendor LLC"
  }
}
```

### Invalid Datetime
```json
{
  "message_id": "msg_007",
  "subject": "Invoice Payment",
  "sender": "vendor-f@test.com",
  "received_at": "invalid_datetime",
  "body": "Regular invoice"
}
```

### Schema Drift - New Fields
```json
{
  "invoice_data": {
    "invoice_id": "INV-1009",
    "amount": 5500.0,
    "currency": "USD",
    "date": "2024-01-18",
    "vendor_name": "Vendor H Innovations",
    "status": "due",
    "project_code": "PROJ-Y2",
    "approver": "john.doe@demandlane.com",
    "due_date": "2024-02-18"
  }
}
```

### Nested Data Structure
```json
{
  "invoice_data": {
    "invoice_id": "INV-1006",
    "amount": 1850.75,
    "currency": "EUR",
    "date": "2024-01-17",
    "vendor_name": "Vendor E Global",
    "status": "paid",
    "tax_amount": 277.61,
    "line_items": [
      {
        "item": "Consulting",
        "quantity": 10,
        "rate": 185.075
      }
    ]
  }
}
```

## Example 4: Database Operations

### Seed Database
```bash
POST http://localhost:8000/invoices/seed?count=20
```

Response:
```json
{
  "message": "Successfully seeded database with 20 invoices",
  "count": 20,
  "timestamp": "2024-01-18T10:10:00Z"
}
```

### Get Statistics
```bash
GET http://localhost:8000/invoices/stats
```

Response:
```json
{
  "total_invoices": 42,
  "database_type": "json",
  "timestamp": "2024-01-18T10:15:00Z"
}
```

### Get Stored Invoices
```bash
GET http://localhost:8000/invoices/stored
```

Response:
```json
{
  "data": [ /* all stored invoices */ ],
  "count": 42,
  "generated_at": "2024-01-18T10:20:00Z"
}
```

### Clear Database
```bash
DELETE http://localhost:8000/invoices/stored
```

Response:
```json
{
  "message": "All stored invoices cleared successfully",
  "timestamp": "2024-01-18T10:25:00Z"
}
```

## Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Generate invoices
response = requests.get(f"{BASE_URL}/invoices?count=10")
data = response.json()

print(f"Generated {data['count']} invoices")

# Process each invoice
for email in data['data']:
    invoice_data = email.get('invoice_data', {})
    
    # Handle missing fields
    invoice_id = invoice_data.get('invoice_id', 'UNKNOWN')
    amount = invoice_data.get('amount')
    currency = invoice_data.get('currency', 'USD')
    
    # Handle amount inconsistencies
    if isinstance(amount, str):
        # Try to clean string amounts
        try:
            cleaned_amount = amount.replace('$', '').replace(',', '')
            amount = float(cleaned_amount)
        except ValueError:
            print(f"Invalid amount for {invoice_id}: {amount}")
            amount = None
    
    if amount is not None:
        print(f"{invoice_id}: {amount} {currency}")
    else:
        print(f"{invoice_id}: Invalid or missing amount")
```

## cURL Examples

### Generate and Store Invoices
```powershell
curl "http://localhost:8000/invoices?count=5&store=true"
```

### Seed Database
```powershell
curl -X POST "http://localhost:8000/invoices/seed?count=50"
```

### Get Statistics
```powershell
curl http://localhost:8000/invoices/stats
```

### Clear Database
```powershell
curl -X DELETE http://localhost:8000/invoices/stored
```

## Common Data Quality Challenges

When consuming this API, your pipeline should handle:

1. **Missing Critical Fields**: Check for null/missing invoice_id, amount, currency
2. **Type Coercion**: Convert string amounts to numbers, handle invalid formats
3. **Deduplication**: Track message_id and invoice_id to avoid duplicates
4. **Schema Validation**: Detect and adapt to new fields appearing
5. **Data Cleaning**: Strip currency symbols, parse dates correctly
6. **Error Handling**: Log and manage invalid records gracefully
7. **Currency Conversion**: Handle multiple currencies if needed
8. **Nested Data**: Flatten or properly handle nested structures like line_items
