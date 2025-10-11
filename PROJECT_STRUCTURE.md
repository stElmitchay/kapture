# WorkChain - Project Structure

## Recommended: Monorepo Structure

**Why:** Everything in one place, easier to develop/demo

```
daily_log_ai/                        # Current repo (root)
├── README.md                        # Updated for WorkChain
├── OVERVIEW.md                      # High-level concept
├── TECHNICAL_ARCHITECTURE.md        # Full specs
├── HACKATHON.md                     # What we're building
│
├── loggerheads/                     # Existing Python app
│   ├── __init__.py
│   ├── config.py
│   ├── activity_tracker.py         # Existing
│   ├── ai_summarizer.py            # Existing
│   ├── database.py                 # Existing
│   ├── cli.py                      # MODIFY: Add blockchain commands
│   └── blockchain.py               # NEW: Solana integration
│
├── workchain-program/              # NEW: Anchor smart contract
│   ├── Anchor.toml
│   ├── Cargo.toml
│   ├── programs/
│   │   └── workchain/
│   │       ├── Cargo.toml
│   │       ├── Xargo.toml
│   │       └── src/
│   │           └── lib.rs          # Smart contract
│   ├── tests/
│   │   └── workchain.ts            # Tests
│   ├── migrations/
│   │   └── deploy.ts
│   └── target/                     # Build artifacts (gitignored)
│
├── scripts/                        # NEW: Helper scripts
│   ├── setup-wallets.sh            # Create test wallets
│   ├── deploy-devnet.sh            # Deploy to devnet
│   └── demo.sh                     # Run full demo
│
├── .env.example                    # Wallet keys, RPC URLs
├── .gitignore                      # Add target/, .anchor/, wallets/
└── package.json                    # For Anchor/TS dependencies
```

---

## Alternative: Separate Repos

If you prefer separation:

```
workchain/                          # Parent folder
├── workchain-tracker/              # Python app (Loggerheads)
│   └── loggerheads/
│       └── ...
│
└── workchain-contract/             # Smart contract
    └── workchain-program/
        └── ...
```

**Pros:** Clean separation, independent versioning
**Cons:** Harder to demo, need to sync, more setup

---

## Recommendation for Hackathon: Monorepo

Keep everything in `daily_log_ai/`:

```
daily_log_ai/
├── loggerheads/          # Python (already here)
└── workchain-program/    # Anchor (add this)
```

**Why:**
- ✅ One `git clone`, ready to go
- ✅ Judges can see everything
- ✅ Easy to demo
- ✅ Shared docs/README
- ✅ Less context switching

---

## How to Build

### Step 1: Initialize Anchor Project

```bash
cd /Users/mitch_1/daily_log_ai
anchor init workchain-program
```

This creates:
```
workchain-program/
├── Anchor.toml
├── programs/workchain/src/lib.rs
└── tests/workchain.ts
```

### Step 2: Add Python Blockchain Module

```bash
cd loggerheads
touch blockchain.py
```

### Step 3: Link Them

In `loggerheads/config.py`:
```python
# Point to deployed program
WORKCHAIN_PROGRAM_ID = "..." # After deployment
```

In `loggerheads/blockchain.py`:
```python
# Load IDL from workchain-program/target/idl/workchain.json
```

---

## Development Workflow

```bash
# Terminal 1: Smart contract development
cd daily_log_ai/workchain-program
anchor build
anchor test
anchor deploy --provider.cluster devnet

# Terminal 2: Python development
cd daily_log_ai/loggerheads
python -m loggerheads create-vault ...
python -m loggerheads submit ...
```

---

## What Gets Committed to Git

```
# .gitignore additions

# Anchor
workchain-program/target/
workchain-program/.anchor/
workchain-program/node_modules/

# Wallets (NEVER commit private keys)
*.json  # Wallet keypairs
.env    # Environment secrets

# Python
__pycache__/
*.pyc
*.egg-info/
```

---

## Final Structure

```
daily_log_ai/
│
├── docs/
│   ├── OVERVIEW.md
│   ├── TECHNICAL_ARCHITECTURE.md
│   └── HACKATHON.md
│
├── loggerheads/                    # Python tracker
│   ├── blockchain.py               # NEW
│   └── cli.py                      # MODIFY
│
├── workchain-program/              # NEW: Smart contract
│   └── programs/workchain/src/
│       └── lib.rs
│
├── README.md                       # Main README
└── .env.example
```

Clean, simple, one repo.

Ready to initialize the Anchor project?
