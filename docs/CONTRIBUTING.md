# Developer Guide: Clone, Install & Test

Quick guide for developers and testers who want to run Loggerheads directly from source.

## Prerequisites

- **macOS or Linux**
- **Python 3.8+**
- **Git**

## Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/stElmitchay/loggerheads.git
cd loggerheads
```

### 2. Install Solana CLI

**macOS/Linux:**
```bash
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

Add to your shell config (`~/.zshrc` or `~/.bashrc`):
```bash
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
```

Reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

Verify:
```bash
solana --version
```

### 3. Install Loggerheads (Development Mode)

```bash
pip3 install -e .
```

The `-e` flag installs in "editable" mode - changes to the code take effect immediately without reinstalling.

### 4. Create Test Wallets

```bash
# Create employer wallet
solana-keygen new --outfile ~/.config/solana/employer.json

# Create employee wallet
solana-keygen new --outfile ~/.config/solana/employee.json
```

**IMPORTANT:** Save the seed phrases somewhere safe!

### 5. Get Devnet SOL (for transaction fees)

```bash
# Set to devnet
solana config set --url devnet

# Use employer wallet
solana config set --keypair ~/.config/solana/employer.json

# Get test SOL
solana airdrop 2
```

### 6. Run Loggerheads

```bash
loggerheads
```

The interactive menu will guide you through the rest!

---

## Full Testing Flow

### Test as Employer (Create Vault)

```bash
# 1. Use employer wallet
solana config set --keypair ~/.config/solana/employer.json

# 2. Get employee's address (in another terminal)
solana address --keypair ~/.config/solana/employee.json
# Copy this address

# 3. Run loggerheads
loggerheads

# 4. Follow prompts:
# - Choose: [1] Employer
# - Choose: [1] Create vault for employee
# - Paste employee address (from step 2)
# - Fund amount: 3000 (USDC - testing)
# - Daily hours: 8
# - Daily pay: 100

# 5. Copy YOUR address to give to "employee"
solana address
```

### Test as Employee (Track Work)

```bash
# 1. Switch to employee wallet
solana config set --keypair ~/.config/solana/employee.json

# 2. Get some SOL for fees
solana airdrop 1

# 3. Run loggerheads
loggerheads

# 4. Follow prompts:
# - Choose: [2] Employee
# - Paste employer address (from employer step 5)
# - Auto-submit? y
# - Time? 18:00

# 5. Start tracking
loggerheads start
```

Leave it running for 30+ minutes to accumulate work data.

### Test Submission & Withdrawal

After tracking for a while:

```bash
# Check hours tracked
loggerheads status

# Submit hours manually (for testing)
loggerheads submit

# Check balance
loggerheads balance

# Withdraw earnings
loggerheads withdraw
```

---

## Development Workflow

### Making Changes

Since you installed with `pip3 install -e .`, changes to the code take effect immediately:

```bash
# Edit any Python file
nano loggerheads/cli.py

# Run immediately - no reinstall needed!
loggerheads
```

### Running Specific Commands

```bash
# Direct commands (bypass menu)
loggerheads start          # Start tracking
loggerheads status         # Check today's hours
loggerheads balance        # Check vault balance
loggerheads submit         # Submit hours
loggerheads withdraw       # Withdraw funds
loggerheads config         # View configuration
loggerheads screenshots    # View recent screenshots
loggerheads logs           # View database logs
```

### Viewing Logs & Data

```bash
# Screenshots directory
ls ~/.loggerheads_logs/screenshots/

# Database
sqlite3 ~/.loggerheads_logs/activity_log.db "SELECT * FROM screenshots LIMIT 5;"

# Vault config
cat ~/.loggerheads_vault.json
```

### Resetting Everything

```bash
# Stop tracking
pkill -f loggerheads

# Clear all data
rm -rf ~/.loggerheads_logs
rm ~/.loggerheads_vault.json
rm ~/.loggerheads_context.json

# Start fresh
loggerheads
```

---

## Testing Specific Features

### Test Auto-Submit

```bash
# Configure vault with auto-submit enabled
loggerheads
# Choose Employee → Enable auto-submit → Set time to NOW + 2 minutes

# Start tracking
loggerheads start

# Wait 2 minutes - should auto-submit
```

### Test App-Based Detection

