#!/bin/bash
# Verify TAP Agent setup is complete

echo "🔍 Verifying Trusted Agent Protocol Setup..."
echo "=============================================="
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
PYTHON_VERSION=$(~/.pyenv/versions/3.13.0/bin/python3 --version 2>&1)
echo "   ✅ $PYTHON_VERSION"
echo ""

# Check if packages are installed
echo "2️⃣  Checking Python packages..."
if ~/.pyenv/versions/3.13.0/bin/python3 -c "import pydantic, fastapi, streamlit, cryptography" 2>/dev/null; then
    echo "   ✅ All required packages installed"
    PYDANTIC_VER=$(~/.pyenv/versions/3.13.0/bin/python3 -c "import pydantic; print(pydantic.__version__)")
    FASTAPI_VER=$(~/.pyenv/versions/3.13.0/bin/python3 -c "import fastapi; print(fastapi.__version__)")
    echo "      - pydantic: $PYDANTIC_VER"
    echo "      - fastapi: $FASTAPI_VER"
else
    echo "   ❌ Some packages missing. Run: pip install -r requirements.txt"
    exit 1
fi
echo ""

# Check if .env exists
echo "3️⃣  Checking TAP Agent configuration..."
if [ -f "tap-agent/.env" ]; then
    echo "   ✅ .env file exists"
    
    # Verify keys are loaded
    cd tap-agent
    if ~/.pyenv/versions/3.13.0/bin/python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); exit(0 if os.getenv('RSA_PRIVATE_KEY') and os.getenv('RSA_PUBLIC_KEY') else 1)" 2>/dev/null; then
        echo "   ✅ RSA keys configured"
    else
        echo "   ❌ RSA keys not found in .env"
        exit 1
    fi
    
    if ~/.pyenv/versions/3.13.0/bin/python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); exit(0 if os.getenv('ED25519_PRIVATE_KEY') and os.getenv('ED25519_PUBLIC_KEY') else 1)" 2>/dev/null; then
        echo "   ✅ Ed25519 keys configured"
    else
        echo "   ❌ Ed25519 keys not found in .env"
        exit 1
    fi
    cd ..
else
    echo "   ❌ .env file not found"
    echo "   💡 Run: cd tap-agent && python3 generate_keys.py"
    exit 1
fi
echo ""

# Check if generate_keys.py exists
echo "4️⃣  Checking key generation script..."
if [ -f "tap-agent/generate_keys.py" ]; then
    echo "   ✅ generate_keys.py available"
else
    echo "   ❌ generate_keys.py not found"
    exit 1
fi
echo ""

# Summary
echo "=============================================="
echo "✅ Setup verification complete!"
echo ""
echo "🚀 Ready to start services:"
echo ""
echo "   TAP Agent:"
echo "   $ ./start-tap-agent.sh"
echo "   or"
echo "   $ cd tap-agent && streamlit run agent_app.py"
echo ""
echo "   Agent Registry:"
echo "   $ cd agent-registry && python main.py"
echo ""
echo "   Merchant Backend:"
echo "   $ cd merchant-backend && python -m uvicorn app.main:app --reload"
echo ""
echo "📚 See SETUP_GUIDE.md for complete instructions"
