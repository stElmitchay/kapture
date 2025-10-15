# WorkChain Smart Contract

**Status:** ✅ DEPLOYED TO DEVNET + Python Integration Complete!

## What We Built

A minimal Solana smart contract (238 lines of Rust) that implements the core flow:

1. Admin deposits money + sets target
2. Oracle submits daily hours
3. Auto-unlock if target met, forfeit if not
4. Employee withdraws unlocked funds

## Smart Contract Structure

### Account (1)
- `Vault` - Stores locked/unlocked balances, target hours, employee/admin/oracle wallets

### Instructions (3)

1. **initialize_vault** - Admin creates vault and locks USDC
   - Input: locked_amount, daily_target_hours, daily_unlock
   - Action: Creates vault PDA, transfers USDC from admin

2. **submit_hours** - Oracle submits daily work hours
   - Input: hours_worked
   - Action: Compares to target, auto-unlocks if met

3. **withdraw** - Employee withdraws unlocked funds
   - Input: amount
   - Action: Transfers USDC from vault to employee

## Files Created

```
workchain-program/
├── programs/workchain-program/src/
│   └── lib.rs                    # 238 lines - Complete smart contract
├── tests/
│   └── workchain-program.ts      # 193 lines - Full test suite
└── Cargo.toml                    # Dependencies (anchor-lang, anchor-spl)
```

## Build

```bash
cd workchain-program
cargo build-sbf
```

**Status:** ✅ Compiled successfully

## Deployment Info

**Network:** Solana Devnet
**Deployed:** ✅ Yes
**Deploy Transaction:** `3m8j8JBQuBDT8ain1E1CAiuiKy4Rz34ykBwpysaNtKVXreY8zSR6TcaN4BpktUAS1ehDBJxydLdV6BXtwd2nT92v`

**Explorer Links:**
- Program: https://explorer.solana.com/address/5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D?cluster=devnet
- Transaction: https://explorer.solana.com/tx/3m8j8JBQuBDT8ain1E1CAiuiKy4Rz34ykBwpysaNtKVXreY8zSR6TcaN4BpktUAS1ehDBJxydLdV6BXtwd2nT92v?cluster=devnet

## Python Integration

✅ Python blockchain integration complete!

**New Files:**
- `../loggerheads/blockchain.py` - Solana integration (submit, withdraw, vault info)
- `../INTEGRATION_GUIDE.md` - Full testing and demo guide

**CLI Commands:**
```bash
# Submit work hours
loggerheads submit <employee_pubkey> <admin_pubkey>

# Withdraw unlocked funds
loggerheads withdraw <amount> <admin_pubkey> <vault_token> <owner_token>

# Check vault status
loggerheads vault-info <employee_pubkey> <admin_pubkey>
```

See `../INTEGRATION_GUIDE.md` for complete end-to-end testing instructions.

## Program ID

```
5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D
```

(Note: This will change when we deploy to devnet)

---

**Stage 1 of hackathon complete!** 🚀
