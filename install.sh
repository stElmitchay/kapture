#!/bin/bash
# Loggerheads One-Command Installer
# Usage: curl -sSL https://raw.githubusercontent.com/stElmitchay/loggerheads/main/install.sh | bash

set -e

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   🚀 Loggerheads Installer            ║"
echo "║   Blockchain-Powered Work Tracker     ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "   Install Python 3.8+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION found"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed"
    exit 1
fi
echo "✓ pip3 found"

# Install Tesseract (system dependency)
echo ""
echo "📦 Checking system dependencies..."

if command -v brew &> /dev/null; then
    # macOS with Homebrew
    if ! command -v tesseract &> /dev/null; then
        echo "📥 Installing Tesseract OCR via Homebrew..."
        brew install tesseract
    else
        echo "✓ Tesseract already installed"
    fi
elif command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    if ! command -v tesseract &> /dev/null; then
        echo "📥 Installing Tesseract OCR via apt..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr python3-tk python3-dev
    else
        echo "✓ Tesseract already installed"
    fi
elif command -v dnf &> /dev/null; then
    # Fedora
    if ! command -v tesseract &> /dev/null; then
        echo "📥 Installing Tesseract OCR via dnf..."
        sudo dnf install -y tesseract python3-devel
    else
        echo "✓ Tesseract already installed"
    fi
else
    echo "⚠️  Could not detect package manager"
    echo "   Please install Tesseract OCR manually:"
    echo "   - macOS: brew install tesseract"
    echo "   - Linux: sudo apt-get install tesseract-ocr"
fi

# Install Loggerheads
echo ""
echo "📦 Installing Loggerheads and all dependencies..."
echo "   This may take a few minutes..."
echo ""

# Check if requirements.txt exists (git clone) or install from PyPI
if [ -f "requirements.txt" ]; then
    # Local installation from source
    echo "🔧 Installing from source..."
    pip3 install -r requirements.txt
    pip3 install -e .
else
    # Install from PyPI
    echo "📦 Installing from PyPI..."
    pip3 install loggerheads
fi

# Verify installation
echo ""
echo "🧪 Verifying installation..."

if command -v loggerheads &> /dev/null; then
    echo "✅ Loggerheads installed successfully!"
else
    echo "⚠️  Warning: loggerheads command not found in PATH"
    echo "   Try running: export PATH=\"$HOME/.local/bin:\$PATH\""
fi

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ Installation Complete!           ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "🚀 Get started:"
echo "   loggerheads          # Interactive setup"
echo "   loggerheads start    # Start tracking"
echo "   loggerheads submit   # Submit hours"
echo ""
echo "📖 Documentation:"
echo "   https://github.com/stElmitchay/loggerheads"
echo ""
