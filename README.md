# Analytics Engineer API

A FastAPI-based mock email service that generates invoice data with intentional inconsistencies for testing data engineering skills and building robust data pipelines.

## 🎯 Purpose

This API simulates a real-world scenario where invoice data is extracted from email sources. It's designed to challenge data engineers with:

- **Schema Drift**: New fields appearing unexpectedly
- **Missing Critical Fields**: invoice_id, amount, or currency might be absent
- **Data Type Inconsistencies**: Numbers as strings, invalid formats, null values
- **Duplicate Records**: Same invoices appearing multiple times
- **Malformed Data**: Invalid dates, unparseable amounts, nested structures

## 🏗️ Architecture

```
analytics-engineer-api/
├── app/
│   ├── api/                 # API route handlers
│   │   └── invoices.py      # Invoice endpoints
│   ├── core/                # Core configuration
│   │   └── config.py        # Settings management
│   ├── db/                  # Database layer
│   │   └── database.py      # Abstraction for JSON/MongoDB
│   ├── models/              # Data models
│   │   └── schemas.py       # Pydantic models
│   ├── utils/               # Utilities
│   │   └── generator.py     # Invoice data generator
│   └── main.py              # FastAPI application
├── data/                    # JSON storage (if using JSON DB)
├── tests/                   # Test files
├── .env                     # Environment variables
├── .env.example             # Example environment file
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip or poetry
- MongoDB (optional, only if using MongoDB storage)

### Installation

1. **Clone the repository**
   ```powershell
   git clone <repository-url>
   cd analytics-engineer-api
   ```

2. **Create virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```powershell
   # Copy example env file
   Copy-Item .env.example .env
   
   # Edit .env with your settings
   # Default uses JSON storage (no additional setup needed)
   ```

5. **Run the server**
   ```powershell
   # Option 1: Using uvicorn directly
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Option 2: Using Python
   python -m app.main
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## 📚 API Endpoints

### 🔐 Authentication

All endpoints (except `/health`) require Bearer Token authentication.

**Login to get access token:**
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "candidate", "password": "test123"}'
```

**Default Credentials:**
- **Candidate**: `candidate` / `test123` (read access)
- **Admin**: `admin` / `admin123` (full access + user management)

**Use token in requests:**
```bash
curl -H "Authorization: Bearer <your_token>" http://localhost:8000/invoices
```

📖 **For detailed authentication guide, see [API_GUIDE.md](API_GUIDE.md)**

---

### Core Endpoints

#### `GET /health`
Health check and basic information (no authentication required)
```json
{
  "status": "healthy",
  "app_name": "Analytics Engineer API",
  "version": "1.0.0",
  "database_type": "json",
  "timestamp": "2024-01-18T10:00:00Z"
}
```

#### `GET /invoices`
Generate and return invoice emails with inconsistencies

**Authentication:** Required  
**Query Parameters:**
- `count` (optional, 1-20): Number of invoices to generate
- `store` (optional, boolean): Whether to save to database

**Example:**
```bash
# Generate random number of invoices
curl -H "Authorization: Bearer <token>" http://localhost:8000/invoices

# Generate exactly 5 invoices
curl -H "Authorization: Bearer <token>" http://localhost:8000/invoices?count=5

