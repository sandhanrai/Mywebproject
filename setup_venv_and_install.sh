#!/bin/bash
# Script to create a new virtual environment and install dependencies

# Create virtual environment in .venv directory
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt

echo "Virtual environment setup complete. To activate, run:"
echo "source .venv/bin/activate"
