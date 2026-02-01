#!/bin/bash

# Neo4j NLP Query Setup Script
# This script helps you set up the project quickly

echo "🚀 Setting up Neo4j NLP Query Generator..."
echo ""

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "❌ Python 3.8 or higher is required. You have Python $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip upgraded"
echo ""

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your actual credentials:"
    echo "   - NEO4J_URI"
    echo "   - NEO4J_USERNAME"
    echo "   - NEO4J_PASSWORD"
    echo "   - GROQ_API_KEY"
    echo ""
else
    echo "ℹ️  .env file already exists"
    echo ""
fi

echo "🎉 Setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Edit .env file with your credentials"
echo "   2. Run: streamlit run app.py"
echo "   3. Open http://localhost:8501 in your browser"
echo ""
echo "🔗 Useful links:"
echo "   - Get Neo4j AuraDB: https://neo4j.com/cloud/aura/"
echo "   - Get Groq API Key: https://console.groq.com/"
echo ""
echo "Happy querying! 🚀"