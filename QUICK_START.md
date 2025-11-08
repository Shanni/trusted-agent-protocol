# Quick Start Guide

## ✅ Setup Complete!

All cryptographic keys have been generated and the environment is configured.

## 🚀 Start the TAP Agent

### Option 1: Use the helper script
```bash
./start-tap-agent.sh
```

### Option 2: Manual start
```bash
cd tap-agent
~/.pyenv/versions/3.13.0/bin/streamlit run agent_app.py
```

The agent will be available at: **http://localhost:8501**

## 📋 What Was Set Up

### 1. Python 3.13 Compatibility ✅
- Updated `pydantic` from 2.5.0 → 2.10.3
- Updated `fastapi` from 0.104.1 → 0.115.6
- Updated `uvicorn` from 0.24.0 → 0.34.0
- Updated `sqlalchemy` from 2.0.23 → 0.36

### 2. Cryptographic Keys Generated ✅
- **RSA-2048 key pair** for HTTP message signatures
- **Ed25519 key pair** for alternative signing algorithm
- Keys stored in `tap-agent/.env` (gitignored)

### 3. Helper Scripts Created ✅
- `generate_keys.py` - Generate new cryptographic keys
- `start-tap-agent.sh` - Start the agent with correct Python
- `verify-setup.sh` - Verify setup is complete

## 🔍 Verify Setup

Run the verification script:
```bash
./verify-setup.sh
```

Expected output:
```
✅ Python 3.13.0
✅ All required packages installed
✅ RSA keys configured
✅ Ed25519 keys configured
✅ Setup verification complete!
```

## 📚 Full System Demo

To run the complete Trusted Agent Protocol demo:

### Terminal 1: Agent Registry (Port 8001)
```bash
cd agent-registry
~/.pyenv/versions/3.13.0/bin/python3 main.py
```

### Terminal 2: Merchant Backend (Port 8000)
```bash
cd merchant-backend
~/.pyenv/versions/3.13.0/bin/python3 -m uvicorn app.main:app --reload
```

### Terminal 3: CDN Proxy (Port 3002)
```bash
cd cdn-proxy
npm install
npm start
```

### Terminal 4: Merchant Frontend (Port 3001)
```bash
cd merchant-frontend
npm install
npm run dev
```

### Terminal 5: TAP Agent (Port 8501)
```bash
./start-tap-agent.sh
```

## 🌐 Access Points

- **TAP Agent UI**: http://localhost:8501
- **Merchant Frontend**: http://localhost:3001
- **Merchant Backend API**: http://localhost:8000/docs
- **Agent Registry**: http://localhost:8001

## 🔑 Key Management

### View Current Keys
```bash
cd tap-agent
cat .env
```

### Regenerate Keys
```bash
cd tap-agent
~/.pyenv/versions/3.13.0/bin/python3 generate_keys.py
```

⚠️ **Warning**: This will overwrite your existing `.env` file!

## 🛠️ Troubleshooting

### "Module not found" errors
Make sure you're using the pyenv Python:
```bash
~/.pyenv/versions/3.13.0/bin/python3 --version
# Should show: Python 3.13.0
```

### "RSA_PRIVATE_KEY must be set" error
Regenerate keys:
```bash
cd tap-agent
~/.pyenv/versions/3.13.0/bin/python3 generate_keys.py
```

### Port already in use
Check what's running on the port:
```bash
lsof -i :8501  # For TAP Agent
lsof -i :8000  # For Merchant Backend
lsof -i :8001  # For Agent Registry
```

## 📖 Documentation

- **SETUP_GUIDE.md** - Detailed setup instructions
- **KEY_GENERATION_SUMMARY.md** - Technical details about keys
- **PYTHON_313_FIX.md** - Python 3.13 compatibility fix
- **README.md** - Main project documentation

## 🎯 Next Steps

1. Start the TAP Agent: `./start-tap-agent.sh`
2. Open http://localhost:8501 in your browser
3. Configure merchant URL (default: http://localhost:3001)
4. Generate and test RFC 9421 signatures
5. Explore the protocol implementation

## 🔒 Security Notes

- ✅ `.env` files are gitignored
- ✅ Never commit private keys
- ✅ Each environment should have unique keys
- ✅ Keys are used for RFC 9421 HTTP Message Signatures

---

**Ready to go!** 🚀

Run `./start-tap-agent.sh` to begin.
