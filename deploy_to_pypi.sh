#!/bin/bash
# Deploy Loggerheads to PyPI
# Run this script to build and upload the package

set -e  # Exit on error

echo "🚀 Deploying Loggerheads to PyPI"
echo "================================="
echo ""

# Check if required tools are installed
echo "📦 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    exit 1
fi

# Install/upgrade build tools
echo "📦 Installing build tools..."
pip3 install --upgrade pip setuptools wheel twine

# Clean previous builds
echo "🗑️  Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Build the package
echo "🔨 Building package..."
python3 setup.py sdist bdist_wheel

# Check the package
echo "🔍 Checking package..."
twine check dist/*

# Ask for confirmation
echo ""
echo "📋 Package built successfully!"
echo "   Files in dist/:"
ls -lh dist/
echo ""
read -p "🚀 Upload to PyPI? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Uploading to PyPI..."
    twine upload dist/*
    echo ""
    echo "✅ Deployed to PyPI!"
    echo ""
    echo "📦 Users can now install with:"
    echo "   pip3 install loggerheads"
else
    echo "❌ Upload cancelled"
    echo ""
    echo "💡 To upload later, run:"
    echo "   twine upload dist/*"
    echo ""
    echo "💡 To test on TestPyPI first:"
    echo "   twine upload --repository testpypi dist/*"
fi

echo ""
echo "================================="
