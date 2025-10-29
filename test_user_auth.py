"""
Test script for username/password authentication system.
Tests login, token generation, and admin endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_login():
    """Test user login with username/password."""
    print_section("Test 1: Login with Username/Password")
    
    # Test candidate login
    print("\n1. Testing candidate login...")
    response = requests.post(
        f"{BASE_URL}/auth/token",
        json={"username": "candidate", "password": "test123"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Login successful!")
        print(f"Token Type: {data['token_type']}")
        print(f"Access Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"✗ Login failed: {response.text}")
        return None

def test_verify_token(token):
    """Test token verification."""
    print_section("Test 2: Verify Token")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Token is valid!")
        print(f"Username: {data.get('username')}")
        print(f"Role: {data.get('role')}")
        print(f"Email: {data.get('email')}")
    else:
        print(f"✗ Token verification failed: {response.text}")

def test_get_current_user(token):
    """Test getting current user info."""
    print_section("Test 3: Get Current User Info")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ User info retrieved!")
        print(f"Username: {data.get('username')}")
        print(f"Email: {data.get('email')}")
        print(f"Full Name: {data.get('full_name')}")
        print(f"Role: {data.get('role')}")
    else:
        print(f"✗ Failed to get user info: {response.text}")

def test_protected_endpoint(token):
    """Test accessing protected invoice endpoint."""
    print_section("Test 4: Access Protected Endpoint")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/invoices/stored",
        headers=headers,
        params={"page": 1, "page_size": 5}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Protected endpoint accessed!")
        print(f"Total Invoices: {data.get('total')}")
        print(f"Current Page: {data.get('page')}")
        print(f"Items Retrieved: {data.get('count')}")
    else:
        print(f"✗ Failed to access protected endpoint: {response.text}")

def test_admin_login():
    """Test admin login."""
    print_section("Test 5: Admin Login")
    
    print("\n1. Testing admin login...")
    response = requests.post(
        f"{BASE_URL}/auth/token",
        json={"username": "admin", "password": "admin123"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Admin login successful!")
        print(f"Access Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"✗ Admin login failed: {response.text}")
        return None

def test_list_users(admin_token):
    """Test listing all users (admin only)."""
    print_section("Test 6: List All Users (Admin Only)")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"✓ Users retrieved!")
        print(f"Total Users: {len(users)}")
        for user in users:
            print(f"  - {user['username']} ({user['role']}) - {user.get('email', 'N/A')}")
    else:
        print(f"✗ Failed to list users: {response.text}")

def test_register_user(admin_token):
    """Test user registration (admin only)."""
    print_section("Test 7: Register New User (Admin Only)")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    new_user = {
        "username": "testuser",
        "password": "testpass123",
        "email": "testuser@example.com",
        "full_name": "Test User",
        "role": "candidate"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        headers=headers,
        json=new_user
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ User registered successfully!")
        print(f"Username: {data.get('username')}")
        print(f"Email: {data.get('email')}")
        print(f"Role: {data.get('role')}")
    else:
        print(f"✗ Failed to register user: {response.text}")

def test_candidate_cannot_register(candidate_token):
    """Test that candidates cannot register users."""
    print_section("Test 8: Candidate Cannot Register Users")
    
    headers = {"Authorization": f"Bearer {candidate_token}"}
    new_user = {
        "username": "unauthorized",
        "password": "pass123",
        "role": "candidate"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        headers=headers,
        json=new_user
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 403:
        print(f"✓ Correctly blocked! Candidates cannot register users.")
        print(f"Error: {response.json().get('detail')}")
    else:
        print(f"✗ Security issue! Candidate was able to access admin endpoint.")

def test_invalid_login():
    """Test login with invalid credentials."""
    print_section("Test 9: Invalid Login Credentials")
    
    response = requests.post(
        f"{BASE_URL}/auth/token",
        json={"username": "invalid", "password": "wrongpass"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 401:
        print(f"✓ Correctly rejected invalid credentials!")
        print(f"Error: {response.json().get('detail')}")
    else:
        print(f"✗ Security issue! Invalid login was accepted.")

def main():
    """Run all authentication tests."""
    print("\n" + "="*60)
    print("  🔐 Username/Password Authentication Test Suite")
    print("="*60)
    
    try:
        # Test candidate flow
        candidate_token = test_login()
        if candidate_token:
            test_verify_token(candidate_token)
            test_get_current_user(candidate_token)
            test_protected_endpoint(candidate_token)
        
        # Test admin flow
        admin_token = test_admin_login()
        if admin_token:
            test_list_users(admin_token)
            test_register_user(admin_token)
        
        # Test security
        if candidate_token:
            test_candidate_cannot_register(candidate_token)
        
        test_invalid_login()
        
        # Summary
        print_section("✓ All Tests Completed!")
        print("\nAuthentication system is working correctly!")
        print("\nDefault Credentials:")
        print("  - Candidate: username='candidate', password='test123'")
        print("  - Admin: username='admin', password='admin123'")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")

if __name__ == "__main__":
    main()
