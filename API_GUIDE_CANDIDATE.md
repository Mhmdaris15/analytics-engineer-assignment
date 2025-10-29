# 📘 API Consumption Guide for Candidates

Welcome! This guide will help you consume the Analytics Engineer Invoice API for your take-home assignment.

## 🔗 Base URL

```
https://demandlane-analytics-engineer.recursive-tech.site
```

> **Note**: The backend server is already running. You don't need to set it up.

---

## 🔐 Authentication

All API endpoints require Bearer Token authentication using JWT (JSON Web Tokens).

### Step 1: Get Your Access Token

**Endpoint:** `POST /auth/token`

**Authentication Method:** Username and password

**Default Credentials:**
- **Candidate Account**: 
  - Username: `candidate`
  - Password: `test123`

**Request Body:**
```json
{
  "username": "candidate",
  "password": "test123"
}
```

**Example using cURL:**
```bash
curl -X POST "https://demandlane-analytics-engineer.recursive-tech.site/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "candidate", "password": "test123"}'
```

**Example using Python:**
```python
import requests

response = requests.post(
    "https://demandlane-analytics-engineer.recursive-tech.site/auth/token",
    json={"username": "candidate", "password": "test123"}
)

token_data = response.json()
access_token = token_data["access_token"]
print(f"Access Token: {access_token}")
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

> **Note:** Tokens expire after **8 hours** (480 minutes). You'll need to log in again to get a new token.

### Step 2: Use the Token in Requests

Include the token in the `Authorization` header with the `Bearer` prefix:

```
Authorization: Bearer <your_access_token>
```

**Example using cURL:**
```bash
curl -X GET "https://demandlane-analytics-engineer.recursive-tech.site/invoices/stored?page=1&page_size=100" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Example using Python:**
```python
import requests

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(
    "https://demandlane-analytics-engineer.recursive-tech.site/invoices/stored",
    headers=headers,
    params={"page": 1, "page_size": 100}
)

data = response.json()
```

---

## 📊 Main Endpoint: Get Stored Invoices

**Endpoint:** `GET /invoices/stored`

**Purpose:** Retrieve invoice data from the database with pagination support.

### Query Parameters

| Parameter | Type | Required | Default | Max | Description |
|-----------|------|----------|---------|-----|-------------|
| `page` | integer | No | 1 | - | Page number (starts at 1) |
| `page_size` | integer | No | 100 | 500 | Number of items per page |

### Response Format

```json
{
  "data": [
    {
      "invoice_id": "INV-2024-001",
      "customer_name": "John Doe",
      "amount": 1500.00,
      "date": "2024-01-15",
      "email": "john@example.com",
      "status": "paid"
    }
    // ... more invoices
  ],
  "count": 100,           // Items in current page
  "total": 5000,          // Total items in database
  "page": 1,              // Current page number
  "page_size": 100,       // Items per page
  "total_pages": 50,      // Total number of pages
  "has_next": true,       // Is there a next page?
  "has_prev": false,      // Is there a previous page?
  "generated_at": "2024-10-29T10:30:00.000Z"
}
```

### Example Usage

#### Python - Fetch All Pages
```python
import requests

# Get access token first
auth_response = requests.post(
    "https://demandlane-analytics-engineer.recursive-tech.site/auth/token",
    json={"username": "candidate", "password": "test123"}
)
access_token = auth_response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {access_token}"
}

# Fetch all pages
all_invoices = []
page = 1
page_size = 100

while True:
    response = requests.get(
        "https://demandlane-analytics-engineer.recursive-tech.site/invoices/stored",
        headers=headers,
        params={"page": page, "page_size": page_size}
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        break
    
    data = response.json()
    all_invoices.extend(data["data"])
    
    print(f"Fetched page {page}/{data['total_pages']} - Total items: {len(all_invoices)}")
    
    # Check if there's a next page
    if not data["has_next"]:
        break
    
    page += 1

print(f"Total invoices fetched: {len(all_invoices)}")
```

#### Python - Using Pandas
```python
import requests
import pandas as pd

# Get access token
auth_response = requests.post(
    "https://demandlane-analytics-engineer.recursive-tech.site/auth/token",
    json={"username": "candidate", "password": "test123"}
)
access_token = auth_response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {access_token}"
}

# Fetch first page
response = requests.get(
    "https://demandlane-analytics-engineer.recursive-tech.site/invoices/stored",
    headers=headers,
    params={"page": 1, "page_size": 500}  # Max allowed per request
)

data = response.json()

# Convert to DataFrame
df = pd.DataFrame(data["data"])
print(f"Loaded {len(df)} invoices")
print(df.head())
```

