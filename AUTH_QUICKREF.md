# 🔐 Authentication Quick Reference

## Default Credentials

### Candidate Account (For Assignment)
```
Username: candidate
Password: test123
Role: candidate
Access: Read invoices, view own info
```

### Admin Account (For Management)
```
Username: admin
Password: admin123
Role: admin
Access: Full access + user management
```

---

## Quick Start (3 Steps)

### 1️⃣ Login
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "candidate", "password": "test123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2️⃣ Save Token
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3️⃣ Use Token
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/invoices/stored?page=1&page_size=100"
```

---

## Python Quick Start

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/token",
    json={"username": "candidate", "password": "test123"}
)
token = response.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
invoices = requests.get(
    "http://localhost:8000/invoices/stored",
    headers=headers,
    params={"page": 1, "page_size": 100}
)

print(f"Retrieved {invoices.json()['count']} invoices")
```

---

## Authentication Endpoints

| Endpoint | Method | Access | Description |
|----------|--------|--------|-------------|
| `/auth/token` | POST | Public | Login with username/password |
| `/auth/verify` | GET | Authenticated | Verify token validity |
| `/auth/me` | GET | Authenticated | Get current user info |
| `/auth/register` | POST | **Admin Only** | Create new user |
| `/auth/users` | GET | **Admin Only** | List all users |

---

## Token Information

- **Expiration:** 8 hours (480 minutes)
- **Type:** JWT (JSON Web Token)
- **Algorithm:** HS256
- **Header Format:** `Authorization: Bearer <token>`

---

## Common Errors

### 401 Unauthorized
**Problem:** Invalid or expired token

**Solutions:**
- Get a new token via `/auth/token`
- Check you're using `Bearer ` prefix
- Verify token hasn't expired (8 hours)

### 403 Forbidden
**Problem:** Insufficient permissions (admin required)

**Solutions:**
- Login with admin account
- Candidates cannot access user management

### 429 Too Many Requests
**Problem:** Rate limit exceeded (30 req/min)

**Solutions:**
- Wait 60 seconds
- Use larger `page_size` (up to 500)
- Add delays between requests

---

## Security Features

✅ **Password Hashing** - bcrypt algorithm  
✅ **JWT Tokens** - Signed and time-limited  
✅ **Role-Based Access** - Candidate vs Admin  
✅ **Rate Limiting** - 30 requests/minute  
✅ **Pagination** - Max 500 items per request  

---

## Example: Complete Flow

```bash
# 1. Login as candidate
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "candidate", "password": "test123"}' \
  | jq -r '.access_token')

# 2. Get your user info
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/auth/me

# 3. Verify token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/auth/verify

# 4. Fetch invoices (paginated)
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/invoices/stored?page=1&page_size=100"

# 5. Check statistics
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/invoices/stats
```

---

## Files & Documentation

- 📘 **API_GUIDE.md** - Complete API consumption guide for candidates
- 🔒 **AUTH_IMPLEMENTATION.md** - Technical authentication details
- 📖 **README.md** - Project overview and setup
- 🚀 **QUICKSTART.md** - Quick setup instructions
- 🔐 **SECURITY.md** - Security features and best practices

---

**Need Help?** Check the interactive documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
