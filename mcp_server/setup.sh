#!/bin/bash

echo "Setting up MongoDB MCP Server..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make server executable
chmod +x mongodb_mcp_server.py

echo "✅ Setup complete!"
echo ""
echo "To run the server:"
echo "  source venv/bin/activate"
echo "  python mongodb_mcp_server.py"
echo ""
echo "To configure with an LLM:"
echo "  1. Copy the absolute path: $(pwd)/mongodb_mcp_server.py"
echo "  2. Add to your LLM's MCP configuration"
echo "  3. Restart the LLM application"
