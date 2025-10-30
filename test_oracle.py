#!/usr/bin/env python3
"""
Test script for oracle service.
Verifies that the oracle API is working correctly.
"""

import time
import subprocess
import sys
import requests
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from loggerheads.oracle_client import get_oracle_client


def test_oracle_service():
    """Test complete oracle service."""

    print("\n" + "="*70)
    print("🧪 TESTING ORACLE SERVICE")
    print("="*70)

    # Start oracle service
    print("\n1️⃣  Starting oracle service...")
    oracle_process = subprocess.Popen(
        ['python3', 'oracle_service/app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for service to start
    print("   Waiting for service to initialize...")
    time.sleep(5)

    try:
        # Test 1: Health check
        print("\n2️⃣  Testing health endpoint...")
        try:
            response = requests.get('http://localhost:5001/health', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check passed")
                print(f"   Oracle: {data['oracle_pubkey'][:16]}...{data['oracle_pubkey'][-8:]}")
                print(f"   Status: {data['status']}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Cannot connect to oracle: {e}")
            return False

        # Test 2: Get oracle pubkey
        print("\n3️⃣  Testing oracle-pubkey endpoint...")
        try:
            response = requests.get('http://localhost:5001/oracle-pubkey', timeout=5)
            if response.status_code == 200:
                data = response.json()
                oracle_pubkey = data['oracle_pubkey']
                print(f"   ✅ Oracle pubkey retrieved")
                print(f"   Pubkey: {oracle_pubkey[:16]}...{oracle_pubkey[-8:]}")
            else:
                print(f"   ❌ Failed to get oracle pubkey: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

        # Test 3: Oracle client
        print("\n4️⃣  Testing oracle client...")
        try:
            client = get_oracle_client('http://localhost:5001')
            health = client.health_check()
            print(f"   ✅ Oracle client working")
            print(f"   Client connected to: {health['oracle_pubkey'][:16]}...")
        except Exception as e:
            print(f"   ❌ Oracle client error: {e}")
            return False

        # Test 4: Test vault status (will fail without vault, but tests endpoint)
        print("\n5️⃣  Testing vault-status endpoint...")
        try:
            response = requests.post(
                'http://localhost:5001/vault-status',
                json={
                    'employee_wallet': 'HzVwVx8WEz8F9xrQmVVWXk9yQqCj3mGkT8Sd8uDMhEXU',
                    'admin_wallet': '4KcYcbhrgzFgKSD5o76hwEE3BLcAUMtVGxHGMKV6vDiS'
                },
                timeout=10
            )
            data = response.json()
            if response.status_code == 404:
                print(f"   ✅ Vault-status endpoint working (vault not found, as expected)")
            elif response.status_code == 200:
                print(f"   ✅ Vault-status endpoint working (vault found!)")
            else:
                print(f"   ⚠️  Unexpected response: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\n🎉 Oracle service is working correctly!")
        print("\n📋 Next steps:")
        print("   1. Keep oracle running: python3 oracle_service/app.py")
        print("   2. Create vault: loggerheads (choose Employer)")
        print("   3. Setup employee: loggerheads (choose Employee)")
        print("   4. Start tracking: loggerheads start")
        print("   5. Submit hours: loggerheads submit")
        print("\n" + "="*70)

        return True

    finally:
        # Stop oracle service
        print("\n🛑 Stopping oracle service...")
        oracle_process.terminate()
        try:
            oracle_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            oracle_process.kill()
        print("   ✓ Oracle stopped")


if __name__ == '__main__':
    success = test_oracle_service()
    sys.exit(0 if success else 1)
