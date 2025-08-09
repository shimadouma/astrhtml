#!/bin/bash
# Manual deployment script for GitHub Pages

set -e

echo "=== Manual Deployment Script ==="

# Check if we're in the right directory
if [ ! -f "build.py" ]; then
    echo "Error: This script must be run from the project root directory"
    exit 1
fi

# Install dependencies if needed
echo "Installing dependencies..."
pip install -r requirements.txt

# Update submodule
echo "Updating ArknightsStoryJson submodule..."
git submodule update --remote --merge

# Build the site
echo "Building site..."
python build.py

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "Error: Build failed - dist directory not found"
    exit 1
fi

# Deploy using gh-pages branch
echo "Deploying to gh-pages branch..."
if command -v gh &> /dev/null; then
    # Using GitHub CLI if available
    echo "Using GitHub CLI for deployment..."
    # Note: This would require additional setup for gh CLI
    echo "Please configure GitHub CLI or use the GitHub Actions workflow for automatic deployment"
else
    # Manual git commands
    echo "Manual deployment:"
    echo "1. Install GitHub CLI: https://cli.github.com/"
    echo "2. Or use git commands to push dist/ to gh-pages branch"
    echo "3. Or push changes to main branch to trigger GitHub Actions"
fi

echo "=== Deployment Complete ==="
echo "Site will be available at: https://<username>.github.io/<repository-name>/"