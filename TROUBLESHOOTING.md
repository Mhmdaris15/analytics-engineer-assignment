# Troubleshooting Guide

Common issues and solutions for the Analytics Engineer API.

## Installation Issues

### Issue: `pip install` fails
**Symptoms**: Errors when installing requirements
**Solutions**:
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Try installing packages individually
pip install fastapi uvicorn pydantic
```

### Issue: Virtual environment activation fails
**Symptoms**: `venv\Scripts\Activate.ps1` doesn't work
**Solutions**:
```powershell
# Check execution policy
Get-ExecutionPolicy

# If restricted, allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Alternative: Use CMD instead of PowerShell
venv\Scripts\activate.bat
```

### Issue: Python not found
**Symptoms**: `'python' is not recognized`
**Solutions**:
- Install Python 3.9+ from python.org
- Add Python to PATH
- Try `python3` instead of `python`
- Try `py` command: `py -m venv venv`

## Server Issues

### Issue: Port 8000 already in use
**Symptoms**: `Address already in use` error
**Solutions**:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or use a different port
uvicorn app.main:app --port 8001
```

### Issue: Import errors when starting server
**Symptoms**: `ModuleNotFoundError: No module named 'fastapi'`
**Solutions**:
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Verify installation
pip list | findstr fastapi

# Reinstall if needed
pip install -r requirements.txt --force-reinstall
```

### Issue: Server starts but can't access endpoints
**Symptoms**: Connection refused or timeout
**Solutions**:
```powershell
# Check if server is running
curl http://localhost:8000/health

# Try 127.0.0.1 instead of localhost
curl http://127.0.0.1:8000/health

# Check firewall settings
# Windows Defender may block the connection

# Verify server is listening
netstat -ano | findstr :8000
```

## Database Issues

### Issue: JSON file permission denied
**Symptoms**: Can't write to `data/invoices.json`
**Solutions**:
```powershell
# Check file permissions
icacls data\invoices.json

# Grant full control to current user
icacls data\invoices.json /grant:r "$env:USERNAME:(F)"

# Or delete and recreate
Remove-Item data\invoices.json
New-Item data\invoices.json -ItemType File -Value "[]"
```

### Issue: MongoDB connection failed
**Symptoms**: `ServerSelectionTimeoutError`
**Solutions**:
```powershell
# Check if MongoDB is running
docker ps | findstr mongo

# Start MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Check connection string in .env
# Should be: mongodb://localhost:27017

# Test connection
mongosh mongodb://localhost:27017
```

### Issue: Database type not switching
**Symptoms**: Still using old database after changing .env
**Solutions**:
- Restart the server (stop and start again)
- Clear Python cache: `Remove-Item -Recurse -Force app\__pycache__`
- Verify .env file is in the root directory
- Check no typos in DATABASE_TYPE value

## Docker Issues

### Issue: Docker command not found
**Symptoms**: `'docker' is not recognized`
**Solutions**:
- Install Docker Desktop from docker.com
- Restart PowerShell after installation
- Check Docker is running: `docker --version`

### Issue: Docker build fails
**Symptoms**: Errors during `docker-compose up`
**Solutions**:
```powershell
# Build with verbose output
docker-compose build --no-cache

# Check Docker logs
docker-compose logs

# Ensure Docker Desktop is running
# Check system resources (Docker needs RAM)
```

### Issue: Container exits immediately
**Symptoms**: Container starts then stops
**Solutions**:
```powershell
# Check container logs
docker-compose logs api

# Run interactively to see errors
docker-compose run api bash

# Check .env is correctly configured
```

### Issue: Can't access API in Docker
**Symptoms**: localhost:8000 not responding
**Solutions**:
```powershell
# Check container is running
docker ps

# Check port mapping
docker ps | findstr 8000

# Use host IP instead of localhost
# Find your IP: ipconfig
# Try: http://<your-ip>:8000
```

## API Issues

### Issue: 422 Validation Error
**Symptoms**: API returns validation error
**Solutions**:
- Check query parameters are correct
- Ensure count is between 1-20 (for /invoices)
- Ensure count is between 1-100 (for /seed)
- Check request body format if sending POST data

### Issue: 500 Internal Server Error
**Symptoms**: Server error when calling endpoint
**Solutions**:
```powershell
# Check server logs for details
# Look at uvicorn output

# Check database is accessible
# Verify .env configuration

# Try health check endpoint first
curl http://localhost:8000/health
```

### Issue: No inconsistencies in generated data
**Symptoms**: All data looks perfect
**Solutions**:
- This is random! Generate more invoices (20+)
- Increase INCONSISTENCY_RATE in .env
- Default is 0.3 (30% chance)
- Try: `INCONSISTENCY_RATE=0.7`

### Issue: Too many duplicates
**Symptoms**: Same invoices appearing repeatedly
**Solutions**:
- Adjust DUPLICATE_RATE in .env
- Default is 0.1 (10% chance)
- Lower it: `DUPLICATE_RATE=0.05`
- Clear database: `curl -X DELETE http://localhost:8000/invoices/stored`

