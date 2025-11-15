#!/bin/bash

# GitHub Repository Setup Script
# This script helps you create and push to a new GitHub repository

echo "🚀 Excel Tags Parser - GitHub Setup"
echo "===================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "📦 Installing via Homebrew..."
    brew install gh
fi

# Check if authenticated
echo "🔐 Checking GitHub authentication..."
if ! gh auth status &> /dev/null; then
    echo "⚠️  Not authenticated with GitHub"
    echo "🔑 Please authenticate..."
    gh auth login
else
    echo "✅ Already authenticated"
fi

# Confirm repository creation
echo ""
echo "📝 Repository Details:"
echo "   Name: excel-tags-parser-mongodb"
echo "   Visibility: Public"
echo "   Description: Excel Tags Parser with MongoDB Integration"
echo ""
read -p "Create this repository and push code? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🎯 Creating repository and pushing code..."
    
    gh repo create excel-tags-parser-mongodb \
        --public \
        --description "Excel Tags Parser with MongoDB Integration - Process large Excel files, extract metadata, and integrate with MongoDB. Includes MCP server for LLM analytics." \
        --source=. \
        --remote=origin \
        --push
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Success! Your repository is live at:"
        gh repo view --web
    else
        echo ""
        echo "❌ Error creating repository"
        echo "📖 See GITHUB_SETUP.md for manual setup instructions"
    fi
else
    echo "⏸️  Setup cancelled"
    echo "📖 See GITHUB_SETUP.md for setup instructions"
fi
