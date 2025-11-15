#!/bin/bash

# Navigate to script directory
cd "$(dirname "$0")"

# Activate virtual environment and run test
source venv/bin/activate
python3 test_mcp.py
deactivate
