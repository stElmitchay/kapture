# Quick Start: Employer

## 5-Minute Setup

### 1. Check Your Wallet
```bash
solana address
```
**Save this** - give to employee later.

### 2. Get Tokens (Devnet Testing)
```bash
solana airdrop 2 --url devnet
```

### 3. Create Vault for Employee
```bash
loggerheads
```
- Choose: **[2] Employer**
- Choose: **[1] Create vault for employee**
- Enter employee wallet address
- Fund amount: **3000** USDC (example: 1 month @ $100/day)
- Daily hours: **8**
- Daily pay: **100** USDC

### 4. Send to Employee

After vault created, send employee:
```
Your employer address: <YOUR_WALLET_FROM_STEP_1>
```

## Done! ✅

**What NOT to do:**
- ❌ Don't run `loggerheads start` (that's for employee)
- ❌ Don't run `loggerheads submit` (that's for employee)
- ❌ Don't set up vault config (that's for employee)

## Monitor Employee

```bash
# Check how much they've earned
loggerheads balance

# See vault details
loggerheads config
```

## Create More Vaults

```bash
loggerheads
# Choose: Employer → Create vault
# Repeat for each employee
```
