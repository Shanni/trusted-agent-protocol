#!/usr/bin/env python3
"""
Sync TAP Agent's Ed25519 public key to the Agent Registry

This script reads the ED25519_PUBLIC_KEY from tap-agent/.env and updates
the agent registry to use the correct public key for signature verification.
"""

import os
import requests
from dotenv import load_dotenv

# Load TAP Agent's environment variables
tap_agent_env_path = os.path.join(os.path.dirname(__file__), 'tap-agent', '.env')
load_dotenv(tap_agent_env_path)

# Get the public key from TAP agent
ed25519_public_key = os.getenv('ED25519_PUBLIC_KEY')

if not ed25519_public_key:
    print("❌ ED25519_PUBLIC_KEY not found in tap-agent/.env")
    print("   Run: cd tap-agent && python generate_keys.py")
    exit(1)

print(f"✅ Found ED25519_PUBLIC_KEY in tap-agent/.env")
print(f"   Public Key: {ed25519_public_key[:20]}...")

# Agent Registry configuration
AGENT_REGISTRY_URL = "http://localhost:9002"
AGENT_ID = 1  # TAP Agent 1
KEY_ID = "primary-ed25519"

print(f"\n🔄 Syncing key to Agent Registry...")
print(f"   Agent ID: {AGENT_ID}")
print(f"   Key ID: {KEY_ID}")

# Step 1: Delete the old key if it exists
try:
    delete_response = requests.delete(
        f"{AGENT_REGISTRY_URL}/agents/{AGENT_ID}/keys/{KEY_ID}"
    )
    if delete_response.status_code == 200:
        print(f"✅ Deleted old key '{KEY_ID}'")
    elif delete_response.status_code == 404:
        print(f"ℹ️  No existing key '{KEY_ID}' to delete")
    else:
        print(f"⚠️  Warning: Could not delete old key (status {delete_response.status_code})")
except Exception as e:
    print(f"⚠️  Warning: Error deleting old key: {e}")

# Step 2: Add the new key
try:
    key_data = {
        "key_id": KEY_ID,
        "public_key": ed25519_public_key,
        "algorithm": "ed25519",
        "description": "Primary Ed25519 signing key (synced from TAP agent)",
        "is_active": "true"
    }
    
    add_response = requests.post(
        f"{AGENT_REGISTRY_URL}/agents/{AGENT_ID}/keys",
        json=key_data
    )
    
    if add_response.status_code == 200:
        print(f"✅ Successfully added new key '{KEY_ID}'")
        result = add_response.json()
        print(f"\n📋 Key Details:")
        print(f"   Key ID: {result['key']['key_id']}")
        print(f"   Algorithm: {result['key']['algorithm']}")
        print(f"   Public Key: {result['key']['public_key'][:30]}...")
        print(f"   Status: {'Active' if result['key']['is_active'] == 'true' else 'Inactive'}")
        print(f"\n✅ Sync complete! TAP Agent can now verify signatures with the CDN proxy.")
    else:
        print(f"❌ Failed to add key (status {add_response.status_code})")
        print(f"   Response: {add_response.text}")
        exit(1)
        
except Exception as e:
    print(f"❌ Error adding key: {e}")
    exit(1)

# Step 3: Verify the key was added correctly
try:
    verify_response = requests.get(f"{AGENT_REGISTRY_URL}/keys/{KEY_ID}")
    if verify_response.status_code == 200:
        key_info = verify_response.json()
        if key_info['public_key'] == ed25519_public_key:
            print(f"\n✅ Verification successful! Key matches TAP agent's public key.")
        else:
            print(f"\n⚠️  Warning: Key in registry doesn't match TAP agent's key!")
            print(f"   TAP Agent: {ed25519_public_key[:30]}...")
            print(f"   Registry:  {key_info['public_key'][:30]}...")
    else:
        print(f"\n⚠️  Could not verify key (status {verify_response.status_code})")
except Exception as e:
    print(f"\n⚠️  Error verifying key: {e}")

print(f"\n🎉 Done! You can now test signature verification:")
print(f"   1. Start all services (agent-registry, cdn-proxy, merchant-backend, tap-agent)")
print(f"   2. In TAP Agent, click '🔄 Reset to Default JSON'")
print(f"   3. Click 'Generate Signature & Launch Browser'")
print(f"   4. The signature should now verify successfully!")
