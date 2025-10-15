#!/bin/bash

# Setup script for Pressure Relief Valve LLM Agent

echo "================================================"
echo "  Pressure Relief Valve LLM Agent - Setup"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
    echo "Error: Python 3.8 or higher is required"
    echo "Current version: $(python3 --version)"
    exit 1
fi

echo "✓ Python version OK: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "(This may take a few minutes...)"
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "✗ Error installing dependencies"
    exit 1
fi
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p data/uploads data/cache models logs
touch data/uploads/.gitkeep data/cache/.gitkeep models/.gitkeep
echo "✓ Directories created"
echo ""

# Create sample dataset
echo "Creating sample dataset..."
python3 main.py --create-sample > /dev/null 2>&1
echo "✓ Sample dataset created"
echo ""

echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "To get started:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the demo:"
echo "     python demo.py"
echo ""
echo "  3. Or start interactive mode:"
echo "     python main.py --interactive"
echo ""
echo "  4. Or start the web API:"
echo "     python api.py"
echo ""
echo "For more information, see README.md"
echo ""
