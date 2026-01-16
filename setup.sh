#!/bin/bash

# Location Analytics - Quick Setup Script
# This script sets up the entire project and generates all necessary data

echo "=================================="
echo "Location Analytics Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 not found. Please install Python 3.9+"; exit 1; }
echo "✓ Python found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || { echo "Failed to activate venv. Run manually: source venv/bin/activate"; exit 1; }
echo "✓ Virtual environment activated"
echo ""

# Install requirements
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Generate data
echo "Generating synthetic location data..."
python generate_location_data.py
echo "✓ Data generated"
echo ""

# Run queries
echo "Creating DuckDB database and running queries..."
python queries.py
echo "✓ Database created"
echo ""

# Run spatial analysis
echo "Performing geospatial analysis..."
python spatial_analysis.py
echo "✓ Spatial analysis complete"
echo ""

echo "=================================="
echo "Setup Complete! 🎉"
echo "=================================="
echo ""
echo "To launch the dashboard, run:"
echo "  streamlit run app.py"
echo ""
echo "Or if you need to activate the environment first:"
echo "  source venv/bin/activate"
echo "  streamlit run app.py"
echo ""
