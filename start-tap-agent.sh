#!/bin/bash
# Start TAP Agent with the correct Python environment

echo "🚀 Starting TAP Agent..."
echo "📍 Using Python: ~/.pyenv/versions/3.13.0/bin/python3"
echo "🌐 Agent will be available at: http://localhost:8501"
echo ""

cd "$(dirname "$0")/tap-agent"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "🔑 Generating keys..."
    ~/.pyenv/versions/3.13.0/bin/python3 generate_keys.py
    echo ""
fi

# Start streamlit
~/.pyenv/versions/3.13.0/bin/streamlit run agent_app.py
