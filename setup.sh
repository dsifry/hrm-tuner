#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "  HRM Tuner Setup"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if venv exists
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✓ Setup Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Now run the analysis with:"
echo "  ./quick-start.sh"
echo ""
