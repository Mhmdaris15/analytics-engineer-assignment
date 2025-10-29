# Security Guide - Bearer Token Authentication

## Overview

The Analytics Engineer API supports **Bearer Token (JWT) authentication** to secure endpoints. Authentication is **disabled by default** for easy testing, but can be enabled in production environments.

## Features

✅ **JWT-based Bearer Token** authentication  
✅ **Pre-shared API Keys** for token generation  
✅ **Configurable token expiration**  
✅ **Optional authentication** (can be toggled on/off)  
✅ **Protected write operations** (seed, delete)  
✅ **Public read operations** (when auth is disabled)  

## Quick Start

### 1. Enable Authentication

Edit your `.env` file:

```env
ENABLE_AUTH=True
SECRET_KEY=your-super-secret-key-min-32-characters-long
VALID_API_KEYS=["demo-api-key-12345", "test-key-67890", "your-custom-key"]
```

**Important:** Change the `SECRET_KEY` to a strong, random string in production!

Generate a secure key:
```powershell
# PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

### 2. Generate a Token

**Method 1: Using cURL**
```powershell
curl -X POST "http://localhost:8000/auth/token" `
  -H "Content-Type: application/json" `
  -d '{\"api_key\": \"demo-api-key-12345\", \"expires_in_minutes\": 60}'
```

**Method 2: Using Python**
```python
import requests

response = requests.post('http://localhost:8000/auth/token', json={
    "api_key": "demo-api-key-12345",
    "expires_in_minutes": 60
})

token_data = response.json()
token = token_data['access_token']
print(f"Token: {token}")
```

**Method 3: Using Swagger UI**
1. Go to http://localhost:8000/docs
2. Find `POST /auth/token` endpoint
3. Click "Try it out"
4. Enter your API key
5. Execute and copy the token

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 60,
  "message": "Use this token in the Authorization header as: Bearer <token>"
}
```

### 3. Use the Token

**With cURL:**
```powershell
curl -X GET "http://localhost:8000/invoices?count=5" `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**With Python:**
```python
import requests

headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(
    'http://localhost:8000/invoices?count=5',
    headers=headers
)

invoices = response.json()
```

**With Swagger UI:**
1. Click the 🔒 "Authorize" button at the top
2. Enter: `Bearer YOUR_TOKEN_HERE`
3. Click "Authorize"
4. Now all requests will include the token

## API Endpoints

### Authentication Endpoints

#### `POST /auth/token` - Generate Token
Generate a JWT access token using your API key.

**Request:**
```json
{
  "api_key": "demo-api-key-12345",
  "expires_in_minutes": 60
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 60,
  "message": "Use this token in the Authorization header as: Bearer <token>"
}
```

#### `GET /auth/verify` - Verify Token
Check if your token is valid.

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "valid": true,
  "message": "Token is valid",
  "token_info": {
    "api_key": "demo-api-key-12345",
    "type": "access",
    "issued_at": 1698765432,
    "expires_at": 1698769032
  }
}
```

### Protected Endpoints (when ENABLE_AUTH=True)

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/invoices` | GET | ✅ Yes | Generate invoices |
| `/invoices/stored` | GET | ❌ No | Get stored invoices |
| `/invoices/stored` | DELETE | ✅ Yes | Clear database |
| `/invoices/stats` | GET | ❌ No | Get statistics |
| `/invoices/seed` | POST | ✅ Yes | Seed database |

## Configuration Options

### Environment Variables

```env
# Enable or disable authentication
ENABLE_AUTH=False  # Set to True to enable

# Secret key for JWT signing (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-min-32-chars

# JWT algorithm
JWT_ALGORITHM=HS256

# Token expiration time (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Valid API keys (JSON array format)
VALID_API_KEYS=["key1", "key2", "key3"]
```

### Security Levels

#### Level 1: No Authentication (Default)
```env
ENABLE_AUTH=False
```
- All endpoints are public
- Good for development and testing
- No token required

#### Level 2: Bearer Token Authentication
```env
ENABLE_AUTH=True
SECRET_KEY=strong-random-secret-key-here
```
- Protected endpoints require valid JWT token
- Tokens generated using pre-shared API keys
- Suitable for production with trusted clients

## Managing API Keys

### Add New API Key

Edit `.env`:
```env
VALID_API_KEYS=["demo-api-key-12345", "test-key-67890", "prod-key-abc123"]
```

### Generate Secure API Key

```powershell
# PowerShell - Generate random 32-char key
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Example output: xK9mN2pQ7rS4tU8vW1yZ3aB5cD6eF7gH
```

### Best Practices

1. **Use strong, unique API keys** (minimum 32 characters)
2. **Rotate keys regularly** in production
3. **Different keys for different clients/environments**
4. **Never commit API keys to version control**
5. **Use environment variables** for key management

## Error Responses

### 401 Unauthorized - Invalid Token
```json
{
  "detail": "Could not validate credentials"
}
```

**Causes:**
- Token is expired
- Token is malformed
- Invalid signature
- Token not provided

**Solution:** Generate a new token

### 401 Unauthorized - Invalid API Key
```json
{
  "detail": "Invalid API key"
}
```

**Causes:**
- API key not in VALID_API_KEYS list
- Typo in API key

**Solution:** Check your API key matches one in `.env`

## Examples

### Complete Python Example

