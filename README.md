# Loggerheads

**Blockchain-powered work tracking with automated payments.** Track work hours automatically, submit to Solana blockchain, earn USDC when you hit targets.

## What Is This?

Loggerheads combines automatic activity tracking with blockchain-enforced payments:

- **For Employees:** Work normally → Hours tracked automatically → Get paid in USDC
- **For Employers:** Create vaults → Fund with USDC → Payments unlock automatically

Everything is menu-driven with simple yes/no questions.

---

## Installation

### Option 1: From PyPI (Recommended)

```bash
pip install loggerheads
```

### Option 2: From Source (For Companies)

For tech teams deploying in a company:

```bash
git clone https://github.com/stElmitchay/loggerheads
cd loggerheads
pip3 install -e .
```

**See [Install From Source Guide](docs/INSTALL_FROM_SOURCE.md)** for complete employer + employee setup.

**Requirements:**
- Python 3.8+
- Solana CLI (app will guide installation)

**First run:**
```bash
loggerheads
```

The interactive menu will guide you through setup.

---

## Quick Start

### For Employees (2 minutes)

```bash
$ loggerheads

# Choose: Employee
# Enter: Employer's wallet address
# Enable auto-submit: y
# Done!

$ loggerheads start  # Start tracking
```

Your work is tracked automatically. At end of day, hours submit to blockchain. When you hit daily target, payment unlocks. Withdraw anytime.

### For Employers (2 minutes)

```bash
$ loggerheads

# Choose: Employer
# Enter: Employee wallet address
# Fund amount: 3000 USDC
# Daily target: 8 hours
# Daily pay: 100 USDC
# Done!
```

Send your wallet address to employee. They configure and start working. Payments unlock automatically when targets met.

---

## How It Works

1. **Employer** creates vault on Solana, locks USDC, sets rules
2. **Employee** installs app, starts tracking work activity
3. **App** captures screenshots, analyzes work (locally, private)
4. **Auto-submit** sends hours to blockchain daily
5. **Smart contract** unlocks payment if target met
6. **Employee** withdraws earnings to wallet

**Security:** Employee can't fake hours (oracle verification). Employer can't withhold payment (blockchain enforcement).

---

## Commands

```bash
loggerheads              # Interactive menu
loggerheads start        # Start tracking
loggerheads status       # Check today's hours
loggerheads balance      # Check earnings
loggerheads submit       # Submit hours manually
loggerheads withdraw     # Withdraw funds
loggerheads config       # View settings
loggerheads help         # Show help
```

---

## Testing (Devnet)

```bash
# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Get devnet SOL
solana config set --url devnet
solana airdrop 2

# Run automated test setup
git clone https://github.com/stElmitchay/loggerheads
cd loggerheads
./quick_test.sh
```

The test script creates test wallets, generates fake work data, and walks you through the full flow.

---

## Documentation

**Installation:**
- [Install From Source](docs/INSTALL_FROM_SOURCE.md) - For tech teams deploying in companies

**Setup Guides:**
- [Employee Quick Start](docs/QUICK_START_EMPLOYEE.md) - 10-minute setup
- [Employer Quick Start](docs/QUICK_START_EMPLOYER.md) - 5-minute setup
- [Production Deployment](docs/PRODUCTION_DEPLOYMENT.md) - Full deployment guide

**Development:**
- [Contributing Guide](docs/CONTRIBUTING.md) - Development workflow, testing
- [PyPI Publishing](docs/PYPI_PUBLISHING_GUIDE.md) - Publishing updates

**Technical:**
- [Architecture](docs/ARCHITECTURE.md) - System architecture
- [Claude Code Guide](docs/CLAUDE.md) - AI assistant instructions

---

## Support

- **Issues:** https://github.com/stElmitchay/loggerheads/issues
- **Network:** Solana Devnet
- **Program ID:** `5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D`

---

## License

MIT License - See LICENSE file