# Generate and store 3 invoices
curl -H "Authorization: Bearer <token>" "http://localhost:8000/invoices?count=3&store=true"
```

**Response:**
```json
{
  "data": [
    {
      "message_id": "msg_001",
      "subject": "Invoice INV-1001",
      "sender": "vendor-a@company.com",
      "received_at": "2024-01-15T10:30:00Z",
      "body": "Please find invoice INV-1001 for $1,500.00",
      "invoice_data": {
        "invoice_id": "INV-1001",
        "amount": 1500.00,
        "currency": "USD",
        "date": "2024-01-14",
        "vendor_name": "Vendor A Inc.",
        "status": "paid"
      }
    }
  ],
  "count": 1,
  "generated_at": "2024-01-18T10:00:00Z"
}
```

#### `GET /invoices/stored`
Retrieve stored invoices with pagination

**Authentication:** Required  
**Rate Limit:** 30 requests/minute  
**Query Parameters:**
- `page` (optional, default: 1): Page number
- `page_size` (optional, default: 100, max: 500): Items per page

#### `DELETE /invoices/stored`
Clear all stored invoices from the database

**Authentication:** Required

#### `GET /invoices/stats`
Get statistics about stored invoices

**Authentication:** Required  
**Response:**
```json
{
  "total_invoices": 42,
  "database_type": "json",
  "timestamp": "2024-01-18T10:00:00Z"
}
```

#### `POST /invoices/seed`
Seed the database with a batch of invoices

**Authentication:** Required

**Query Parameters:**
- `count` (optional, 1-100): Number of invoices to seed (default: 10)

**Example:**
```powershell
curl -X POST "http://localhost:8000/invoices/seed?count=20"
```

## ⚙️ Configuration

### Environment Variables

All configuration is managed through environment variables in `.env`:

```env
# Application Settings
APP_NAME=Analytics Engineer API
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database Configuration
# Options: "json" or "mongodb"
DATABASE_TYPE=json

# MongoDB Configuration (only if DATABASE_TYPE=mongodb)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=analytics_engineer
MONGODB_COLLECTION=invoices

# JSON Storage Configuration (only if DATABASE_TYPE=json)
JSON_STORAGE_PATH=./data/invoices.json

# Data Generation Settings
MIN_INVOICES_PER_REQUEST=2
MAX_INVOICES_PER_REQUEST=5
INCONSISTENCY_RATE=0.3  # 30% chance of inconsistencies
DUPLICATE_RATE=0.1      # 10% chance of duplicates
```

### Database Options

#### JSON File Storage (Default)
- **Pros**: No external dependencies, easy setup, good for development
- **Cons**: Not suitable for high concurrency, limited query capabilities
- **Setup**: No additional configuration needed

#### MongoDB Storage
- **Pros**: Better for production, supports complex queries, handles concurrency
- **Cons**: Requires MongoDB server
- **Setup**:
  ```powershell
  # 1. Install MongoDB locally or use Docker
  docker run -d -p 27017:27017 --name mongodb mongo:latest
  
  # 2. Update .env
  DATABASE_TYPE=mongodb
  MONGODB_URL=mongodb://localhost:27017
  ```

## 🎲 Data Inconsistencies

The API generates the following types of inconsistencies to challenge your data pipeline:

### 1. Schema Drift
New fields appear over time:
```json
{
  "invoice_data": {
    "due_date": "2024-02-15",      // New field
    "project_code": "PROJ-X1",     // New field
    "tax_amount": 277.61,          // New field
    "line_items": [...]            // New nested structure
  }
}
```

### 2. Missing Critical Fields
```json
{
  "invoice_data": {
    // invoice_id is MISSING!
    "amount": 299.99,
    "currency": "USD"
  }
}
```

### 3. Data Type Inconsistencies
```json
{
  "amount": "$1,500.00",        // String instead of number
  "amount": "TWO THOUSAND",     // Text instead of number
  "amount": null,               // Null value
  "received_at": "invalid_datetime"  // Invalid format
}
```

### 4. Duplicate Records
Same `message_id` or `invoice_id` appearing multiple times

### 5. Currency Variations
```json
{
  "amount": 1850.75,
  "currency": "EUR"  // Different currency
}
```

## 🧪 Testing Your Pipeline

### Recommended Testing Strategy

1. **Fetch Fresh Data**
   ```powershell
   curl http://localhost:8000/invoices?count=10
   ```

2. **Store Data for Testing**
   ```powershell
   curl "http://localhost:8000/invoices?count=20&store=true"
   ```

3. **Retrieve Stored Data**
   ```powershell
   curl http://localhost:8000/invoices/stored
   ```

4. **Check Statistics**
   ```powershell
   curl http://localhost:8000/invoices/stats
   ```

5. **Clear and Reset**
   ```powershell
   curl -X DELETE http://localhost:8000/invoices/stored
   ```

### Example Python Client

```python
import requests

