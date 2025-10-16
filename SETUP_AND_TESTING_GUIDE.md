# WorkChain Setup & Testing Guide

Complete guide to setting up and testing the WorkChain system locally.

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [Understanding the System](#understanding-the-system)
3. [Detailed Setup](#detailed-setup)
4. [Testing the Flow](#testing-the-flow)
5. [How to Make It User-Friendly](#how-to-make-it-user-friendly)

---

## Quick Start

If you just want to test it quickly:

```bash
# 1. Create wallets
solana-keygen new --outfile ~/.config/solana/admin.json
solana-keygen new --outfile ~/.config/solana/employee.json
solana-keygen new --outfile ~/.config/solana/oracle.json

# 2. Fund wallets
solana config set --url https://api.devnet.solana.com
solana airdrop 5 $(solana-keygen pubkey ~/.config/solana/admin.json)
solana airdrop 2 $(solana-keygen pubkey ~/.config/solana/employee.json)
solana airdrop 2 $(solana-keygen pubkey ~/.config/solana/oracle.json)

# 3. Create vault
cd workchain-program
npm install
anchor build
npx ts-node scripts/create-vault.ts

# 4. Test (replace with your addresses from step 3)
cd ..
loggerheads vault-info <EMPLOYEE_PUBKEY> <ADMIN_PUBKEY>
```

---

## Understanding the System

### The Three Roles

**Admin (Company/Boss)**
- Creates vault once
- Deposits USDC into it
- Sets rules: target hours, unlock amount
- Never needs to do anything again

**Employee (Worker)**
- Works normally
- Loggerheads tracks automatically in background
- Can check status and withdraw unlocked funds

**Oracle (Loggerheads - Automated)**
- Tracks work via screenshots
- Submits hours to blockchain automatically (should be automated!)
- Triggers unlock when target is met

### What Each Address Means

When you create a vault, you get 6 addresses:

```
3 WALLETS (People):
├── ADMIN_PUBKEY          → The company's wallet
├── EMPLOYEE_PUBKEY       → The worker's wallet
└── ORACLE_PUBKEY         → Loggerheads' wallet

1 SMART CONTRACT:
└── VAULT_PDA             → The rules & logic

2 TOKEN ACCOUNTS (Bank accounts for USDC):
├── VAULT_TOKEN_ACCOUNT   → Vault's USDC storage (3000 USDC)
└── EMPLOYEE_TOKEN_ACCOUNT → Employee's USDC wallet (for withdrawals)
```

**Simple Analogy:**
- ADMIN = Company that fills a vending machine with $3000
- EMPLOYEE = Worker who can collect from it
- ORACLE = Sensor that checks if worker met target
- VAULT_PDA = The vending machine's computer (rules)
- VAULT_TOKEN_ACCOUNT = Cash box inside the machine
- EMPLOYEE_TOKEN_ACCOUNT = Worker's personal wallet

---

## Detailed Setup

### Step 1: Create Wallets

```bash
solana-keygen new --outfile ~/.config/solana/admin.json
solana-keygen new --outfile ~/.config/solana/employee.json
solana-keygen new --outfile ~/.config/solana/oracle.json
```

Each command creates a keypair (public + private key). Save the public keys displayed!

### Step 2: Fund Wallets with Devnet SOL

```bash
solana config set --url https://api.devnet.solana.com

# Admin needs more for creating accounts
solana airdrop 5 $(solana-keygen pubkey ~/.config/solana/admin.json)

# Employee and oracle need less
solana airdrop 2 $(solana-keygen pubkey ~/.config/solana/employee.json)
solana airdrop 2 $(solana-keygen pubkey ~/.config/solana/oracle.json)
```

### Step 3: Build the Smart Contract

```bash
cd workchain-program
npm install          # Install dependencies
anchor build         # Compile contract & generate IDL
```

### Step 4: Create the Vault

```bash
npx ts-node scripts/create-vault.ts
```

This script will:
1. Load your three wallets
2. Create a test USDC token mint (simulates real USDC)
3. Create token accounts for admin, vault, and employee
4. Mint 3000 test USDC to admin
5. Create the vault and transfer admin's USDC to it

**IMPORTANT:** Save all the addresses it prints! You'll need them for testing.

### Step 5: Verify Vault Creation

```bash
cd ..
loggerheads vault-info <EMPLOYEE_PUBKEY> <ADMIN_PUBKEY>
```

Should show:
```
💰 Vault Information:
   Total Locked: 3000.00 USDC
   Unlocked: 0.00 USDC
   Still Locked: 3000.00 USDC
   Daily Target: 6 hours
   Daily Unlock: 150.00 USDC
```

---

## Testing the Flow

### Option 1: Real Tracking (Slow)

```bash
# Start tracker - let it run for an hour or more
loggerheads start

# After working, submit hours
loggerheads submit <EMPLOYEE_PUBKEY> <ADMIN_PUBKEY>
```

### Option 2: Simulated Tracking (Fast)

```bash
# Simulate 7 hours of work
python3 << 'EOF'
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('activity_log.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS screenshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        extracted_text TEXT,
        log_id INTEGER
    )
''')

start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
for i in range(42):  # 7 hours * 6 screenshots/hour
    timestamp = start_time + timedelta(minutes=i * 10)
    cursor.execute(
        'INSERT INTO screenshots (file_path, timestamp) VALUES (?, ?)',
        (f'fake_{i}.png', timestamp.isoformat())
    )

conn.commit()
conn.close()
print('✅ Simulated 7 hours of work')
EOF

# Now submit
loggerheads submit <EMPLOYEE_PUBKEY> <ADMIN_PUBKEY>
```

Should show:
```
📊 Calculated hours worked today: 7
📤 Submitting 7 hours to blockchain...
✅ Success!
💰 Vault Status:
   Unlocked: 150.00 USDC
```

### Check Vault Again

```bash
loggerheads vault-info <EMPLOYEE_PUBKEY> <ADMIN_PUBKEY>
```

Now shows:
```
   Unlocked: 150.00 USDC  ← Changed!
```

### Withdraw Funds

```bash
loggerheads withdraw 150 <ADMIN_PUBKEY> <VAULT_TOKEN_ACCOUNT> <EMPLOYEE_TOKEN_ACCOUNT>
```

Should show:
```
💸 Withdrawing 150.0 USDC...
✅ Success!
```

---

## How to Make It User-Friendly

### Current UX Problems

❌ Too many manual commands
❌ User needs to copy/paste long addresses
❌ No visual feedback
❌ Manual submission required
❌ No menu system

### Ideal User Experience

#### For Admin (One-Time Setup):

```
$ loggerheads admin

┌─────────────────────────────────────────┐
│  WorkChain Admin Setup                  │
└─────────────────────────────────────────┘

Would you like to:
[1] Create a new vault for an employee
[2] View existing vaults
[3] Exit

Choice: 1

Creating new vault...

Enter employee email: john@company.com
Enter employee wallet (or press Enter to generate): [Enter]
✓ Generated wallet for john@company.com
  Address: 4BnpZWX...

How much USDC to deposit: 3000
Daily work target (hours): 6
Daily unlock amount (USDC): 150

✓ Vault created!
✓ 3000 USDC transferred from your wallet

Employee setup link:
https://workchain.app/setup?vault=FPZkD6d...

Send this link to john@company.com
```

#### For Employee (Daily Use):

```
$ loggerheads start

┌─────────────────────────────────────────┐
│  WorkChain - Auto Tracker               │
└─────────────────────────────────────────┘

✓ Connected to vault: FPZkD6d...
✓ Tracking started in background

Today's Progress:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Hours worked: 3.5 / 6.0
  Unlock status: 🔒 Locked (2.5 hours to go)

Auto-submission: ✓ Enabled (submits at 6 PM)
Status: Running in background...

Press Ctrl+C to stop
```

#### Auto-Submission (Background Service):

```
$ loggerheads install

✓ Installed WorkChain service
✓ Auto-tracking enabled (Mon-Fri, 9 AM - 6 PM)
✓ Auto-submission enabled (Daily at 6 PM)

Your vault is now fully automated!
```

### Implementation Plan

**1. Config File (Store addresses once)**
```json
{
  "vault": {
    "employee_pubkey": "4BnpZ...",
    "admin_pubkey": "Errir...",
    "vault_pda": "FPZkD...",
    "vault_token": "8EpV3...",
    "employee_token": "BtFs..."
  },
  "auto_submit": true,
  "submit_time": "18:00"
}
```

**2. Automatic Submission (Cron job or systemd timer)**
```python
# Auto-runs at 6 PM daily
def auto_submit():
    config = load_config()
    hours = calculate_hours_worked_today()

    if hours > 0:
        submit_hours(
            hours,
            config['vault']['employee_pubkey'],
            config['vault']['admin_pubkey']
        )
```

**3. Menu-Based CLI**
```python
def main_menu():
    while True:
        print_menu()
        choice = input("Choice: ")

        if choice == "1":
            start_tracking()
        elif choice == "2":
            show_vault_status()
        elif choice == "3":
            withdraw_menu()
        elif choice == "4":
            settings_menu()
```

**4. Status Dashboard**
```python
def show_status():
    """Real-time dashboard"""
    while True:
        clear_screen()
        print_header()
        print_hours_today()
        print_vault_balance()
        print_unlock_progress()
        time.sleep(5)  # Update every 5 seconds
```

---

## Next Steps

### Phase 1: Automation (High Priority)
- [ ] Auto-submission at end of day
- [ ] Store vault config in file
- [ ] Background tracking service

### Phase 2: Better UX (High Priority)
- [ ] Interactive menu system
- [ ] Real-time status dashboard
- [ ] One-command setup

### Phase 3: Admin Tools (Medium Priority)
- [ ] Admin web dashboard
- [ ] Multi-employee management
- [ ] Vault creation wizard

### Phase 4: Production (Low Priority - After Testing)
- [ ] Use real USDC instead of test tokens
- [ ] Deploy to mainnet
- [ ] Security audit

---

## Troubleshooting

### Error: "Vault not found"
- Vault wasn't created yet
- Run: `npx ts-node scripts/create-vault.ts`

### Error: "No work hours detected"
- Database is empty
- Run tracking first or use simulation script

### Error: "Insufficient funds"
- Wallet needs devnet SOL
- Run: `solana airdrop 2 <PUBKEY>`

### Error: "Unauthorized oracle"
- Wrong keypair file
- Make sure using `~/.config/solana/oracle.json`

---

## Summary

**Current State:**
✅ Smart contract deployed
✅ Python integration working
✅ Can create vaults
✅ Can submit hours manually
✅ Can withdraw funds

**Needs Improvement:**
❌ Too manual - needs automation
❌ No menu system - needs better UX
❌ Commands too complex - needs simplification

**Ideal Flow:**
1. Admin: One-time setup via web or CLI wizard
2. Employee: Install app, it runs in background
3. App: Auto-submits at end of day
4. Employee: Just checks balance and withdraws when ready

That's the vision! The tech works, now we need better UX.
