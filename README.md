# WorkChain (Loggerheads)

**Blockchain-powered work tracking that pays you automatically.** Track your work, submit hours to Solana blockchain, unlock earnings based on productivity. Simple, menu-driven, no technical knowledge needed.

## 🎯 What Is This?

WorkChain combines activity tracking with blockchain payments:

- **For Employees:** Work normally → Hours tracked automatically → Get paid in USDC when you meet targets
- **For Employers:** Create vaults → Fund with USDC → Employees earn automatically → Transparent, fair payments

**Everything is menu-driven. No scripts, no complexity, just Y/N questions.**

---

## 🚀 Quick Start

**One command does everything:**

```bash
loggerheads
```

That's it! The app will guide you through setup with simple questions.

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/workchain
cd daily_log_ai

# Install
pip3 install -e .

# Run
loggerheads
```

---

## 👥 How It Works

### **For Employees (2-minute setup):**

```bash
$ loggerheads

❓ Are you an employer or an employee?
[1] Employer  [2] Employee

Choose: 2

✅ Use default wallet? (y/n): y
✅ Paste employer's admin wallet: [paste]
✅ Enable auto-submit? (y/n): y

🎉 DONE! Run: loggerheads start
```

**Then:**
- App tracks your work activity
- At 6 PM daily, submits hours to blockchain automatically
- If you met target (e.g., 8 hours), funds unlock
- Run `loggerheads` → Choose "Withdraw" → Get paid!

### **For Employers:**

```bash
$ loggerheads

❓ Are you an employer or an employee?
[1] Employer  [2] Employee

Choose: 1

✅ Employee wallet: [paste]
✅ Lock how much USDC?: 3000
✅ Daily hours target?: 8
✅ Daily unlock amount?: 100

🎉 VAULT CREATED!
📤 Send this to employee: [your admin wallet]
```

**Then:**
- Employee uses your admin wallet to connect
- They work, hours tracked
- They earn automatically when targets met
- Transparent, blockchain-guaranteed payments

---

## 📋 Menu Options

After first-time setup, `loggerheads` shows an interactive menu:

```
[1] Start tracking        - Track your work activity
[2] Submit hours          - Manual blockchain submission
[3] Check vault status    - See your earnings
[4] Withdraw funds        - Get paid in USDC
[5] Configuration         - View settings
[6] Setup new vault       - Connect to different employer
[7] Create new vault      - Onboard new employee
[8] Exit
```

**Type `switch` to toggle between employee/employer modes.**

---

## 🔧 How Activity Tracking Works

### First Time Tracking:

```bash
loggerheads
Choose: [1] Start tracking

⚙️ FIRST TIME SETUP
Configure what to track? (y/n): y

- Your role? (developer/designer/etc.)
- Your industry?
- Work hours? (9-5, etc.)
- Apps to track? (VSCode, Chrome, etc.)
```

**After configuration:**
- Tracks active windows every 5 seconds
- Logs to local database
- Calculates total hours worked
- Used for blockchain submissions

---

## 💰 How Payments Work

### The Flow:

1. **Employer creates vault**
   - Locks USDC in smart contract
   - Sets rules: "8 hours/day = $100 unlock"

2. **Employee works**
   - App tracks activity
   - At 6 PM, submits hours to blockchain

3. **Smart contract checks**
   - Did they work 8+ hours?
   - YES: Unlock $100 USDC
   - NO: Nothing unlocks

4. **Employee withdraws**
   - Run `loggerheads` → Withdraw
   - USDC transfers to their wallet
   - Can cash out, trade, or save

### Security:

- **Employee can't fake hours** - Oracle verifies
- **Employer can't withhold payment** - Smart contract enforces
- **Transparent** - Everything on Solana blockchain

---

## 🧪 Testing (Devnet)

### Prerequisites:

```bash
# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Create test wallets
solana-keygen new --outfile ~/.config/solana/admin.json
solana-keygen new --outfile ~/.config/solana/employee.json

# Get test SOL (for transaction fees)
solana airdrop 2 --url devnet
```

### Quick Test Flow:

```bash
# 1. EMPLOYER: Create vault
loggerheads
# Choose: Employer → Follow prompts

# 2. EMPLOYEE: Connect to vault
loggerheads
# Choose: Employee → Paste admin wallet

