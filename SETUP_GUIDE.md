# Trusted Agent Protocol - Setup Guide

## Prerequisites

- Python 3.13.0 (via pyenv)
- Node.js (for frontend and CDN proxy)
- pip packages installed from `requirements.txt`

## Quick Setup

### 1. Install Python Dependencies

```bash
# From the root of trusted-agent-protocol
pip install -r requirements.txt
```

✅ **Fixed**: Updated to Python 3.13-compatible versions (see `PYTHON_313_FIX.md`)

### 2. Generate Cryptographic Keys for TAP Agent

The TAP Agent requires RSA and Ed25519 key pairs for signing HTTP messages per RFC 9421.

```bash
cd tap-agent
~/.pyenv/versions/3.13.0/bin/python3 generate_keys.py
```

This will:
- Generate RSA-2048 key pair
- Generate Ed25519 key pair  
- Create `.env` file with all required keys
- The `.env` file is automatically gitignored for security

✅ **Output**: `.env` file created with:
- `RSA_PRIVATE_KEY` and `RSA_PUBLIC_KEY`
- `ED25519_PRIVATE_KEY` and `ED25519_PUBLIC_KEY`
- Default configuration (merchant URL, port, etc.)

### 3. Start the Services

Open 5 terminal windows and run:

#### Terminal 1: Agent Registry (Port 8001)
```bash
cd agent-registry
~/.pyenv/versions/3.13.0/bin/python3 main.py
```

#### Terminal 2: Merchant Backend (Port 8000)
```bash
cd merchant-backend
~/.pyenv/versions/3.13.0/bin/python3 -m uvicorn app.main:app --reload
```

#### Terminal 3: CDN Proxy (Port 3002)
```bash
cd cdn-proxy
npm install
npm start
```

#### Terminal 4: Merchant Frontend (Port 3001)
```bash
cd merchant-frontend
npm install
npm run dev
```

#### Terminal 5: TAP Agent (Port 8501)
```bash
cd tap-agent
~/.pyenv/versions/3.13.0/bin/streamlit run agent_app.py
```

### 4. Access the Demo

- **TAP Agent UI**: http://localhost:8501
- **Merchant Frontend**: http://localhost:3001
- **Merchant Backend API**: http://localhost:8000
- **Agent Registry**: http://localhost:8001

## Configuration

### TAP Agent Environment Variables

Edit `tap-agent/.env` to customize:

```bash
# Merchant API Configuration
MERCHANT_API_URL=http://localhost:8000

# Agent Configuration  
AGENT_PORT=8501

# Debug Configuration
DEBUG=true

# Keys are auto-generated - do not modify unless regenerating
```

### Regenerating Keys

If you need to regenerate keys:

```bash
cd tap-agent
~/.pyenv/versions/3.13.0/bin/python3 generate_keys.py
```

⚠️ **Warning**: This will overwrite your existing `.env` file!

## Troubleshooting

### Python Module Not Found

If you see `ModuleNotFoundError`, ensure you're using the pyenv Python:

```bash
# Check which Python is being used
which python3

# Should be: /Users/shanliu/.pyenv/versions/3.13.0/bin/python3
# If not, use the full path or configure pyenv in your shell
```

### RSA_PRIVATE_KEY Error

If you see `ValueError: RSA_PRIVATE_KEY and RSA_PUBLIC_KEY must be set`:

1. Make sure you're in the `tap-agent` directory
2. Run the key generation script: `python3 generate_keys.py`
3. Verify `.env` file exists: `ls -la .env`

### Port Already in Use

If a port is already in use, either:
1. Stop the existing process
2. Change the port in the respective configuration file

## Security Notes

- ✅ `.env` files are gitignored by default
- ⚠️ Never commit private keys to version control
- 🔒 Keys are used for cryptographic signatures per RFC 9421
- 🔑 Each agent should have unique key pairs in production

## Next Steps

1. Open the TAP Agent at http://localhost:8501
2. Configure the merchant URL (default: http://localhost:3001)
3. Generate signatures and test the protocol
4. Review the signature verification in the CDN Proxy logs

For detailed component documentation, see:
- [TAP Agent README](./tap-agent/README.md)
- [Merchant Backend README](./merchant-backend/README.md)
- [Agent Registry README](./agent-registry/README.md)
