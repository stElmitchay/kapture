# Kapture Architecture - How Everything Works

## System Overview

Kapture combines off-chain work tracking with on-chain payment enforcement through an oracle-based architecture.

```
┌─────────────────┐
│   EMPLOYEE      │
│   - Tracks work │
│   - Screenshots │
│   - Local DB    │
└────────┬────────┘
         │
         │ Work Summary
         ▼
┌─────────────────┐
│   ORACLE        │
│   - Verifies    │
│   - Signs       │
│   - Submits     │
└────────┬────────┘
         │
         │ Signed Transaction
         ▼
┌─────────────────┐
│  SMART CONTRACT │
│  (Solana)       │
│  - Validates    │
│  - Unlocks $$$  │
└─────────────────┘
```

## Components

### 1. Off-Chain Tracking (Employee's Machine)

**Files:**
- `activity_tracker.py` - Monitors active windows
- `database.py` - Stores screenshots and logs in SQLite
- `cli/` - User interface commands

**What happens:**
- Takes screenshots every few minutes
- OCR extracts text from screenshots
- AI analyzes work activity
- Calculates hours worked
- All stored locally at `~/.loggerheads_logs/`

### 2. Oracle (Independent Service)

**Files:**
- `oracle_secure.py` - Oracle keypair management
- `auto_submit.py` - Submission logic

**What it does:**
- Acts as neutral third party
- Verifies work hours are legitimate
- Signs transactions with oracle keypair
- Submits to blockchain

**Current Implementation (Devnet Testing):**
- Oracle keypair shared among testers
- Submission happens client-side (employee has keypair)
- Allows full testing without backend infrastructure

**Production Implementation (Future):**
- Oracle runs as API service
- Employees POST work proof to API
- Oracle verifies server-side
- Oracle signs and submits
- Keypair never leaves secure server

### 3. Smart Contract (Solana Blockchain)

**Files:**
- `workchain-program/programs/workchain-program/src/lib.rs`

**Instructions:**

1. **initialize_vault** (Employer creates vault)
   - Stores: employee, admin, oracle, amounts, rules
   - Locks USDC in vault token account

2. **submit_hours** (Oracle only)
   - Requires oracle signature (prevents fraud)
   - Checks if hours >= daily_target_hours
   - If yes → unlocks daily_unlock amount
   - If no → payment forfeited

3. **withdraw** (Employee only)
   - Requires employee signature
   - Transfers unlocked USDC to employee wallet
   - Updates vault balance

### 4. Python Integration (Client Side)

**Files:**
- `blockchain.py` - All blockchain interactions
- `vault_creation.py` - Employer creates vaults
- `token_utils.py` - Balance checking

## Data Flow: Complete Lifecycle

### Setup Phase

```
EMPLOYER:
1. Generates Solana wallet
2. Gets USDC (funds vault)
3. Runs: loggerheads (choose Employer)
4. Creates vault with employee wallet + rules
   → Calls initialize_vault on smart contract
   → Transfers USDC to vault

EMPLOYEE:
1. Generates Solana wallet
2. Gets employer's wallet address
3. Runs: loggerheads (choose Employee)
4. System derives vault PDA from employee + admin wallets
   → No need to manually enter vault addresses!
```

### Daily Work Phase

```
EMPLOYEE:
1. Runs: loggerheads start
2. Works normally (8 hours)
3. Screenshots captured every few minutes
4. Data stored in ~/.loggerheads_logs/activity_log.db

AT END OF DAY:
1. Employee/Oracle submits hours
2. calculate_hours_worked_today() queries database
3. Calculates time from first to last screenshot
4. Returns hours (e.g., 8.2 hours)
```

### Submission Phase

```
CURRENT (Devnet Testing):
1. auto_submit.py runs (cron job or manual)
2. Loads oracle keypair from ~/.loggerheads/oracle-keypair.json
3. Calls submit_hours() in blockchain.py
4. Builds instruction with oracle signature
5. Sends transaction to Solana

FUTURE (Production):
1. Employee runs: loggerheads submit
2. Packages work proof (screenshots, hours, timestamp)
3. POSTs to Oracle API: /submit-hours
4. Oracle verifies proof is legitimate
5. Oracle signs and submits to blockchain
6. Returns transaction signature to employee
```

### Payment Phase

```
SMART CONTRACT:
1. Receives submit_hours transaction
2. Validates oracle signature matches vault.oracle
3. Checks: hours_worked >= vault.daily_target_hours
4. If true:
   - vault.unlocked_amount += vault.daily_unlock
   - Emits success log
5. If false:
   - No unlock
   - Payment forfeited

EMPLOYEE WITHDRAWAL:
1. Runs: loggerheads withdraw
2. Calls withdraw() in smart contract
3. Transfers USDC from vault to employee token account
4. Updates vault.unlocked_amount
```

