# Quick Start: Employee

## 10-Minute Setup (One Time Only!)

### 1. Install Solana
```bash
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

Add to your shell config (`~/.zshrc` or `~/.bashrc`):
```bash
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
```

Reload:
```bash
source ~/.zshrc  # or ~/.bashrc
```

### 2. Create Your Wallet
```bash
solana-keygen new
```

**SAVE THE SEED PHRASE!** Write it down somewhere safe.

### 3. Get Your Address
```bash
solana address
```

**Send this to your employer** - they need it.

### 4. Install Loggerheads
```bash
pip3 install loggerheads
```

### 5. Set Up Your Work Account
```bash
loggerheads
```

- Choose: **[2] Employee**
- Paste: **Employer address** (they sent you this)
- Auto-submit? → **y**
- Time? → **18:00** (or when you finish work)

### 6. Install Auto-Start
```bash
loggerheads install
```

### 7. Start Tracking
```bash
loggerheads start
```

## Done! ✅

Now just work normally. The system:
- ✅ Tracks your work automatically
- ✅ Submits hours at 18:00 daily
- ✅ Unlocks payment when you hit target
- ✅ Lets you withdraw anytime

---

## Daily Use

### Morning:
- Log in to laptop
- Tracker starts automatically
- Work normally

### Evening (18:00):
- Hours auto-submit
- Payment unlocks (if target met)

### Check Status:
```bash
# See hours today
loggerheads status

# Check earnings
loggerheads balance
```

### Withdraw Money:
```bash
loggerheads withdraw
```

---

## Troubleshooting

### "Hours showing 0.0"
```bash
# Is tracker running?
loggerheads status

# Restart tracker
pkill -f loggerheads
loggerheads start
```

### "Can't submit hours"
```bash
# Check config
loggerheads config

# Verify employer address is correct
```

### "Need help"
```bash
loggerheads help
```

---

## What Gets Tracked?

✅ **Work Activities:**
- Code editors (VS Code, Cursor, PyCharm, etc.)
- Terminal/command line
- Documentation/tutorials
- Work-related browsing
- Work chat (Slack about projects)

❌ **Filtered Out:**
- Personal WhatsApp chats
- YouTube music/entertainment
- Social media
- Shopping

The AI is smart - it knows "YouTube Python tutorial" is work, but "YouTube music" isn't!

---

## Privacy

- Screenshots stored locally on YOUR laptop
- OCR text analyzed to detect work
- Only hours (number) submitted to blockchain
- Screenshots deleted after summary generated
- You can check: `~/.loggerheads_logs/`
