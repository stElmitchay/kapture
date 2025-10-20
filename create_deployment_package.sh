#!/bin/bash
# Create deployment package for employee laptop

echo "📦 Creating Loggerheads Deployment Package"
echo "==========================================="

# Create deployment directory
DEPLOY_DIR="loggerheads_employee_package"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

echo "✓ Created deployment directory"

# Copy necessary files
echo "📋 Copying files..."

# Copy the built wheel
cp dist/loggerheads-*.whl $DEPLOY_DIR/ 2>/dev/null || {
    echo "⚠️  No wheel found, building..."
    python3 setup.py bdist_wheel
    cp dist/loggerheads-*.whl $DEPLOY_DIR/
}

# Copy documentation
cp docs/QUICK_START_EMPLOYEE.md $DEPLOY_DIR/
cp docs/PRODUCTION_DEPLOYMENT.md $DEPLOY_DIR/
cp README.md $DEPLOY_DIR/

# Create installation script
cat > $DEPLOY_DIR/install.sh << 'EOF'
#!/bin/bash
echo "🚀 Installing Loggerheads for Employee"
echo "======================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python 3 found"

# Check Solana CLI
if ! command -v solana &> /dev/null; then
    echo "⚠️  Solana CLI not found"
    echo "Installing Solana CLI..."
    sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

    echo ""
    echo "📝 Add this to your ~/.zshrc or ~/.bashrc:"
    echo 'export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"'
    echo ""
    echo "Then run: source ~/.zshrc"
    echo ""
fi

# Install loggerheads
echo "📦 Installing loggerheads..."
pip3 install loggerheads-*.whl

echo ""
echo "✅ Installation complete!"
echo ""
echo "📖 Next steps:"
echo "1. Read QUICK_START_EMPLOYEE.md"
echo "2. Create wallet: solana-keygen new"
echo "3. Get your address: solana address"
echo "4. Send address to employer"
echo "5. Run: loggerheads"
echo ""
EOF

chmod +x $DEPLOY_DIR/install.sh

# Create README for the package
cat > $DEPLOY_DIR/INSTALL_README.txt << 'EOF'
LOGGERHEADS EMPLOYEE INSTALLATION
==================================

This package contains everything you need to start earning with Loggerheads.

QUICK INSTALL:
1. Run: ./install.sh
2. Create wallet: solana-keygen new
3. Get address: solana address
4. Send address to your employer
5. Run: loggerheads
6. Follow the prompts

DETAILED GUIDE:
See QUICK_START_EMPLOYEE.md for full instructions.

REQUIREMENTS:
- macOS or Linux
- Python 3.8+
- 1GB free disk space

SUPPORT:
- Documentation: PRODUCTION_DEPLOYMENT.md
- Full README: README.md
EOF

# Create a tarball
echo "📦 Creating tarball..."
tar -czf loggerheads_employee_package.tar.gz $DEPLOY_DIR

echo ""
echo "✅ Deployment package created!"
echo ""
echo "📦 Package location:"
echo "   $(pwd)/loggerheads_employee_package.tar.gz"
echo ""
echo "📤 Transfer to employee laptop:"
echo "   1. USB drive: Copy loggerheads_employee_package.tar.gz"
echo "   2. Or email/cloud: Share the tarball"
echo ""
echo "📥 On employee laptop:"
echo "   tar -xzf loggerheads_employee_package.tar.gz"
echo "   cd loggerheads_employee_package"
echo "   ./install.sh"
echo ""