## Security Model

### Trust Assumptions

**Employer trusts:**
- Oracle to verify work legitimately
- Smart contract to enforce rules correctly

**Employee trusts:**
- Employer to fund vault as agreed
- Oracle to submit hours fairly
- Smart contract to unlock payment when earned

**Oracle is trusted by both:**
- Prevents employee from faking hours
- Prevents employer from denying payment
- Neutral arbitrator

### Attack Vectors & Mitigations

**Employee fakes hours:**
- ❌ Can't work without oracle signature
- ✅ Oracle verifies screenshots/activity before signing

**Employer doesn't pay:**
- ❌ Can't stop smart contract from unlocking
- ✅ Funds pre-locked in vault, automatic release

**Oracle colludes with employee:**
- ⚠️  Could sign fake hours
- ✅ Employer can audit blockchain + choose trusted oracle
- ✅ Future: Multiple oracles required (decentralization)

**Oracle colludes with employer:**
- ⚠️  Could refuse to sign real hours
- ✅ Employee can prove work with screenshots
- ✅ Future: Dispute resolution mechanism

## Key Design Decisions

### 1. Why Oracle Instead of Direct Submission?

**With Oracle:**
```
Employee → Oracle → Blockchain
         (verifies)  (enforces)
```
- Work must be verified
- Prevents fraud
- Trustless for employer

**Without Oracle:**
```
Employee → Blockchain
         (no verification)
```
- Employee could fake hours
- Defeats purpose of system
- Employer has no protection

### 2. Why Derive Vault PDA Instead of Storing Address?

**Current (Deterministic Derivation):**
```rust
vault_pda = derive(employee_wallet, admin_wallet)
```
- Employee only needs: admin wallet
- Everything else derived automatically
- Simple UX

**Alternative (Manual Entry):**
```
Employee needs: vault PDA, vault token account, employee token account...
```
- Complex UX
- Error-prone
- Horrible onboarding

### 3. Why SQLite Instead of Blockchain for Tracking?

**Off-chain (Current):**
- Fast: No blockchain latency
- Cheap: No transaction fees
- Private: Screenshots stay local
- Scalable: No blockchain storage costs

**On-chain (Alternative):**
- Every screenshot → transaction
- Costs SOL per screenshot
- Public data (privacy issue)
- Slow and expensive

**Best of both:**
- Track off-chain (fast, cheap, private)
- Submit summary on-chain (verified, immutable)

## Migration Path: Devnet → Production

### Current State (Devnet Testing)
- [x] Smart contract deployed on devnet
- [x] Python client working
- [x] Oracle keypair shared among testers
- [x] Manual and auto-submit working
- [x] End-to-end flow functional

### Before Mainnet
- [ ] Migrate smart contract to mainnet
- [ ] Change USDC_MINT to mainnet USDC
- [ ] Change RPC_URL to mainnet
- [ ] Deploy oracle as API service
- [ ] Update clients to POST to oracle API
- [ ] Security audit of smart contract
- [ ] Load testing

### Oracle Service Requirements

**Infrastructure:**
```
Oracle API (Node.js/Python)
├── POST /submit-hours
│   ├── Verify employee wallet
│   ├── Validate work proof
│   ├── Check rate limits
│   ├── Sign transaction
│   └── Submit to blockchain
├── GET /oracle-pubkey
│   └── Return oracle public key
└── GET /status
    └── Health check
```

**Database:**
```
submissions
├── employee_wallet
├── admin_wallet
├── hours
├── timestamp
├── transaction_signature
└── status
```

**Security:**
- Oracle keypair in secure enclave
- Rate limiting per wallet
- DDoS protection
- Logging and monitoring
- Fraud detection algorithms

## File Reference

**Core Blockchain:**
- `blockchain.py:392` - submit_hours() - Submits to chain
- `blockchain.py:137` - load_keypair() - Loads user wallet
- `blockchain.py:172` - derive_vault_pda() - Derives vault address

**Tracking:**
- `database.py:114` - calculate_hours_worked_today()
- `activity_tracker.py` - Screenshot capture
- `cli/dashboard_textual.py` - Live dashboard

**Oracle:**
- `oracle_secure.py:59` - get_oracle_keypair()
- `oracle_secure.py:102` - generate_oracle_keypair()
- `auto_submit.py:14` - auto_submit() - Daily submission

**Vault:**
- `vault_creation.py:32` - create_vault_interactive()
- `vault_creation.py:194` - create_vault_on_chain()
- `vault_config.py` - Stores vault configuration

**CLI:**
- `cli/__init__.py` - Command routing
- `cli/onboarding.py` - First-time setup
- `cli/commands/` - All commands

**Smart Contract:**
- `workchain-program/programs/workchain-program/src/lib.rs`
  - Line 11: initialize_vault
  - Line 51: submit_hours
  - Line 89: withdraw
