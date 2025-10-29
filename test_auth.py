"""
Test script for Bearer Token Authentication.
Demonstrates how to use the authentication system.
"""

import requests
import json
from typing import Optional


BASE_URL = "http://localhost:8000"


class AuthenticatedClient:
    """API client with Bearer Token authentication."""
    
    def __init__(self, api_key: str):
        self.base_url = BASE_URL
        self.api_key = api_key
        self.token: Optional[str] = None
    
    def generate_token(self, expires_in_minutes: int = 60) -> str:
        """Generate a new Bearer token."""
        print(f"\n🔐 Generating token with API key: {self.api_key}")
        
        response = requests.post(
            f"{self.base_url}/auth/token",
            json={
                "api_key": self.api_key,
                "expires_in_minutes": expires_in_minutes
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['access_token']
            print(f"✅ Token generated successfully")
            print(f"   Expires in: {data['expires_in']} minutes")
            print(f"   Token (first 50 chars): {self.token[:50]}...")
            return self.token
        else:
            print(f"❌ Failed to generate token: {response.status_code}")
            print(f"   Error: {response.text}")
            raise Exception(f"Token generation failed: {response.text}")
    
    def verify_token(self) -> dict:
        """Verify if the current token is valid."""
        if not self.token:
            raise Exception("No token available. Call generate_token() first.")
        
        print(f"\n🔍 Verifying token...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/auth/verify", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token is valid")
            print(f"   {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Token verification failed: {response.status_code}")
            print(f"   Error: {response.text}")
            raise Exception(f"Token verification failed: {response.text}")
    
    def get_headers(self) -> dict:
        """Get headers with Bearer token."""
        if not self.token:
            self.generate_token()
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_invoices(self, count: int = 5, store: bool = False) -> dict:
        """Fetch invoices (requires auth if ENABLE_AUTH=True)."""
        print(f"\n📧 Fetching {count} invoices...")
        
        headers = self.get_headers()
        response = requests.get(
            f"{self.base_url}/invoices",
            params={"count": count, "store": store},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully fetched {data['count']} invoices")
            return data
        else:
            print(f"❌ Failed to fetch invoices: {response.status_code}")
            print(f"   Error: {response.text}")
            raise Exception(f"Failed to fetch invoices: {response.text}")
    
    def seed_database(self, count: int = 10) -> dict:
        """Seed database (requires auth if ENABLE_AUTH=True)."""
        print(f"\n🌱 Seeding database with {count} invoices...")
        
        headers = self.get_headers()
        response = requests.post(
            f"{self.base_url}/invoices/seed",
            params={"count": count},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            return data
        else:
            print(f"❌ Failed to seed database: {response.status_code}")
            print(f"   Error: {response.text}")
            raise Exception(f"Failed to seed database: {response.text}")
    
    def clear_database(self) -> dict:
        """Clear database (requires auth if ENABLE_AUTH=True)."""
        print(f"\n🗑️  Clearing database...")
        
        headers = self.get_headers()
        response = requests.delete(
            f"{self.base_url}/invoices/stored",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            return data
        else:
            print(f"❌ Failed to clear database: {response.status_code}")
            print(f"   Error: {response.text}")
            raise Exception(f"Failed to clear database: {response.text}")


def test_without_auth():
    """Test API access without authentication."""
    print("\n" + "="*80)
    print("  TEST 1: Access without Authentication")
    print("="*80)
    
    print("\nTrying to access /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        print("✅ Public endpoint accessible (as expected)")
        data = response.json()
        print(f"   App: {data['app_name']} v{data['version']}")
    else:
        print(f"❌ Failed: {response.status_code}")


def test_with_auth():
    """Test API access with Bearer token authentication."""
    print("\n" + "="*80)
    print("  TEST 2: Access with Bearer Token Authentication")
    print("="*80)
    
    # Create authenticated client
    client = AuthenticatedClient(api_key="demo-api-key-12345")
    
    try:
        # Generate token
        client.generate_token(expires_in_minutes=60)
        
        # Verify token
        client.verify_token()
        
        # Use token to access endpoints
        client.get_invoices(count=3, store=True)
        
        # Seed database
        client.seed_database(count=5)
        
        # Get stats (public endpoint, but we'll use token anyway)
        headers = client.get_headers()
        response = requests.get(f"{BASE_URL}/invoices/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 Database stats:")
            print(f"   Total invoices: {stats['total_invoices']}")
            print(f"   Database type: {stats['database_type']}")
        
        # Clear database
        client.clear_database()
        
        print("\n" + "="*80)
        print("  ✅ All authenticated operations completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")


def test_invalid_api_key():
    """Test with invalid API key."""
    print("\n" + "="*80)
    print("  TEST 3: Invalid API Key")
    print("="*80)
    
    print("\nTrying to generate token with invalid API key...")
    response = requests.post(
        f"{BASE_URL}/auth/token",
        json={"api_key": "invalid-key-xyz"}
    )
    
    if response.status_code == 401:
        print("✅ Correctly rejected invalid API key")
        print(f"   Error message: {response.json()['detail']}")
    else:
        print(f"❌ Unexpected response: {response.status_code}")


def test_expired_token():
    """Test with very short-lived token."""
    print("\n" + "="*80)
    print("  TEST 4: Token Expiration (Demo)")
    print("="*80)
    
    print("\nGenerating token with 1 minute expiration...")
    client = AuthenticatedClient(api_key="demo-api-key-12345")
    client.generate_token(expires_in_minutes=1)
    
    print("\n💡 Token will expire in 1 minute")
    print("   In production, you would need to regenerate the token after expiration")


def main():
    """Run all authentication tests."""
    print("\n" + "="*80)
    print("  ANALYTICS ENGINEER API - AUTHENTICATION TEST SUITE")
    print("="*80)
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("\n❌ Server not responding correctly")
            return
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print("   Please ensure the server is running on http://localhost:8000")
        return
    
    # Check if authentication is enabled
    print("\n📋 Checking authentication status...")
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    print(f"   API: {data['app_name']}")
    print(f"   Version: {data['version']}")
    
    # Run tests
    test_without_auth()
    test_with_auth()
    test_invalid_api_key()
    test_expired_token()
    
    print("\n" + "="*80)
    print("  🎉 All authentication tests completed!")
    print("="*80)
    
    print("\n📚 Documentation:")
    print("   • Full security guide: See SECURITY.md")
    print("   • API documentation: http://localhost:8000/docs")
    print("   • Authentication endpoints: /auth/token and /auth/verify")
    
    print("\n💡 Quick Tips:")
    print("   • Authentication is DISABLED by default (ENABLE_AUTH=False)")
    print("   • To enable: Set ENABLE_AUTH=True in .env file")
    print("   • Demo API keys: demo-api-key-12345, test-key-67890")
    print("   • Token format: Authorization: Bearer <your-token>")
    
    print("\n🔒 To enable authentication:")
    print("   1. Edit .env: ENABLE_AUTH=True")
    print("   2. Restart the server")
    print("   3. Generate token: POST /auth/token")
    print("   4. Use token in Authorization header")


if __name__ == "__main__":
    main()
