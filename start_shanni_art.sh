#!/bin/bash

# TAP Shanni Art Gallery - Quick Start Script
# This script seeds the database and provides instructions to start all services

echo "🎨 TAP Shanni Art Gallery - Setup"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -d "merchant-backend" ]; then
    echo "❌ Error: Please run this script from the trusted-agent-protocol directory"
    exit 1
fi

# Seed the database with Shanni Art products
echo "📦 Seeding database with Shanni Art products..."
cd merchant-backend
python seed_shanni_art.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database seeded successfully!"
    echo ""
    echo "🚀 To start the TAP Shanni Art Gallery, run these commands in separate terminals:"
    echo ""
    echo "Terminal 1 - Backend:"
    echo "  cd merchant-backend && python main.py"
    echo ""
    echo "Terminal 2 - Frontend:"
    echo "  cd merchant-frontend && npm start"
    echo ""
    echo "Terminal 3 - CDN Proxy:"
    echo "  cd cdn-proxy && node server.js"
    echo ""
    echo "Terminal 4 - Agent Registry:"
    echo "  cd agent-registry && python main.py"
    echo ""
    echo "Optional - TAP Agent (for automated shopping):"
    echo "  cd tap-agent && streamlit run agent_app_v3.py"
    echo ""
    echo "🌐 Once started, visit:"
    echo "  Gallery: http://localhost:3000"
    echo "  Agent:   http://localhost:8501"
    echo ""
    echo "🎨 Enjoy the Shanni Art Gallery!"
else
    echo ""
    echo "❌ Error seeding database. Please check the error messages above."
    exit 1
fi