# Generate and fetch invoices
response = requests.get('http://localhost:8000/invoices?count=5')
invoices = response.json()['data']

# Process each invoice
for email in invoices:
    invoice_data = email.get('invoice_data', {})
    
    # Handle missing invoice_id
    invoice_id = invoice_data.get('invoice_id', 'UNKNOWN')
    
    # Handle amount inconsistencies
    amount = invoice_data.get('amount')
    if isinstance(amount, str):
        # Clean string amounts: "$1,500.00" -> 1500.00
        amount = float(amount.replace('$', '').replace(',', ''))
    
    # Handle missing currency
    currency = invoice_data.get('currency', 'USD')
    
    print(f"{invoice_id}: {amount} {currency}")
```

## 🐳 Docker Support

### Using Docker Compose

```powershell
# Start the API with MongoDB
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🏗️ Design Decisions

### 1. Database Abstraction
- **Decision**: Created `DatabaseInterface` abstract class
- **Rationale**: Allows easy switching between JSON and MongoDB without changing business logic
- **Benefits**: Testability, flexibility, future extensibility

### 2. Flexible Pydantic Models
- **Decision**: Used `extra="allow"` in models
- **Rationale**: Permits schema drift without breaking validation
- **Benefits**: Handles unexpected fields gracefully

### 3. Async Architecture
- **Decision**: Used async/await throughout
- **Rationale**: Better performance for I/O operations (especially MongoDB)
- **Benefits**: Scalability, concurrent request handling

### 4. Separate Generator Module
- **Decision**: Isolated data generation logic in `generator.py`
- **Rationale**: Single responsibility, testability
- **Benefits**: Easy to modify generation rules, testable in isolation

### 5. Configuration Management
- **Decision**: Used Pydantic Settings with `.env` file
- **Rationale**: Type-safe, validated configuration
- **Benefits**: Prevents misconfiguration, clear documentation

## 📈 Scalability Considerations

If data volume increased 100x, consider:

1. **Database**: Switch to MongoDB with proper indexing
   ```python
   # Add indexes on frequently queried fields
   await collection.create_index("invoice_data.invoice_id")
   await collection.create_index("received_at")
   ```

2. **Caching**: Add Redis for frequently accessed data
   ```python
   # Cache generated invoices temporarily
   cache.set(f"invoices:{request_id}", invoices, ex=300)
   ```

3. **Pagination**: Implement cursor-based pagination
   ```python
   @router.get("/invoices/stored")
   async def get_stored_invoices(
       limit: int = 100,
       cursor: Optional[str] = None
   ):
       # Return limited results with next cursor
   ```

4. **Background Processing**: Use Celery for heavy operations
   ```python
   @celery_app.task
   def process_invoice_batch(invoice_ids):
       # Process in background
   ```

5. **Load Balancing**: Deploy multiple instances behind a load balancer

## 🧰 Development

### Running Tests

```powershell
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Code Quality

```powershell
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## 🤝 Contributing

This is a mock API for educational purposes. Feel free to:
- Add more inconsistency types
- Improve data generation algorithms
- Add more database backends
- Enhance documentation

## 📄 License

MIT License - feel free to use this for educational and testing purposes.

## 🔗 Related Projects

- **Analytics Engineer Assignment**: This API was created to support the Demandlane take-home assignment
- **Data Pipeline Testing**: Use this API to test your ETL/ELT pipelines

## 📞 Support

For issues or questions:
1. Check the API documentation: http://localhost:8000/docs
2. Review this README
3. Open an issue on GitHub

---

**Happy Data Engineering! 🚀**
