# RSA Key Generation - Summary

## Problem Solved

The TAP Agent requires RSA and Ed25519 cryptographic key pairs to sign HTTP messages according to RFC 9421 (HTTP Message Signatures). These keys were missing from the environment variables.

## Solution Implemented

### 1. Created Key Generation Script

**File**: `tap-agent/generate_keys.py`

This script:
- Generates a 2048-bit RSA key pair using `cryptography` library
- Generates an Ed25519 key pair for alternative signing algorithm
- Exports keys in PEM format
- Creates a `.env` file with properly formatted keys
- Escapes newlines for environment variable compatibility

### 2. Generated Keys

**Command**:
```bash
cd tap-agent
~/.pyenv/versions/3.13.0/bin/python3 generate_keys.py
```

**Output**:
- ✅ RSA private key (1704 characters)
- ✅ RSA public key (451 characters)
- ✅ Ed25519 private key
- ✅ Ed25519 public key
- ✅ `.env` file created with all keys

### 3. Security Measures

- ✅ `.env` file is in `.gitignore` (already configured)
- ✅ Keys are never committed to version control
- ✅ Each environment should generate unique keys
- ✅ Keys are used for RFC 9421 HTTP Message Signatures

## Key Format

Keys are stored in PEM format and escaped for environment variables:

```bash
# Example format in .env
RSA_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgk...\n-----END PRIVATE KEY-----\n"
RSA_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhki...\n-----END PUBLIC KEY-----\n"
```

## How It Works

### RFC 9421 HTTP Message Signatures

The TAP Agent uses these keys to:

1. **Sign HTTP requests** with cryptographic signatures
2. **Prove agent identity** to merchants
3. **Prevent replay attacks** using nonces and timestamps
4. **Bind signatures to specific domains** and paths

### Signature Components

```
Signature-Input: sig2=("@authority" "@path"); created=1234567890; expires=1234567900; keyId="agent-key-1"; alg="rsa-pss-sha256"; nonce="abc123"; tag="payment"
Signature: sig2=:BASE64_ENCODED_SIGNATURE:
```

## Usage

### Starting the TAP Agent

```bash
cd tap-agent
~/.pyenv/versions/3.13.0/bin/streamlit run agent_app.py
```

The agent will:
1. Load keys from `.env` file
2. Use RSA-PSS-SHA256 algorithm for signing
3. Generate RFC 9421 compliant signatures
4. Send signed requests to merchants

### Verifying Keys Are Loaded

```bash
cd tap-agent
~/.pyenv/versions/3.13.0/bin/python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Keys loaded:', bool(os.getenv('RSA_PRIVATE_KEY')))"
```

## Regenerating Keys

If you need to regenerate keys (e.g., for security rotation):

```bash
cd tap-agent
~/.pyenv/versions/3.13.0/bin/python3 generate_keys.py
```

⚠️ **Warning**: This will overwrite your existing `.env` file!

## Files Created/Modified

### New Files
- ✅ `tap-agent/generate_keys.py` - Key generation script
- ✅ `tap-agent/.env` - Environment variables with keys (gitignored)
- ✅ `SETUP_GUIDE.md` - Complete setup instructions
- ✅ `KEY_GENERATION_SUMMARY.md` - This file

### Existing Files (Not Modified)
- `tap-agent/.env.example` - Template file
- `tap-agent/.gitignore` - Already includes `.env`
- `tap-agent/agent_app.py` - Uses keys from environment

## Next Steps

1. ✅ Keys are generated and ready
2. ✅ Environment variables are configured
3. ✅ TAP Agent can now start successfully
4. 🚀 Ready to run the full demo

Start all services as documented in `SETUP_GUIDE.md` or the main `README.md`.

## Technical Details

### RSA Key Specifications
- **Algorithm**: RSA
- **Key Size**: 2048 bits
- **Public Exponent**: 65537
- **Format**: PKCS#8 PEM
- **Signature Algorithm**: RSA-PSS-SHA256

### Ed25519 Key Specifications
- **Algorithm**: Ed25519 (Edwards-curve Digital Signature Algorithm)
- **Key Size**: 256 bits
- **Format**: PKCS#8 PEM
- **Use Case**: Alternative signing algorithm (faster, smaller signatures)

### Why Two Key Types?

The protocol supports multiple signing algorithms:
- **RSA-PSS-SHA256**: Widely supported, industry standard
- **Ed25519**: Modern, faster, smaller signatures

Merchants can verify either type based on their capabilities.
