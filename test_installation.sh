#!/bin/bash
# Test Loggerheads Installation
# Verifies all dependencies are installed correctly

set -e

echo "🧪 Testing Loggerheads Installation"
echo "===================================="
echo ""

# Test Python imports
echo "📦 Testing Python imports..."

python3 << 'EOF'
import sys

# Test core dependencies
try:
    import pygetwindow
    print("  ✓ pygetwindow")
except ImportError:
    print("  ✗ pygetwindow MISSING")
    sys.exit(1)

try:
    from PIL import Image
    print("  ✓ pillow")
except ImportError:
    print("  ✗ pillow MISSING")
    sys.exit(1)

try:
    import pytesseract
    print("  ✓ pytesseract")
except ImportError:
    print("  ✗ pytesseract MISSING")
    sys.exit(1)

try:
    from pynput import keyboard, mouse
    print("  ✓ pynput")
except ImportError:
    print("  ✗ pynput MISSING")
    sys.exit(1)

# Test UI dependencies
try:
    from rich import print as rprint
    print("  ✓ rich")
except ImportError:
    print("  ✗ rich MISSING")
    sys.exit(1)

try:
    import textual
    print("  ✓ textual")
except ImportError:
    print("  ✗ textual MISSING")
    sys.exit(1)

# Test blockchain dependencies
try:
    from solana.rpc.api import Client
    print("  ✓ solana")
except ImportError:
    print("  ✗ solana MISSING")
    sys.exit(1)

try:
    from solders.pubkey import Pubkey
    print("  ✓ solders")
except ImportError:
    print("  ✗ solders MISSING")
    sys.exit(1)

# Test API dependencies
try:
    import requests
    print("  ✓ requests")
except ImportError:
    print("  ✗ requests MISSING")
    sys.exit(1)

try:
    import flask
    print("  ✓ flask")
except ImportError:
    print("  ✗ flask MISSING")
    sys.exit(1)

try:
    from flask_cors import CORS
    print("  ✓ flask-cors")
except ImportError:
    print("  ✗ flask-cors MISSING")
    sys.exit(1)

try:
    from flask_limiter import Limiter
    print("  ✓ flask-limiter")
except ImportError:
    print("  ✗ flask-limiter MISSING")
    sys.exit(1)

# Test utilities
try:
    from dotenv import load_dotenv
    print("  ✓ python-dotenv")
except ImportError:
    print("  ✗ python-dotenv MISSING")
    sys.exit(1)

# Test liveness detection
try:
    import cv2
    print("  ✓ opencv-python")
except ImportError:
    print("  ✗ opencv-python MISSING")
    sys.exit(1)

print("\n✅ All dependencies installed correctly!")

EOF

echo ""
echo "🧪 Testing Loggerheads modules..."

python3 << 'EOF'
import sys
sys.path.insert(0, '.')

try:
    from loggerheads.database import init_db
    print("  ✓ database module")
except ImportError as e:
    print(f"  ✗ database module: {e}")
    sys.exit(1)

try:
    from loggerheads.liveness_detector import check_liveness
    print("  ✓ liveness_detector module")
except ImportError as e:
    print(f"  ✗ liveness_detector module: {e}")
    sys.exit(1)

try:
    from loggerheads.blockchain import get_vault_info
    print("  ✓ blockchain module")
except ImportError as e:
    print(f"  ✗ blockchain module: {e}")
    sys.exit(1)

try:
    from loggerheads.oracle_client import get_oracle_client
    print("  ✓ oracle_client module")
except ImportError as e:
    print(f"  ✗ oracle_client module: {e}")
    sys.exit(1)

try:
    from loggerheads.auto_submit import auto_submit
    print("  ✓ auto_submit module")
except ImportError as e:
    print(f"  ✗ auto_submit module: {e}")
    sys.exit(1)

try:
    from loggerheads.app_based_analyzer import generate_app_based_summary
    print("  ✓ app_based_analyzer module")
except ImportError as e:
    print(f"  ✗ app_based_analyzer module: {e}")
    sys.exit(1)

print("\n✅ All modules working correctly!")

EOF

echo ""
echo "🧪 Testing CLI commands..."
if command -v loggerheads &> /dev/null; then
    echo "  ✓ loggerheads command available"
else
    echo "  ✗ loggerheads command NOT FOUND"
    echo "    Run: pip3 install -e ."
fi

echo ""
echo "===================================="
echo "✅ Installation test complete!"
echo "===================================="
echo ""
echo "📦 Ready to use:"
echo "   loggerheads --help"
echo "   loggerheads start"
echo ""