## Testing Issues

### Issue: pytest not found
**Symptoms**: `'pytest' is not recognized`
**Solutions**:
```powershell
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Or install all dev dependencies
pip install -r requirements.txt
```

### Issue: Tests failing
**Symptoms**: Test failures when running pytest
**Solutions**:
```powershell
# Ensure server is NOT running during tests
# Tests use TestClient which starts its own server

# Run specific test
pytest tests/test_api.py::TestHealthEndpoints -v

# Run with more details
pytest tests/ -vv -s

# Check test dependencies are installed
pip list | findstr pytest
```

### Issue: test_api.py script fails
**Symptoms**: Connection error when running test script
**Solutions**:
```powershell
# Ensure server IS running for this script
# This script tests the actual running server

# Start server first
uvicorn app.main:app --reload

# Then in another terminal:
python test_api.py

# Check the BASE_URL in test_api.py matches your setup
```

## Configuration Issues

### Issue: .env file not being read
**Symptoms**: Using default values instead of .env
**Solutions**:
- Ensure .env is in root directory (same level as app/)
- Check file is named exactly `.env` (not `.env.txt`)
- No spaces in environment variable names
- Restart server after changing .env
- Verify with: `Get-Content .env`

### Issue: Settings not updating
**Symptoms**: Changed .env but no effect
**Solutions**:
```powershell
# Stop server completely (Ctrl+C)
# Clear Python cache
Remove-Item -Recurse -Force app\__pycache__

# Restart server
uvicorn app.main:app --reload
```

## Performance Issues

### Issue: Server is slow
**Symptoms**: Long response times
**Solutions**:
- Reduce INCONSISTENCY_RATE (less processing)
- Use MongoDB instead of JSON for better performance
- Limit number of invoices per request
- Check system resources (RAM, CPU)
- Enable production mode: `DEBUG=False`

### Issue: High memory usage
**Symptoms**: Server consuming lots of RAM
**Solutions**:
- Clear stored invoices periodically
- Use MongoDB with proper indexes
- Limit JSON file size
- Restart server periodically in production

## Development Issues

### Issue: Code changes not reflecting
**Symptoms**: Modified code but server behaves the same
**Solutions**:
```powershell
# Ensure using --reload flag
uvicorn app.main:app --reload

# Or restart server manually
# Ctrl+C then start again

# Clear Python cache
Remove-Item -Recurse -Force app\__pycache__
```

### Issue: Import errors in IDE
**Symptoms**: Red underlines in VSCode/PyCharm
**Solutions**:
- Select correct Python interpreter (venv)
- VSCode: Ctrl+Shift+P → "Python: Select Interpreter"
- Restart IDE after creating venv
- Install packages: `pip install -r requirements.txt`

## Getting Help

### Check Logs
```powershell
# Server logs (console output)
# Look for error messages and stack traces

# Docker logs
docker-compose logs -f api

# Check specific container
docker logs analytics-engineer-api
```

### Verify Installation
```powershell
# Check Python version
python --version  # Should be 3.9+

# Check installed packages
pip list

# Check FastAPI is working
python -c "import fastapi; print(fastapi.__version__)"
```

### Test Basic Functionality
```powershell
# Test if server starts
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Test health endpoint
curl http://localhost:8000/health

# Test basic invoice generation
curl http://localhost:8000/invoices?count=1
```

### Still Having Issues?

1. **Read the error message carefully**
   - Error messages usually contain the solution

2. **Check the documentation**
   - README.md for setup instructions
   - QUICKSTART.md for quick start
   - EXAMPLES.md for usage examples

3. **Try a clean install**
   ```powershell
   # Remove virtual environment
   Remove-Item -Recurse -Force venv
   
   # Recreate everything
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Check system requirements**
   - Python 3.9 or higher
   - At least 2GB RAM
   - Port 8000 available
   - Internet connection (for pip install)

5. **Use Docker as fallback**
   ```powershell
   # Docker often "just works"
   docker-compose up -d
   ```

## Quick Reset

If all else fails, complete reset:

```powershell
# Stop everything
docker-compose down
Ctrl+C  # Stop server if running

# Clean up
Remove-Item -Recurse -Force venv
Remove-Item -Recurse -Force app\__pycache__
Remove-Item -Recurse -Force data\invoices.json
Remove-Item .env

# Fresh start
Copy-Item .env.example .env
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

**Still stuck?** Double-check that you followed the QUICKSTART.md guide step-by-step.
