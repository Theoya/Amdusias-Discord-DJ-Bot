#!/bin/bash

echo "========================================"
echo "  Amdusias Discord DJ Bot"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run setup first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ".env file not found!"
    echo "Please copy .env.example to .env and configure it."
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting bot..."
echo ""
python main.py