```python
import requests

BASE_URL = "http://localhost:8000"

class APIClient:
    def __init__(self, api_key: str):
        self.base_url = BASE_URL
        self.api_key = api_key
        self.token = None
    
    def authenticate(self):
        """Get a Bearer token."""
        response = requests.post(
            f"{self.base_url}/auth/token",
            json={"api_key": self.api_key}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data['access_token']
        return self.token
    
    def get_headers(self):
        """Get headers with Bearer token."""
        if not self.token:
            self.authenticate()
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_invoices(self, count: int = 5):
        """Fetch invoices (protected endpoint)."""
        response = requests.get(
            f"{self.base_url}/invoices?count={count}",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def seed_database(self, count: int = 10):
        """Seed database (protected endpoint)."""
        response = requests.post(
            f"{self.base_url}/invoices/seed?count={count}",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()

# Usage
client = APIClient(api_key="demo-api-key-12345")

# This will automatically authenticate
invoices = client.get_invoices(count=5)
print(f"Fetched {len(invoices['data'])} invoices")

# Seed database
result = client.seed_database(count=20)
print(result['message'])
```

### cURL Script Example

```powershell
# PowerShell script for authenticated API access

# Configuration
$API_KEY = "demo-api-key-12345"
$BASE_URL = "http://localhost:8000"

# Generate token
$tokenResponse = Invoke-RestMethod -Method Post -Uri "$BASE_URL/auth/token" `
    -ContentType "application/json" `
    -Body (@{api_key=$API_KEY} | ConvertTo-Json)

$TOKEN = $tokenResponse.access_token
Write-Host "Token obtained: $TOKEN"

# Use token to fetch invoices
$headers = @{
    Authorization = "Bearer $TOKEN"
}

$invoices = Invoke-RestMethod -Method Get -Uri "$BASE_URL/invoices?count=5" `
    -Headers $headers

Write-Host "Fetched $($invoices.count) invoices"

# Seed database
$seedResult = Invoke-RestMethod -Method Post -Uri "$BASE_URL/invoices/seed?count=10" `
    -Headers $headers

Write-Host $seedResult.message
```

## Testing Authentication

### Test Script

```powershell
# test_auth.ps1

Write-Host "Testing API Authentication..." -ForegroundColor Cyan

# 1. Test without authentication (should work if ENABLE_AUTH=False)
Write-Host "`n1. Testing public access..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod "http://localhost:8000/health"
    Write-Host "✓ Public endpoint accessible" -ForegroundColor Green
} catch {
    Write-Host "✗ Public endpoint failed" -ForegroundColor Red
}

# 2. Generate token
Write-Host "`n2. Generating authentication token..." -ForegroundColor Yellow
try {
    $tokenResponse = Invoke-RestMethod -Method Post `
        -Uri "http://localhost:8000/auth/token" `
        -ContentType "application/json" `
        -Body '{"api_key": "demo-api-key-12345"}'
    
    $token = $tokenResponse.access_token
    Write-Host "✓ Token generated successfully" -ForegroundColor Green
    Write-Host "  Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Token generation failed" -ForegroundColor Red
    exit 1
}

# 3. Verify token
Write-Host "`n3. Verifying token..." -ForegroundColor Yellow
try {
    $headers = @{ Authorization = "Bearer $token" }
    $verify = Invoke-RestMethod -Uri "http://localhost:8000/auth/verify" `
        -Headers $headers
    Write-Host "✓ Token is valid" -ForegroundColor Green
} catch {
    Write-Host "✗ Token verification failed" -ForegroundColor Red
}

# 4. Use token to access protected endpoint
Write-Host "`n4. Accessing protected endpoint..." -ForegroundColor Yellow
try {
    $invoices = Invoke-RestMethod -Uri "http://localhost:8000/invoices?count=3" `
        -Headers $headers
    Write-Host "✓ Successfully fetched $($invoices.count) invoices" -ForegroundColor Green
} catch {
    Write-Host "✗ Protected endpoint access failed" -ForegroundColor Red
}

Write-Host "`nAll authentication tests completed!" -ForegroundColor Cyan
```

## Production Recommendations

### 1. Environment Variables
```env
# PRODUCTION SETTINGS
ENABLE_AUTH=True
SECRET_KEY=<generate-strong-random-key-64-chars>
ACCESS_TOKEN_EXPIRE_MINUTES=30
VALID_API_KEYS=["<strong-key-1>", "<strong-key-2>"]
```

### 2. Use HTTPS
Always use HTTPS in production to protect tokens in transit.

### 3. Short Token Expiration
Set `ACCESS_TOKEN_EXPIRE_MINUTES=30` or less for better security.

### 4. Rotate Secrets Regularly
- Change `SECRET_KEY` every 90 days
- Rotate API keys for different clients

### 5. Monitor Access
Log authentication attempts and monitor for suspicious activity.

### 6. Rate Limiting
Consider adding rate limiting middleware (not included in this implementation).

## Troubleshooting

### Token Expired
**Error:** "Could not validate credentials"  
**Solution:** Generate a new token using `/auth/token`

### Invalid API Key
**Error:** "Invalid API key"  
**Solution:** Check API key matches one in `VALID_API_KEYS`

### Token Not Sent
**Error:** "Not authenticated"  
**Solution:** Include `Authorization: Bearer <token>` header

### Authentication Not Working
**Check:**
1. Is `ENABLE_AUTH=True` in .env?
2. Did you restart the server after changing .env?
3. Is the token in the correct format: `Bearer <token>`?

## Additional Resources

- JWT.io - Decode and inspect JWT tokens: https://jwt.io
- FastAPI Security Documentation: https://fastapi.tiangolo.com/tutorial/security/
- OAuth2 with Password Flow: For more advanced authentication needs

---

**Remember:** Authentication is **optional** and disabled by default. Enable it when you need to secure your API in production or controlled environments.
