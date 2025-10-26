# Loggerheads

**Automatic work tracking meets blockchain payments.** Your hours are tracked automatically through AI-powered screen analysis, then verified and paid through Solana smart contracts.

---

## What Is This?

Loggerheads is a work tracking system that combines local AI analysis with blockchain automation:

**The Problem It Solves:**
- Manual time tracking is tedious and easy to forget
- Traditional payment systems require trust between employer and employee
- There's no verifiable proof of work completion

**How Loggerheads Works:**
1. You work normally on your computer
2. The app takes periodic screenshots and uses OCR + AI to understand what you're doing
3. Your work hours are calculated automatically
4. Hours are submitted to a Solana smart contract
5. When you hit your daily target, payment unlocks automatically
6. You withdraw your earnings to your wallet

**Key Benefits:**
- **Zero manual tracking** - Just work, everything else is automatic
- **Trustless payments** - Smart contracts enforce payment rules, no one can cheat
- **Privacy-first** - All analysis happens locally on your machine
- **Transparent** - Everything is verifiable on the blockchain

---

## Installation

### Requirements
- **Python 3.8+** - Check with `python3 --version`
- **macOS or Linux** - Currently supported platforms
- **Solana CLI** - The app will help you install this

### Install Loggerheads

**Option 1: Quick Install (Recommended)**
```bash
pip3 install loggerheads
```

**Option 2: From Source**
```bash
git clone https://github.com/stElmitchay/loggerheads
cd loggerheads
pip3 install -e .
```

### First-Time Setup

After installation, just run:
```bash
loggerheads
```

The interactive menu will guide you through everything with simple questions. No technical knowledge required.

---

## Getting Started

### For Employees

**Setup (2 minutes):**
```bash
$ loggerheads
```
- Choose "Employee" mode
- Enter your employer's wallet address (they'll give you this)
- Configure auto-submit (recommended: Yes)
- Done!

**Daily Usage:**
```bash
$ loggerheads start
```
This starts the tracker. Work normally - your activity is captured automatically. Press Ctrl+C when you're done for the day.

**Check Your Status:**
```bash
$ loggerheads status      # See hours worked today
$ loggerheads balance     # Check your earnings
$ loggerheads withdraw    # Withdraw your USDC
```

### For Employers

**Setup (5 minutes):**
```bash
$ loggerheads
```
- Choose "Employer" mode
- Follow prompts to create a payment vault
- Fund it with USDC
- Set daily target hours and payment amount
- Share your wallet address with employees

That's it! Employees configure their app with your wallet address and start working. Payments unlock automatically when they hit their targets.

---

## Common Commands

```bash
loggerheads              # Interactive menu (start here)
loggerheads start        # Start tracking work
loggerheads status       # Check today's hours
loggerheads balance      # Check wallet balance
loggerheads submit       # Submit hours to blockchain
loggerheads withdraw     # Withdraw earned USDC
loggerheads config       # View your configuration
loggerheads help         # Show all commands
```

---

## How It Works (Technical Overview)

1. **Screen Capture** - Takes screenshots every few minutes
2. **OCR Processing** - Extracts text from screenshots using Tesseract
3. **AI Analysis** - Understands what applications you're using and what work you're doing
4. **Local Storage** - Everything stored in local SQLite database (private)
5. **Blockchain Submission** - Hours submitted to Solana smart contract with oracle signature
6. **Smart Contract Verification** - Contract verifies oracle signature and unlocks payment
7. **Withdrawal** - Employee withdraws USDC to their wallet

**Privacy Note:** All screenshots and analysis happen locally on your machine. Nothing is uploaded to any server. Only your work hours (not screenshots) are submitted to the blockchain.

---

## Security & Production Setup

**For Testing/Demos:** The app works out of the box with demo credentials. Perfect for trying it out.

**For Production:** You must set up a secure oracle keypair:

```bash
# Generate secure keypair
python3 -m loggerheads.oracle_secure --generate

# Add to your shell config (~/.bashrc or ~/.zshrc)
export ORACLE_KEYPAIR_PATH=~/.loggerheads/oracle-keypair.json

# Verify
python3 -m loggerheads.oracle_secure --pubkey
```

The oracle signs work submissions to prevent fraud. Without a secure oracle, anyone could fake work hours.

See [Oracle Security Guide](docs/ORACLE_SECURITY.md) for complete details.

---

## Testing on Solana Devnet

Want to try it out without real money?

```bash
# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Switch to devnet
solana config set --url devnet

# Get free test SOL
solana airdrop 2

# Run quick test
./quick_test.sh
```

The test script sets up test wallets and walks you through the complete employer + employee flow.

---

## Documentation

**Quick Start Guides:**
- [Employee Setup](docs/QUICK_START_EMPLOYEE.md) - Detailed employee walkthrough
- [Employer Setup](docs/QUICK_START_EMPLOYER.md) - Detailed employer walkthrough
- [Installing from Source](docs/INSTALL_FROM_SOURCE.md) - For tech teams

**Production & Security:**
- [Production Deployment](docs/PRODUCTION_DEPLOYMENT.md) - Production setup guide
- [Oracle Security](docs/ORACLE_SECURITY.md) - Security best practices

**Development:**
- [Architecture](docs/ARCHITECTURE.md) - How the system works
- [Contributing](docs/CONTRIBUTING.md) - Development workflow

---

## Troubleshooting

**"Command not found: loggerheads"**
- Make sure pip install completed successfully
- Try `python3 -m loggerheads` instead
- Add `~/.local/bin` to your PATH

**"Failed to connect to Solana"**
- Check your internet connection
- Verify Solana CLI is installed: `solana --version`
- Try switching network: `solana config set --url devnet`

**"Screenshot permission denied"**
- On macOS, go to System Preferences → Security & Privacy → Privacy → Screen Recording
- Enable Terminal (or your terminal app)

**More help:**
- [Open an issue](https://github.com/stElmitchay/loggerheads/issues)
- Check the docs folder for detailed guides

---

## Project Info

**Network:** Solana (Devnet for testing, Mainnet for production)
**Smart Contract:** `5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D`
**License:** MIT
**Repository:** https://github.com/stElmitchay/loggerheads
