# Quick Start Guide

## Start the Server

### Option 1: Local Development
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker (JSON Storage)
```powershell
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

### Option 3: Docker with MongoDB
```powershell
# Build and start with MongoDB
docker-compose -f docker-compose.mongodb.yml up -d

# Access MongoDB UI at http://localhost:8081
# Username: admin, Password: admin123

# Stop
docker-compose -f docker-compose.mongodb.yml down
```

## Test the API

### Using Browser
1. Open http://localhost:8000/docs
2. Try the `/invoices` endpoint with different parameters

### Using cURL
```powershell
# Generate 5 invoices
curl http://localhost:8000/invoices?count=5

# Store 3 invoices
curl "http://localhost:8000/invoices?count=3&store=true"

# Get statistics
curl http://localhost:8000/invoices/stats
```

### Using Python Script
```powershell
python test_api.py
```

## Common Operations

### Generate Invoices with Inconsistencies
```powershell
# Random number (2-5)
curl http://localhost:8000/invoices

# Specific count
curl http://localhost:8000/invoices?count=10

# Generate and store
curl "http://localhost:8000/invoices?count=5&store=true"
```

### Database Management
```powershell
# Seed database with test data
curl -X POST "http://localhost:8000/invoices/seed?count=20"

# Get all stored invoices
curl http://localhost:8000/invoices/stored

# Get statistics
curl http://localhost:8000/invoices/stats

# Clear all data
curl -X DELETE http://localhost:8000/invoices/stored
```

## Switching Database Types

### To JSON (Default)
Edit `.env`:
```env
DATABASE_TYPE=json
JSON_STORAGE_PATH=./data/invoices.json
```

### To MongoDB
1. Start MongoDB:
   ```powershell
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

2. Edit `.env`:
   ```env
   DATABASE_TYPE=mongodb
   MONGODB_URL=mongodb://localhost:27017
   ```

3. Restart server

## Troubleshooting

### Server won't start
- Check if port 8000 is available: `netstat -ano | findstr :8000`
- Verify Python version: `python --version` (need 3.9+)
- Check `.env` file exists and is properly configured

### Import errors
```powershell
pip install -r requirements.txt --upgrade
```

### MongoDB connection failed
- Ensure MongoDB is running: `docker ps`
- Check connection string in `.env`
- Test connection: `mongosh mongodb://localhost:27017`

## Next Steps

1. **Read the full README.md** for detailed documentation
2. **Explore API docs** at http://localhost:8000/docs
3. **Build your data pipeline** to consume this API
4. **Handle the inconsistencies** in your ETL process

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health status |
| GET | `/invoices` | Generate invoices |
| GET | `/invoices/stored` | Get stored invoices |
| DELETE | `/invoices/stored` | Clear stored invoices |
| GET | `/invoices/stats` | Get statistics |
| POST | `/invoices/seed` | Seed database |

---
For more details, see [README.md](README.md)