#### JavaScript/Node.js
```javascript
const axios = require('axios');

async function fetchInvoices() {
  // Get access token
  const authResponse = await axios.post('https://demandlane-analytics-engineer.recursive-tech.site/auth/token', {
    username: 'candidate',
    password: 'test123'
  });
  
  const accessToken = authResponse.data.access_token;
  
  // Fetch invoices
  const response = await axios.get('https://demandlane-analytics-engineer.recursive-tech.site/invoices/stored', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    },
    params: {
      page: 1,
      page_size: 100
    }
  });
  
  const { data, total, page, total_pages, has_next } = response.data;
  console.log(`Page ${page}/${total_pages} - Total: ${total} invoices`);
  
  return data;
}

fetchInvoices();
```

---

## 🚦 Rate Limiting

**Important:** The API has rate limiting to prevent abuse.

### Limits
- **30 requests per minute per IP address**
- If you exceed this limit, you'll receive a `429 Too Many Requests` response

### Best Practices

1. **Add delays between requests:**
   ```python
   import time
   
   for page in range(1, total_pages + 1):
       response = requests.get(url, headers=headers, params={"page": page})
       # Process data...
       time.sleep(2)  # Wait 2 seconds between requests
   ```

2. **Use maximum page_size to minimize requests:**
   ```python
   # Good: Fewer requests
   params = {"page": 1, "page_size": 500}
   
   # Less efficient: More requests
   params = {"page": 1, "page_size": 10}
   ```

3. **Handle rate limit errors gracefully:**
   ```python
   import time
   
   def fetch_with_retry(url, headers, params, max_retries=3):
       for attempt in range(max_retries):
           response = requests.get(url, headers=headers, params=params)
           
           if response.status_code == 429:
               wait_time = 60  # Wait 1 minute
               print(f"Rate limited. Waiting {wait_time} seconds...")
               time.sleep(wait_time)
               continue
           
           return response
       
       raise Exception("Max retries exceeded")
   ```

---

## 🔍 Other Useful Endpoints

### Get API Statistics
**Endpoint:** `GET /invoices/stats`

Returns statistics about stored invoices.

```bash
curl -X GET "https://demandlane-analytics-engineer.recursive-tech.site/invoices/stats" \
  -H "Authorization: Bearer <your_token>"
```

**Response:**
```json
{
  "total_invoices": 5000,
  "database_type": "json",
  "storage_location": "data/invoices.json"
}
```

### Health Check
**Endpoint:** `GET /health`

Check if the API is running (no authentication required).

```bash
curl -X GET "https://demandlane-analytics-engineer.recursive-tech.site/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-10-29T10:30:00.000Z"
}
```

### Verify Your Token
**Endpoint:** `GET /auth/verify`

Verify if your access token is still valid.

```bash
curl -X GET "https://demandlane-analytics-engineer.recursive-tech.site/auth/verify" \
  -H "Authorization: Bearer <your_token>"
```

**Response:**
```json
{
  "valid": true,
  "username": "candidate",
  "role": "candidate",
  "email": "candidate@example.com",
  "expires_at": 1730217000
}
```

### Get Your User Information
**Endpoint:** `GET /auth/me`

Get information about your current authenticated user.

```bash
curl -X GET "https://demandlane-analytics-engineer.recursive-tech.site/auth/me" \
  -H "Authorization: Bearer <your_token>"
```

**Response:**
```json
{
  "username": "candidate",
  "email": "candidate@example.com",
  "full_name": "Test Candidate",
  "role": "candidate",
  "disabled": false
}
```

---

## 🐛 Troubleshooting

### 401 Unauthorized Error
**Problem:** Your request is being rejected with `401 Unauthorized`.

**Solutions:**
1. Make sure you include the `Authorization` header
2. Check that you're using `Bearer ` prefix (note the space)
3. Verify your token hasn't expired (tokens expire after 8 hours)
4. Get a new token using `/auth/token` endpoint

### 429 Too Many Requests Error
**Problem:** You're being rate limited.

**Solutions:**
1. Wait 60 seconds before making more requests
2. Reduce your request frequency
3. Use larger `page_size` to fetch more data per request (max 500)

### 400 Bad Request - Page Does Not Exist
**Problem:** Requesting a page number that doesn't exist.

**Solutions:**
1. Check the `total_pages` value in the response
2. Use `has_next` to determine if you can fetch the next page
3. Start from `page=1` and increment until `has_next=false`

---

## 💡 Tips for the Assignment

1. **Handle Inconsistent Data:** The API returns intentionally inconsistent data. Your job is to clean and normalize it.

2. **Efficient Pagination:** Use the maximum `page_size` (500) to minimize the number of API calls.

3. **Error Handling:** Implement proper error handling for rate limits, authentication errors, and network issues.

4. **Data Validation:** Validate and clean the data as you fetch it. Common issues include:
   - Missing fields
   - Type inconsistencies (strings vs numbers)
   - Duplicate records
   - Schema drift across records

5. **Save Your Progress:** Consider saving fetched data to avoid re-fetching due to rate limits.

---

## 🆘 Need Help?

- Review the response metadata (especially `has_next`, `total_pages`) to navigate pagination correctly
- Monitor rate limits and adjust your request frequency accordingly

**Good luck with your assignment! 🚀**
