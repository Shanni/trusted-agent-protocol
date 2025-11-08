#!/usr/bin/env python3
"""
Generate RSA and Ed25519 key pairs for the TAP Agent
"""

from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def generate_rsa_keys():
    """Generate RSA key pair"""
    print("🔑 Generating RSA key pair...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Serialize private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    # Serialize public key to PEM format
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_pem, public_pem

def generate_ed25519_keys():
    """Generate Ed25519 key pair"""
    import base64
    print("🔑 Generating Ed25519 key pair...")
    
    # Generate private key
    private_key = ed25519.Ed25519PrivateKey.generate()
    
    # Get raw 32-byte private key and encode as base64
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    private_b64 = base64.b64encode(private_bytes).decode('utf-8')
    
    # Get raw 32-byte public key and encode as base64
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    public_b64 = base64.b64encode(public_bytes).decode('utf-8')
    
    return private_b64, public_b64

def escape_for_env(key_string):
    """Escape key string for .env file format"""
    # Replace newlines with \n for single-line format
    return key_string.replace('\n', '\\n')

def main():
    print("=" * 60)
    print("TAP Agent Key Generator")
    print("=" * 60)
    print()
    
    # Generate RSA keys
    rsa_private, rsa_public = generate_rsa_keys()
    print("✅ RSA keys generated")
    print()
    
    # Generate Ed25519 keys
    ed25519_private, ed25519_public = generate_ed25519_keys()
    print("✅ Ed25519 keys generated")
    print()
    
    # Create .env file content
    env_content = f"""# TAP Agent Environment Variables
# Generated automatically - DO NOT COMMIT TO VERSION CONTROL

# Merchant API Configuration
MERCHANT_API_URL=http://localhost:8000

# Agent Configuration
AGENT_PORT=8501

# Debug Configuration
DEBUG=true

# RSA Key Pair for HTTP Message Signatures (RFC 9421)
RSA_PRIVATE_KEY="{escape_for_env(rsa_private)}"
RSA_PUBLIC_KEY="{escape_for_env(rsa_public)}"

# Ed25519 Key Pair for HTTP Message Signatures (RFC 9421)
# Keys are base64-encoded raw 32-byte keys
ED25519_PRIVATE_KEY="{ed25519_private}"
ED25519_PUBLIC_KEY="{ed25519_public}"
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("=" * 60)
    print("✅ Keys generated and saved to .env file")
    print("=" * 60)
    print()
    print("📝 RSA Private Key (first 100 chars):")
    print(rsa_private[:100] + "...")
    print()
    print("📝 RSA Public Key (first 100 chars):")
    print(rsa_public[:100] + "...")
    print()
    print("📝 Ed25519 Private Key (base64, 32 bytes):")
    print(ed25519_private)
    print()
    print("📝 Ed25519 Public Key (base64, 32 bytes):")
    print(ed25519_public)
    print()
    print("⚠️  IMPORTANT: Keep your .env file secure and do not commit it to version control!")
    print("✅ You can now run: streamlit run agent_app.py")

if __name__ == "__main__":
    main()
