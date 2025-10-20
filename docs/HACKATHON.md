# WorkChain - Hackathon Core Flow

**ONE GOAL: Prove the core mechanism works.**

---

## The Core Flow (Nothing Else Matters)

```
1. Admin deposits money + sets target
   ↓
2. User works (Loggerheads tracks)
   ↓
3. End of day: Check if target reached
   ↓
4. YES → Money unlocks automatically
   NO  → Money stays locked (forfeited)
```

**That's it. This is what we build.**

---

## Smart Contract (Ultra Minimal)

### ONE Account

```rust
#[account]
pub struct Vault {
    pub owner: Pubkey,           // Employee wallet
    pub admin: Pubkey,           // Admin wallet
    pub oracle: Pubkey,          // Loggerheads (trusted to report hours)

    pub locked_amount: u64,      // USDC locked
    pub unlocked_amount: u64,    // USDC available to withdraw
    pub daily_target_hours: u8,  // e.g., 6 hours
    pub daily_unlock: u64,       // e.g., 150 USDC

    pub bump: u8,
}
```

### THREE Instructions

```rust
// 1. Admin creates vault and deposits USDC
pub fn initialize_vault(
    ctx: Context<InitializeVault>,
    locked_amount: u64,        // 3000 USDC
    daily_target_hours: u8,    // 6 hours
    daily_unlock: u64,         // 150 USDC
) -> Result<()>

// 2. Oracle reports daily hours → auto-unlock if target met
pub fn submit_hours(
    ctx: Context<SubmitHours>,
    hours_worked: u8,
) -> Result<()> {
    // If hours >= target → unlock funds
    // If hours < target → do nothing (forfeit)
}

// 3. Employee withdraws unlocked funds
pub fn withdraw(
    ctx: Context<Withdraw>,
    amount: u64,
) -> Result<()>
```

**Total: ~150 lines of Rust. That's it.**

---

## Python (Minimal Addition)

### Add ONE file to Loggerheads

```python
# loggerheads/blockchain.py

def create_vault(admin_wallet, employee_wallet, amount, target_hours, daily_unlock):
    """Admin creates vault."""
    # Call initialize_vault instruction
    pass

def submit_hours(hours):
    """Submit today's hours to blockchain."""
    # Call submit_hours instruction
    # Contract automatically unlocks if hours >= target
    pass

def withdraw(amount):
    """Withdraw unlocked funds."""
    # Call withdraw instruction
    pass
```

### Update CLI

```python
# loggerheads/cli.py

elif command == "create-vault":
    # Admin command
    create_vault(...)

elif command == "submit":
    # Calculate hours from logs
    hours = calculate_hours_worked_today()
    submit_hours(hours)
    print(f"Submitted {hours} hours")

elif command == "withdraw":
    withdraw(float(sys.argv[2]))
    print(f"Withdrawn!")
```

**Total: ~100 lines of Python. That's it.**

---

## Demo (2 Minutes)

### Setup (Pre-Demo)

```bash
# Deploy contract
anchor deploy

# Admin creates vault
loggerheads create-vault \
  --admin ADM123... \
  --employee EMP456... \
  --amount 3000 \
  --target-hours 6 \
  --daily-unlock 150
```

### Day 1: Success

```bash
# User works all day
loggerheads start
# ... tracks work ...

# End of day
loggerheads submit
# Output:
# ✅ Worked 7 hours (target: 6)
# ✅ Unlocked $150 USDC
# TX: 5Kq8x...Mn3P
```

**Show Solana Explorer:** Transaction, logs showing unlock

```bash
# Withdraw
loggerheads withdraw 150
# Output:
# ✅ Withdrawn $150 USDC
# TX: 7Hs2p...Qq9X
```

**Show Phantom Wallet:** Balance increased

### Day 2: Failure

```bash
loggerheads submit
# Output:
# ❌ Worked 4 hours (target: 6)
# ❌ Did not unlock
# TX: 9Pf4d...Lz1K
```

**Show Solana Explorer:** Transaction, logs showing no unlock

**Show:** Money stays locked (forfeited)

---

## Implementation Timeline

### Hour 1-3: Smart Contract
- [ ] Init Anchor project
- [ ] Create Vault account struct
- [ ] Implement initialize_vault()
- [ ] Implement submit_hours() with auto-unlock logic
- [ ] Implement withdraw()
- [ ] Test locally

### Hour 4-5: Deploy & Test
- [ ] Deploy to devnet
- [ ] Test with Anchor client
- [ ] Verify transactions on Explorer

### Hour 6-8: Python Integration
- [ ] Create blockchain.py
- [ ] Implement 3 functions (create, submit, withdraw)
- [ ] Update CLI
- [ ] Test: Python → Solana

### Hour 9-10: End-to-End Test
- [ ] Create real vault
- [ ] Track real work with Loggerheads
- [ ] Submit hours
- [ ] Verify unlock
- [ ] Withdraw funds

### Hour 11-12: Demo Prep
- [ ] Record demo video
- [ ] Prepare pitch deck (5 slides)
- [ ] Practice presentation

**Total: 12 hours**

---

## What We're NOT Building

❌ Web dashboard
❌ Quality scoring
❌ Task counting
❌ Disputes
❌ Treasury
❌ Redistribution
❌ Multiple periods
❌ Pause/resume
❌ Discord integration (can add later if time)
❌ FastAPI
❌ Cron jobs (manual command instead)
❌ Database changes (use existing)
❌ Complex metrics

---

## Files We're Creating

```
workchain/                           # NEW: Anchor project
├── Anchor.toml
├── programs/workchain/src/
│   └── lib.rs                       # ~150 lines
└── tests/workchain.ts               # ~50 lines

loggerheads/
├── blockchain.py                    # NEW: ~100 lines
└── cli.py                           # MODIFY: +30 lines
```

**Total new code: ~280 lines**

---

## Success = This Works

```
┌─────────────────────────────────────────┐
│ Admin deposits 3000 USDC                │
│ Sets target: 6 hours/day                │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ User works 7 hours                      │
│ Loggerheads tracks                      │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Submit to blockchain                    │
│ Smart contract checks: 7 >= 6? YES     │
│ Auto-unlock 150 USDC                    │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ User withdraws 150 USDC                 │
│ Balance increases ✅                    │
└─────────────────────────────────────────┘

Next day: Works 4 hours → No unlock → Forfeited
```

**If this works, we win.**

---

## Pitch (30 seconds)

> "Remote workers have zero accountability. We flip the salary model: You get paid FIRST, your money locks in a Solana smart contract. Work your daily target? Unlock your pay. Don't work? Forfeit it. Loss aversion is 2x stronger than motivation. We built a working prototype: Admin deposits, employee works, blockchain automatically unlocks if target met. Watch."

*(Show 1-minute demo video)*

---

## Risk Mitigation

**Risk:** Solana RPC fails during demo
**Fix:** Record backup video

**Risk:** Wallet issues
**Fix:** Pre-fund wallets, test beforehand

**Risk:** Transaction takes too long
**Fix:** Show pre-generated Explorer links

**Risk:** Run out of time
**Fix:** Ship smart contract first (core innovation)

---

## Judging Criteria

✅ **Innovation:** Reverse salary model on blockchain (novel)
✅ **Technical:** Smart contract + AI integration (complex enough)
✅ **Utility:** Solves real remote work problem
✅ **Completeness:** Working end-to-end (money actually moves)

---

## Next Step

Start with smart contract. I'll create the Anchor project structure and implement the 3 instructions.

Ready?