```bash
# Start tracking
loggerheads start

# Open different apps:
# - VSCode/Cursor (should count as work)
# - Terminal (should count as work)
# - WhatsApp with "project discussion" (work)
# - WhatsApp with "birthday party" (not work)
# - YouTube with "Python tutorial" (work)
# - YouTube with "music playlist" (not work)

# After 30 min, check results
loggerheads status
loggerheads screenshots
```

### Test Blockchain Integration

```bash
# Check program is deployed
solana program show 5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D --url devnet

# View transaction on explorer (after submit)
# Copy transaction signature from submit output
# Visit: https://explorer.solana.com/tx/SIGNATURE?cluster=devnet
```

---

## Troubleshooting

### "Command not found: loggerheads"

```bash
# Check installation
pip3 show loggerheads

# If not found, reinstall
pip3 install -e .

# Check Python bin directory is in PATH
which python3
ls -la $(dirname $(which python3))/../bin/loggerheads
```

### "Module not found" errors

```bash
# Install all dependencies from setup.py
pip3 install -e .
```

### "Insufficient funds" error

```bash
# Check SOL balance
solana balance

# Get more test SOL
solana airdrop 2

# For USDC testing on devnet
# You'll need to use a faucet or mint authority
```

### Database issues

```bash
# Check database exists
ls -la ~/.loggerheads_logs/activity_log.db

# View database schema
sqlite3 ~/.loggerheads_logs/activity_log.db ".schema"

# Check data
sqlite3 ~/.loggerheads_logs/activity_log.db "SELECT COUNT(*) FROM screenshots;"
```

### Role confusion

```bash
# Clear vault config and start over
rm ~/.loggerheads_vault.json

# Verify which wallet you're using
solana address

# Check config shows correct role
loggerheads config
```

---

## Running Tests

### Manual Testing Checklist

- [ ] Employer: Create vault
- [ ] Employee: Configure vault
- [ ] Employee: Start tracking
- [ ] Employee: Screenshots captured
- [ ] Employee: OCR extracted text
- [ ] Employee: Hours calculated correctly
- [ ] Employee: Submit hours to blockchain
- [ ] Employee: Check balance shows unlocked funds
- [ ] Employee: Withdraw to wallet
- [ ] Employer: View employee vault status

### Quick Test with Fake Data

```bash
# Add fake work data to database (testing only)
python3 << 'EOF'
from loggerheads.database import get_db_path
from datetime import datetime, timedelta
import sqlite3

db_path = get_db_path()
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add 8 hours of screenshots (96 entries, 5 min apart)
now = datetime.now()
for i in range(96):
    timestamp = now - timedelta(minutes=5 * (96 - i))
    cursor.execute('''
        INSERT INTO screenshots (file_path, timestamp, extracted_text)
        VALUES (?, ?, ?)
    ''', (
        f'/fake/screenshot_{i}.png',
        timestamp.isoformat(),
        f'VSCode - main.py - Project: {i}'
    ))

conn.commit()
conn.close()
print('✅ Added 8 hours of fake work data')
EOF

# Check hours
loggerheads status
# Should show: "Hours today: 8.0 hours"

# Submit to blockchain
loggerheads submit
```

---

## Project Structure

```
loggerheads/
├── loggerheads/              # Main Python package
│   ├── cli.py                # Interactive menu
│   ├── blockchain.py         # Solana integration
│   ├── vault_creation.py     # Vault creation flow
│   ├── database.py           # Activity tracking
│   ├── scheduler.py          # Screenshot tracking loop
│   ├── app_based_analyzer.py # Work detection
│   └── ...
├── workchain-program/        # Solana smart contract (Rust)
├── setup.py                  # Package configuration
├── README.md                 # User documentation
├── QUICK_START_EMPLOYEE.md   # Employee setup guide
├── QUICK_START_EMPLOYER.md   # Employer setup guide
└── CONTRIBUTING.md           # This file
```

---

## Need Help?

- **Issues:** https://github.com/stElmitchay/loggerheads/issues
- **Discussions:** https://github.com/stElmitchay/loggerheads/discussions
- **Documentation:** See README.md

---

## Contributing

Contributions welcome! To contribute:

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test thoroughly (see testing section above)
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

---

## License

MIT License - See LICENSE file