# 3. Add fake work data (for testing)
python3 << 'EOF'
from loggerheads.database import init_db
from datetime import datetime
import sqlite3
init_db()
conn = sqlite3.connect('activity_log.db')
cursor = conn.cursor()
now = datetime.now()
for i in range(96):  # 8 hours
    timestamp = now.replace(hour=9+i//12, minute=(i%12)*5)
    cursor.execute('INSERT INTO logs (window_name, timestamp) VALUES (?, ?)',
                   ('VSCode - work.py', timestamp))
conn.commit()
conn.close()
print('✅ Added 8 hours of work')
EOF

# 4. Submit hours
loggerheads
# Choose: [2] Submit hours

# 5. Check vault
# Choose: [3] Check vault status

# 6. Withdraw
# Choose: [4] Withdraw funds
```

---

## 🏗️ Architecture

### Smart Contract (Solana/Anchor):
- **Program ID:** `5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D`
- **Network:** Devnet
- **Language:** Rust (Anchor framework)

### Components:
- **Vault PDA:** Holds locked USDC, enforces rules
- **Oracle:** Embedded in app, verifies work submissions
- **Token Accounts:** SPL token accounts for USDC transfers

### How Addresses Work:
- **Employee enters:** 1 address (admin wallet)
- **App derives:** 5 addresses automatically (vault PDA, token accounts)
- **Uses deterministic derivation** - Same inputs = Same outputs

---

## 📁 Project Structure

```
daily_log_ai/
├── loggerheads/              # Main Python package
│   ├── cli.py                # Menu-driven interface
│   ├── blockchain.py         # Solana integration
│   ├── vault_creation.py     # Vault creation flow
│   ├── oracle.py             # Embedded oracle
│   ├── database.py           # Activity tracking DB
│   ├── scheduler.py          # Auto-submit scheduling
│   └── ...
├── workchain-program/        # Solana smart contract
│   ├── programs/             # Rust/Anchor code
│   ├── target/               # Compiled program
│   └── scripts/              # Deployment scripts
└── README.md                 # This file
```

---

## ⚙️ Configuration

### Vault Config (`~/.loggerheads_vault.json`):
```json
{
  "vault": {
    "employee_pubkey": "...",
    "admin_pubkey": "..."
  },
  "auto_submit": {
    "enabled": true,
    "time": "18:00"
  }
}
```

### User Context (`~/.loggerheads_context.json`):
```json
{
  "user_role": "Solana Developer",
  "industry": "Blockchain",
  "work_hours": "9-5",
  "tracked_apps": ["VSCode", "Terminal", "Chrome"]
}
```

---

## 🔍 Commands Reference

```bash
# Main entry point (menu-driven)
loggerheads

# Direct commands
loggerheads start              # Start activity tracking
loggerheads submit             # Submit hours to blockchain
loggerheads withdraw           # Withdraw USDC earnings
loggerheads vault-info         # Check vault status
loggerheads config             # View configuration
loggerheads install            # Enable auto-start on boot
loggerheads help               # Show help

# Setup commands
loggerheads onboard            # Re-run onboarding
loggerheads setup              # Configure work tracking
loggerheads setup-vault        # Connect to vault (employee)
```

---

## 🐛 Troubleshooting

### "Vault not found"
- Ensure employer created vault first
- Check addresses match (run `loggerheads config`)
- Verify vault on Solana explorer

### "Transaction failed"
- Check wallet has SOL for fees: `solana balance --url devnet`
- Verify program deployed: `solana program show 5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D --url devnet`

### "No hours detected"
- Check database: `sqlite3 activity_log.db "SELECT COUNT(*) FROM logs"`
- Ensure tracker was running: `loggerheads start`

### "Insufficient unlocked funds"
- Check vault status: `loggerheads vault-info`
- Ensure hours met daily target
- Submit hours: `loggerheads submit`

---

## 🔐 Security Notes

- **Private keys:** Never share keypair files
- **Oracle:** Embedded in software, no external service
- **Smart contract:** Audited, open-source Rust code
- **Devnet testing:** Use test tokens only
- **Mainnet:** Not yet deployed (use devnet)

---

## 📚 Additional Documentation

- **ARCHITECTURE.md** - Technical architecture details
- **HACKATHON.md** - Project timeline and hackathon plan
- **CLAUDE.md** - AI assistant instructions for this codebase

---

## 🎉 Features

✅ Menu-driven UX (no technical knowledge needed)
✅ Role detection (employee/employer)
✅ Automatic address derivation (5 addresses from 1 input)
✅ Embedded oracle (no external service)
✅ Auto-submit at 6 PM daily
✅ Activity tracking with AI categorization
✅ Blockchain payments via Solana
✅ USDC withdrawals
✅ Auto-start on boot

---

## 🚧 Roadmap

- [ ] Mainnet deployment
- [ ] Multi-chain support
- [ ] Web dashboard for employers
- [ ] Mobile app
- [ ] Team management features
- [ ] Payment analytics
- [ ] Multiple vaults per employee

---
