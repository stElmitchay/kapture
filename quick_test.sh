#!/bin/bash
# Quick test script for developers
# Simulates a full work day and tests blockchain submission

set -e  # Exit on error

echo "🧪 Loggerheads Quick Test Script"
echo "================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

if ! command -v solana &> /dev/null; then
    echo "❌ Solana CLI not found."
    echo "Install with: sh -c \"\$(curl -sSfL https://release.solana.com/stable/install)\""
    exit 1
fi
echo "✅ Solana CLI found: $(solana --version | head -1)"

# Check if package is installed
if ! command -v loggerheads &> /dev/null; then
    echo "📦 Installing loggerheads in development mode..."
    pip3 install -e .
fi
echo "✅ Loggerheads installed"

echo ""
echo "🔧 Setup Phase"
echo "=============="

# Ensure we're on devnet
echo "Setting Solana to devnet..."
solana config set --url devnet > /dev/null

# Check if wallets exist
if [ ! -f ~/.config/solana/employer.json ]; then
    echo "Creating employer wallet..."
    solana-keygen new --outfile ~/.config/solana/employer.json --no-bip39-passphrase --silent
    echo "✅ Employer wallet created"
fi

if [ ! -f ~/.config/solana/employee.json ]; then
    echo "Creating employee wallet..."
    solana-keygen new --outfile ~/.config/solana/employee.json --no-bip39-passphrase --silent
    echo "✅ Employee wallet created"
fi

# Get addresses
EMPLOYER_ADDR=$(solana address --keypair ~/.config/solana/employer.json)
EMPLOYEE_ADDR=$(solana address --keypair ~/.config/solana/employee.json)

echo ""
echo "👔 Employer: $EMPLOYER_ADDR"
echo "👤 Employee: $EMPLOYEE_ADDR"
echo ""

# Get SOL for both wallets
echo "💰 Getting test SOL..."
solana config set --keypair ~/.config/solana/employer.json > /dev/null
solana airdrop 2 --url devnet > /dev/null 2>&1 || echo "⚠️  Airdrop rate limit (this is OK if you have SOL)"
echo "✅ Employer has $(solana balance) SOL"

solana config set --keypair ~/.config/solana/employee.json > /dev/null
solana airdrop 1 --url devnet > /dev/null 2>&1 || echo "⚠️  Airdrop rate limit (this is OK if you have SOL)"
echo "✅ Employee has $(solana balance) SOL"

echo ""
echo "📊 Test Phase"
echo "============="

# Clear previous test data
echo "Clearing previous test data..."
rm -rf ~/.loggerheads_logs
rm -f ~/.loggerheads_vault.json ~/.loggerheads_context.json
echo "✅ Clean slate"

# Add fake work data
echo ""
echo "📸 Generating fake work data (8 hours)..."
python3 << 'EOF'
from loggerheads.database import get_db_path, init_db
from datetime import datetime, timedelta
import sqlite3

# Initialize database
init_db()

db_path = get_db_path()
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add 8 hours of screenshots (96 entries, 5 min apart)
now = datetime.now()
work_apps = [
    'VSCode - main.py - blockchain project',
    'Terminal - git commit',
    'Cursor - app.tsx - React development',
    'Chrome - Solana Documentation',
    'Terminal - npm run build',
    'VSCode - database.py - Python development',
]

for i in range(96):
    timestamp = now - timedelta(minutes=5 * (96 - i))
    app = work_apps[i % len(work_apps)]
    cursor.execute('''
        INSERT INTO screenshots (file_path, timestamp, extracted_text)
        VALUES (?, ?, ?)
    ''', (
        f'/fake/screenshot_{i}.png',
        timestamp.isoformat(),
        f'{app} (Screenshot {i})'
    ))

conn.commit()
conn.close()
print('✅ Added 96 screenshots (8 hours of work)')
EOF

# Check hours
echo ""
echo "Calculating hours worked..."
HOURS=$(python3 -c "from loggerheads.database import calculate_hours_worked_today; print(calculate_hours_worked_today())")
echo "✅ Detected: $HOURS hours of work"

echo ""
echo "🎯 What to test next:"
echo ""
echo "1️⃣  CREATE VAULT (as Employer):"
echo "   solana config set --keypair ~/.config/solana/employer.json"
echo "   loggerheads"
echo "   → Choose: [1] Employer"
echo "   → Choose: [1] Create vault"
echo "   → Employee address: $EMPLOYEE_ADDR"
echo "   → Fund: 3000"
echo "   → Hours: 8"
echo "   → Pay: 100"
echo ""
echo "2️⃣  CONFIGURE VAULT (as Employee):"
echo "   solana config set --keypair ~/.config/solana/employee.json"
echo "   loggerheads"
echo "   → Choose: [2] Employee"
echo "   → Employer address: $EMPLOYER_ADDR"
echo "   → Auto-submit: y"
echo "   → Time: 18:00"
echo ""
echo "3️⃣  SUBMIT HOURS (as Employee):"
echo "   loggerheads submit"
echo ""
echo "4️⃣  CHECK BALANCE (as Employee):"
echo "   loggerheads balance"
echo ""
echo "5️⃣  WITHDRAW (as Employee):"
echo "   loggerheads withdraw"
echo ""
echo "════════════════════════════════════════"
echo "💡 TIP: The fake data is already loaded!"
echo "   You can skip straight to step 1 and create the vault."
echo "════════════════════════════════════════"
