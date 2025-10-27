# Kapture

**Unlock Your Days**

Get paid your full salary upfront, then unlock it daily by proving you worked.

---

## What Is This?

Kapture flips traditional payment on its head:

**Traditional Way:**
- Work for 2 weeks or a month
- Wait until payday
- You get paid

**The Kapture Way:**
- Get your full monthly salary upfront (e.g., $3,000)
- It's locked in a blockchain vault
- Each day you hit your work quota → That day's portion unlocks (e.g., $150)
- Miss your quota → You lose that day's payment
- Everything is automatic and verified on the blockchain

**Example:**

You're a UX engineer earning $3,000/month. On day 1:
- Your employer locks $3,000 USDC in a vault for you
- You need to work 8 hours/day to unlock $150/day
- Kapture tracks your work automatically throughout the day
- At the end of the day, proof is sent to the blockchain
- If you worked 8+ hours → $150 unlocks to your wallet
- If you worked less → You lose that $150
- Repeat for 20 working days

**Who Is This For?**
- **Companies with remote workers** - Ensure accountability without micromanagement
- **DAOs** - Pay contributors with built-in verification
- **Freelancers** - Build trust with new clients through provable work
- **Self-discipline** - Lock your own money to force yourself to work
- **Bootcamps/Education** - Students unlock refunds by completing daily work
- **Anyone** who wants automatic, trustless work verification

---

## Installation

### What You Need
- **Python 3.8 or newer** - Check by running `python3 --version` in your terminal
- **Git** - Check by running `git --version` in your terminal
- **Solana CLI** - Check by running `solana --version` in your terminal
- **macOS or Linux** - Currently supported platforms
- **5-10 minutes** for setup

### Step 1: Clone the Repository

Open your terminal and run:
```bash
git clone https://github.com/stElmitchay/kapture
cd kapture
```

### Step 2: Install Python Dependencies

Run this command:
```bash
pip3 install -e .
```

This installs all the Python packages Kapture needs.

### Step 3: Run Kapture

Now you're ready! Run:
```bash
loggerheads
```

You'll see a menu with simple questions. The app will guide you through the rest of the setup.

**First time?** It will ask if you're an employer or employee, then walk you through creating a vault or connecting to one.

---

## How To Use It

### If You're An Employer

**Setup (takes 5 minutes):**

1. Run `loggerheads`
2. Choose "Employer" when asked
3. Create a payment vault (the app will guide you)
4. Put USDC into the vault (e.g., $3,000 for one employee for one month)
5. Set the rules:
   - Daily work hours needed (e.g., 8 hours)
   - Daily payment amount (e.g., $150)
6. Give your wallet address to your employee

That's it! Your employee sets up their app and starts working. Money unlocks automatically each day they hit their quota.


### If You're An Employee

**Setup (takes 2 minutes):**

1. Run `loggerheads`
2. Choose "Employee" when asked
3. Enter your employer's wallet address (they'll give you this)
4. Say "yes" to auto-submit (recommended)
5. Done!

**Daily usage:**

```bash
loggerheads start
```

Just work normally. Kapture captures your activity automatically. At the end of the day:
- Your hours are calculated
- Proof is sent to the blockchain
- If you hit your quota → Money unlocks
- A summary gets sent to Discord (if configured)

Press Ctrl+C when you're done working.

**Check your money:**
```bash
loggerheads balance      # See what you've unlocked
loggerheads withdraw     # Send it to your wallet
```


---

## All Commands

```bash
loggerheads              # Open the menu (start here if you're new)
loggerheads start        # Start tracking your work
loggerheads status       # See how many hours you've worked today
loggerheads balance      # Check how much money you've unlocked
loggerheads submit       # Send your hours to the blockchain (happens automatically)
loggerheads withdraw     # Move unlocked money to your wallet
loggerheads config       # See your settings
loggerheads help         # Show all commands
```

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

