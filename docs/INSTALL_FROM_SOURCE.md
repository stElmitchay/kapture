# Install From Source (Production)

Quick guide for tech teams deploying Loggerheads for actual use in a company. This is **not** for development/contributing - this is for production deployment from source.

## Use Case

You're a tech team at Company A. You need to:
1. Install on Boss A's laptop (Employer)
2. Install on Staff A's laptop (Employee)
3. Both ready to track work and process payments

---

## Prerequisites

Both laptops need:
- macOS or Linux
- Python 3.8+
- Internet connection (for installation only)

---

## Part 1: Employer Laptop Setup

Run these commands on the employer's laptop:

### 1. Install Solana CLI

```bash
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

Add to shell config (`~/.zshrc` or `~/.bashrc`):
```bash
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
```

Reload:
```bash
source ~/.zshrc  # or ~/.bashrc
```

### 2. Clone and Install Loggerheads

```bash
git clone https://github.com/stElmitchay/loggerheads.git
cd loggerheads
pip3 install -e .
```

### 3. Create Employer Wallet

```bash
# Set to devnet (or mainnet for production)
solana config set --url devnet

# Create wallet
solana-keygen new

# Get devnet SOL for transaction fees
solana airdrop 2

# Save employer address - you'll give this to employee later
solana address
```

**Save this address!** The employee will need it.

### 4. Create Vault for Employee

```bash
loggerheads
```

Follow the prompts:
1. Choose: **[1] Employer**
2. Choose: **[1] Create vault for employee**
3. Enter **employee wallet address** (they'll give you this)
4. Fund amount: **3000** (example: 1 month @ $100/day)
5. Daily hours: **8**
6. Daily pay: **100**

Done! Give the employee your wallet address from step 3.

### 5. Employer is Done

The employer laptop does NOT run tracking. Only the employee laptop tracks work.

---

## Part 2: Employee Laptop Setup

Run these commands on the employee's laptop:

### 1. Install Solana CLI

```bash
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

Add to shell config (`~/.zshrc` or `~/.bashrc`):
```bash
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
```

Reload:
```bash
source ~/.zshrc  # or ~/.bashrc
```

### 2. Clone and Install Loggerheads

```bash
git clone https://github.com/stElmitchay/loggerheads.git
cd loggerheads
pip3 install -e .
```

### 3. Create Employee Wallet

```bash
# Set to devnet (or mainnet for production)
solana config set --url devnet

# Create wallet
solana-keygen new

# Get devnet SOL for transaction fees
solana airdrop 1

# Get your address - send this to employer
solana address
```

**Send this address to the employer!** They need it to create your vault.

### 4. Configure Vault

**WAIT** until employer has created the vault, then:

```bash
loggerheads
```

Follow the prompts:
1. Choose: **[2] Employee**
2. Enter **employer wallet address** (they gave you this)
3. Auto-submit? **y**
4. Time? **18:00** (or your preferred end-of-day time)

### 5. Enable Auto-Start (Optional but Recommended)

```bash
loggerheads install
```

This makes tracking start automatically when you log in.

### 6. Start Tracking

```bash
loggerheads start
```

Or just restart your laptop (if you enabled auto-start).

---

## Verification

### On Employee Laptop:

```bash
# Check tracking is working
loggerheads status

# Should show hours accumulating
# Example: "Hours today: 0.5 hours"
```

After a full work day:

```bash
# Check balance (should show unlocked funds)
loggerheads balance

# Withdraw earnings
loggerheads withdraw
```

### On Employer Laptop:

```bash
# Check vault status
loggerheads balance

# Should show:
# - Total funded
# - Employee earned amount
# - Remaining balance
```

---

## Daily Workflow

### Employee:
1. **Morning:** Log in → Tracking starts automatically
2. **Work:** Work normally, app tracks in background
3. **Evening (18:00):** Hours auto-submit to blockchain
4. **Anytime:** Withdraw earnings with `loggerheads withdraw`

### Employer:
- Monitor vault status: `loggerheads balance`
- View configuration: `loggerheads config`
- **No tracking needed** on employer laptop

---

## Production vs Devnet

**For Testing (Devnet):**
```bash
solana config set --url devnet
```

**For Production (Mainnet):**
```bash
solana config set --url mainnet-beta
```

**IMPORTANT:** Use devnet for initial testing. Switch to mainnet only when ready for real money.

---

## Troubleshooting

### "Command not found: loggerheads"

```bash
# Reinstall
cd loggerheads
pip3 install -e .

# Check installation
which loggerheads
```

### "No hours detected"

```bash
# Is tracker running?
ps aux | grep loggerheads

# Restart tracker
pkill -f loggerheads
loggerheads start
```

### "Transaction failed"

```bash
# Check SOL balance
solana balance

# Get more devnet SOL
solana airdrop 2

# For mainnet, you need to buy SOL
```

### "Vault not found"

- Verify employer created the vault first
- Check addresses match:
  ```bash
  loggerheads config
  ```
- Ensure both using same network (devnet or mainnet)

---

## Key Differences from Development Setup

This guide is for **production use**, not development:

- ✅ Clone from GitHub (stays up to date with pulls)
- ✅ Install with `pip3 install -e .` (editable mode, easy updates)
- ✅ Real vaults, real tracking, real payments
- ✅ Both employer and employee use same installation method

**This is NOT for:**
- Contributing code to the project
- Running tests
- Modifying the codebase

For development/contributing, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Updating to Latest Version

On both laptops:

```bash
cd loggerheads
git pull
pip3 install -e .
```

That's it! Changes take effect immediately.

---

## Multiple Employees

For each additional employee:

1. **Employee** creates wallet, sends address to employer
2. **Employer** runs `loggerheads` → Create new vault → Enter employee address
3. **Employee** configures vault with employer address
4. **Employee** starts tracking

Each employee tracks independently on their own laptop.

---

## Support

- **Issues:** https://github.com/stElmitchay/loggerheads/issues
- **Full Deployment Guide:** See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
- **Network:** Solana Devnet (testing) or Mainnet (production)

---

## Summary

**Employer laptop:**
1. Install Solana CLI
2. Clone repo + install: `git clone` + `pip3 install -e .`
3. Create wallet
4. Create vault for employee
5. Done - no tracking

**Employee laptop:**
1. Install Solana CLI
2. Clone repo + install: `git clone` + `pip3 install -e .`
3. Create wallet
4. Configure vault (after employer creates it)
5. Start tracking: `loggerheads start`

Both laptops ready for production use!
