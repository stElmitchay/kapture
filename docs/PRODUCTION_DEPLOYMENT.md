# Production Deployment Guide

## Overview

Loggerheads is a blockchain-powered work tracking system with two separate roles:

- **EMPLOYER** (you): Creates vaults, funds them, monitors employee work
- **EMPLOYEE** (second laptop): Tracks work, submits hours, earns payment

---

## Architecture

```
┌─────────────────────────┐         ┌─────────────────────────┐
│   EMPLOYER LAPTOP       │         │   EMPLOYEE LAPTOP       │
│  (Your Main Machine)    │         │  (Second Laptop)        │
├─────────────────────────┤         ├─────────────────────────┤
│                         │         │                         │
│  ✓ Create vaults        │         │  ✓ Install loggerheads  │
│  ✓ Fund with USDC       │         │  ✓ Run tracker          │
│  ✓ Monitor status       │         │  ✓ Submit hours         │
│  ✗ NO tracking          │         │  ✓ Withdraw earnings    │
│  ✗ NO vault config      │         │                         │
│                         │         │                         │
└────────────┬────────────┘         └────────────┬────────────┘
             │                                   │
             │        Solana Blockchain          │
             └───────────────┬───────────────────┘
                             │
                      ┌──────▼──────┐
                      │    Vault    │
                      │  Smart      │
                      │  Contract   │
                      └─────────────┘
```

---

## Part 1: Employer Setup (Your Main Laptop)

### Prerequisites
- Solana CLI installed
- USDC tokens (devnet or mainnet)
- Python 3.8+

### Step 1: Install Loggerheads
```bash
cd /Users/mitch_1/daily_log_ai
pip3 install -e .
```

### Step 2: Check Your Wallet
```bash
solana address
```
**Save this address** - you'll give it to employees.

### Step 3: Get Devnet Tokens (Testing Only)
```bash
# Get SOL for transaction fees
solana airdrop 2 --url devnet

# Check balance
solana balance --url devnet
```

For USDC, use a faucet or mint authority.

### Step 4: Create Vault for Employee

**Option A: Interactive (Recommended)**
```bash
loggerheads
# Choose: Employer
# Follow prompts to create vault
```

**Option B: Manual Script**
```bash
cd workchain-program/scripts
npx ts-node create-vault.ts
```

You'll need:
- Employee's wallet address (they run: `solana address`)
- Amount to lock (e.g., 3000 USDC for month)
- Daily target hours (e.g., 8)
- Daily unlock amount (e.g., 100 USDC)

### Step 5: Give Employee Their Info

Send employee **ONLY** this:
```
Your employer wallet: <YOUR_WALLET_ADDRESS>
```

That's it! They don't need anything else.

### Step 6: Monitor Employee Work

```bash
# Check vault status
loggerheads balance

# View vault details
loggerheads config
```

### ⚠️ IMPORTANT: Employer Does NOT Track

**DO NOT run these on employer laptop:**
- ❌ `loggerheads start` (tracking)
- ❌ `loggerheads submit` (submitting)
- ❌ Set up vault config

Those commands are for the EMPLOYEE laptop only!

---

## Part 2: Employee Setup (Second Laptop)

### Prerequisites
- Python 3.8+
- Solana CLI installed

### Step 1: Install Solana CLI

**macOS:**
```bash
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

**Linux:**
```bash
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

Add to PATH:
```bash
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
```

### Step 2: Create Wallet
```bash
solana-keygen new --outfile ~/.config/solana/id.json
```

**IMPORTANT**: Save the seed phrase securely!

### Step 3: Get Your Wallet Address
```bash
solana address
```

**Send this address to your employer** - they need it to create your vault.

### Step 4: Install Loggerheads
```bash
pip3 install loggerheads
```

Or from source:
```bash
git clone <repo-url>
cd daily_log_ai
pip3 install -e .
```

### Step 5: Set Up Your Vault Config
```bash
loggerheads
```

Choose:
1. **Employee** (not Employer!)
2. Enter employer's wallet address (they gave you this)
3. Enable auto-submit? → **Yes**
4. Time? → **18:00** (or your preferred time)

### Step 6: Install Auto-Start
```bash
loggerheads install
```

This makes tracking start automatically when you log in.

### Step 7: Start Tracking
```bash
loggerheads start
```

Or restart your laptop (auto-start will begin tracking).

### Step 8: Verify It's Working
```bash
# Check status
loggerheads status

# See recent screenshots
loggerheads screenshots

# Check your balance
loggerheads balance
```

### Step 9: Daily Workflow

**Morning:**
- Log in → Tracker starts automatically ✓
- Work normally ✓

**End of Day (18:00):**
- Hours auto-submit to blockchain ✓
- Payment unlocks if target met ✓

**When Ready:**
```bash
# Withdraw your earnings
loggerheads withdraw
```

---

## Testing the Full Flow

### On Employer Laptop:
```bash
# 1. Create test vault
loggerheads
# Choose: Employer → Create vault

# 2. Check it was created
loggerheads balance
```

### On Employee Laptop:
```bash
# 1. Configure vault
loggerheads
# Choose: Employee → Enter employer address

# 2. Start tracking (let it run 30+ min)
loggerheads start

# 3. After 30 min, check hours
loggerheads status
# Should show: "Hours today: 0.5 hours" (or similar)

# 4. Submit manually (for testing)
loggerheads submit
# Should unlock payment if hours >= target

# 5. Check balance
loggerheads balance
# Should show unlocked USDC

# 6. Withdraw
loggerheads withdraw
```

---

## Troubleshooting

### Employee: "Hours showing 0.0"
```bash
# Check if tracker is running
loggerheads status

# Check screenshots exist
ls ~/.loggerheads_logs/screenshots/

# Check database
sqlite3 ~/.loggerheads_logs/activity_log.db "SELECT COUNT(*) FROM screenshots;"
```

### Employee: "Submit failed"
```bash
# Check vault config
loggerheads config

# Verify employer address is correct
# Check you have SOL for transaction fees
solana balance
```

### Employer: "Can't create vault"
```bash
# Check USDC balance
spl-token accounts

# Check SOL balance
solana balance

# Verify you're on correct network
solana config get
```

---

## Production Checklist

### Before Employee Starts Work:

- [ ] Employer created vault with correct employee address
- [ ] Vault is funded with enough USDC
- [ ] Employee installed loggerheads on their laptop
- [ ] Employee configured vault with employer address
- [ ] Employee ran `loggerheads install` for auto-start
- [ ] Tracker is running and capturing screenshots
- [ ] Auto-submit is enabled
- [ ] Test submit worked and unlocked payment

### Daily Monitoring:

- [ ] Employee's tracker is running
- [ ] Hours are being calculated correctly
- [ ] Auto-submit runs at configured time
- [ ] Payments unlock when target met
- [ ] Employee can withdraw earnings

---

## Security Notes

### For Employers:
- Keep your wallet seed phrase secure
- Don't share your private key
- Monitor vault balances regularly
- Verify employee addresses before funding

### For Employees:
- Keep your wallet seed phrase secure
- Don't share your private key
- Only install loggerheads from trusted source
- Verify employer address before configuring

---

## Network Configuration

### Devnet (Testing):
```bash
solana config set --url devnet
```

### Mainnet (Production):
```bash
solana config set --url mainnet-beta

# Update in code:
# loggerheads/blockchain.py
# Change DEFAULT_RPC_URL to mainnet
```

---

## Support

Issues: https://github.com/your-repo/issues
Documentation: See README.md
