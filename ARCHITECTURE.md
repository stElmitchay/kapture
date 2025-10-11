# WorkChain - Technical Architecture & Implementation Plan

**Hackathon Project: Reverse Salary Accountability System on Solana**

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Core Concept](#core-concept)
3. [Use Cases & User Personas](#use-cases--user-personas)
4. [System Architecture](#system-architecture)
5. [Smart Contract Design](#smart-contract-design)
6. [Backend Architecture](#backend-architecture)
7. [Frontend Architecture](#frontend-architecture)
8. [Verification & Dispute System](#verification--dispute-system)
9. [Monetization Strategy](#monetization-strategy)
10. [MVP Roadmap](#mvp-roadmap)
11. [Technical Stack](#technical-stack)
12. [Security Considerations](#security-considerations)
13. [Future Enhancements](#future-enhancements)

---

## Executive Summary

**WorkChain** is a blockchain-based productivity accountability system that inverts traditional salary mechanisms. Instead of earning wages through work, employees/freelancers receive their full salary upfront, locked in a Solana smart contract. Daily productive work unlocks portions of this salary; unmet productivity thresholds result in forfeited funds (configurable by employer/admin).

**Inspiration:** Streamflow's conditional token unlocks + gamification psychology

**Differentiator:** Real-time work tracking (via Loggerheads) + AI verification + blockchain accountability

---

## Core Concept

### The Reverse Salary Mechanism

```
Traditional Model:
Work → Time Passes → Get Paid (delayed gratification)

WorkChain Model:
Get Paid → Work → Keep Your Money (loss aversion)
```

**Psychological Drivers:**
- **Loss Aversion:** Humans hate losing what they already have (2x stronger than gaining)
- **Immediate Stakes:** Money is locked NOW, not promised later
- **Daily Wins:** Small daily victories vs. distant monthly reward
- **Transparency:** On-chain proof of productivity

### Flow

```
Month Start:
1. Employer deposits $3,000 USDC to WorkChain contract (for employee)
2. Funds locked in employee's vault PDA
3. Employee configures: daily threshold = 6 hours productive work

Daily Cycle:
4. Loggerheads tracks employee activity (screenshots + AI analysis)
5. At 4:30 PM: AI generates work summary
6. Backend oracle submits work proof to Solana
7. Smart contract evaluates: hours >= threshold?
   ✅ YES: Unlock $150 USDC → employee can withdraw
   ❌ NO: $150 stays locked (forfeited at month end)

Month End:
8. Unearned funds redistributed per employer's policy:
   - Lost forever (burn)
   - Returned to employer treasury
   - Donated to charity
   - Rolled into next month bonus pool
```

---

## Use Cases & User Personas

### Primary Use Cases

#### 1. **Remote Teams & DAOs**
**Persona:** Sarah, DAO contributor working from home
- **Problem:** No accountability, easy to slack off, DAO wastes money on inactive contributors
- **Solution:** Sarah locks her monthly stipend, proves work daily via Loggerheads tracking
- **Benefit:** DAO only pays for real work, Sarah earns trust + full payment

**Example:**
- DAO budget: $5,000/month for Sarah
- Sarah deposits $5,000 USDC at month start
- Works 20/22 days productively
- Earns: $4,545 (unlocked)
- Lost: $455 (returned to DAO treasury)

#### 2. **Freelancers with Self-Discipline Issues**
**Persona:** Mike, freelance developer struggling with procrastination
- **Problem:** Inconsistent work habits, misses deadlines, loses clients
- **Solution:** Mike uses WorkChain for self-accountability (employer = himself)
- **Benefit:** Financial stakes force consistent habits, builds portfolio

**Example:**
- Mike sets personal "salary" of $6,000/month
- Threshold: 6 hours coding/day
- Lost funds → donated to charity (motivates him)
- After 3 months: builds consistent work rhythm

#### 3. **Companies with Hybrid/Remote Workforce**
**Persona:** TechCorp, 50-person startup with trust issues in remote work
- **Problem:** Can't verify remote employees actually working 8 hours
- **Solution:** Optional WorkChain program for remote workers (incentivized)
- **Benefit:** Transparent productivity, performance-based pay unlocks

**Example:**
- TechCorp offers 10% salary bonus for WorkChain participation
- Employees opt-in voluntarily
- Company sees productivity data (AI summaries, not raw screenshots)
- High performers unlock bonus; low performers see before firing

#### 4. **Bootcamps & Education Programs**
**Persona:** Web3 Academy, training developers
- **Problem:** Students pay upfront, lose motivation halfway through
- **Solution:** Students lock "commitment deposit," unlock via daily learning
- **Benefit:** Higher completion rates, proved dedication to employers

**Example:**
- Student pays $2,000 course fee
- Locked in WorkChain, unlocked daily via:
  - Completing assignments
  - Attending sessions
  - Building projects
- Graduate with proof of consistent effort (on-chain)

#### 5. **Gig Economy Workers**
**Persona:** Delivery drivers, virtual assistants, content creators
- **Problem:** Unpredictable income, no motivation structure
- **Solution:** Lock weekly earnings goal, unlock via daily work
- **Benefit:** Consistent income, gamified work

---

### User Roles

1. **Admin/Employer**
   - Creates salary vault
   - Deposits funds
   - Sets thresholds & rules
   - Chooses redistribution policy
   - Views aggregated analytics

2. **Employee/Worker**
   - Receives locked salary
   - Installs Loggerheads tracker
   - Works daily to meet threshold
   - Withdraws unlocked funds
   - Can dispute AI verification

3. **Oracle (Backend System)**
   - Monitors Loggerheads data
   - Submits daily work proofs to chain
   - Handles verification logic
   - Manages dispute resolution

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER LAYER                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Employee Device                    Admin Dashboard          │
│  ┌─────────────────┐              ┌──────────────────┐      │
│  │  Loggerheads    │              │  React Frontend  │      │
│  │  (Python CLI)   │              │  (Employer View) │      │
│  │  - Tracking     │              │  - Create Vaults │      │
│  │  - Screenshots  │              │  - View Analytics│      │
│  │  - AI Summary   │              │  - Manage Policy │      │
│  └────────┬────────┘              └────────┬─────────┘      │
│           │                                │                 │
└───────────┼────────────────────────────────┼─────────────────┘
            │                                │
            │      ┌─────────────────────────┤
            │      │                         │
┌───────────▼──────▼─────────────────────────▼─────────────────┐
│                    BACKEND LAYER (Python)                     │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI Server                          │   │
│  │  - REST API endpoints                                │   │
│  │  - WebSocket (real-time updates)                     │   │
│  │  - Authentication (JWT)                              │   │
│  └──────────┬───────────────────────────┬─────────────┬─┘   │
│             │                           │             │     │
│  ┌──────────▼──────┐     ┌──────────────▼─┐  ┌───────▼────┐│
│  │  Oracle Service │     │  Work Analyzer │  │  Database  ││
│  │  - Daily cron   │     │  - AI Summary  │  │  SQLite    ││
│  │  - Submit proofs│     │  - Hour calc   │  │  - Logs    ││
│  │  - Solana txs   │     │  - Hash proofs │  │  - Proofs  ││
│  └──────────┬──────┘     └────────────────┘  └────────────┘│
│             │                                                │
└─────────────┼────────────────────────────────────────────────┘
              │
              │  Solana Transactions
              │  (via @solana/web3.js or solders)
              │
┌─────────────▼──────────────────────────────────────────────┐
│                  BLOCKCHAIN LAYER (Solana)                 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────┐ │
│  │  Salary Vault   │  │  Work Verifier   │  │ Treasury │ │
│  │  Program        │  │  Program         │  │ Program  │ │
│  │  (Anchor)       │  │  (Anchor)        │  │ (Anchor) │ │
│  │                 │  │                  │  │          │ │
│  │ - Lock funds    │  │ - Verify proofs  │  │ - Collect│ │
│  │ - Daily unlock  │  │ - Calc threshold │  │ - Distrib│ │
│  │ - Withdraw      │  │ - Trigger unlock │  │ - Charity│ │
│  └─────────────────┘  └──────────────────┘  └──────────┘ │
│                                                            │
│  SPL Token Program (USDC)                                  │
│                                                            │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                   STORAGE LAYER                            │
├────────────────────────────────────────────────────────────┤
│  - SQLite (local work logs)                                │
│  - Solana (on-chain proofs, balances)                      │
│  - IPFS/Arweave (optional: encrypted summaries)            │
└────────────────────────────────────────────────────────────┘
```

---

## Smart Contract Design

### Program Architecture (Anchor Framework)

We'll build 3 Solana programs using Anchor:

#### **Program 1: Salary Vault**

**Purpose:** Lock and manage salary funds for each employee

**Accounts:**

```rust
#[account]
pub struct EmployeeVault {
    pub owner: Pubkey,                  // Employee wallet
    pub admin: Pubkey,                  // Employer/admin wallet
    pub total_locked: u64,              // Total USDC locked (in lamports)
    pub unlocked_balance: u64,          // Available to withdraw
    pub daily_unlock_amount: u64,       // Per successful day
    pub threshold_hours: u8,            // Required hours/day (e.g., 6)
    pub work_days_per_month: u8,        // Expected days (e.g., 22)
    pub current_period_start: i64,      // Unix timestamp
    pub current_period_end: i64,        // Unix timestamp
    pub days_achieved: u16,             // Days threshold met
    pub days_missed: u16,               // Days threshold missed
    pub redistribution_mode: u8,        // 0=burn, 1=return, 2=charity, 3=bonus
    pub charity_address: Option<Pubkey>,// If mode=2
    pub paused: bool,                   // Emergency pause
    pub bump: u8,                       // PDA bump
}

#[account]
pub struct DailyRecord {
    pub vault: Pubkey,                  // Parent vault
    pub date: i64,                      // Unix timestamp (day)
    pub hours_worked: u8,               // Hours tracked
    pub threshold_met: bool,            // Passed?
    pub amount_unlocked: u64,           // USDC unlocked
    pub proof_hash: [u8; 32],           // Work proof hash
    pub verified_at: i64,               // Verification timestamp
    pub disputed: bool,                 // Employee disputed?
    pub bump: u8,
}
```

**Instructions:**

```rust
// Admin creates vault and deposits salary
pub fn initialize_vault(
    ctx: Context<InitializeVault>,
    total_amount: u64,
    daily_unlock: u64,
    threshold_hours: u8,
    work_days: u8,
    period_start: i64,
    period_end: i64,
    redistribution_mode: u8,
) -> Result<()>

// Employee withdraws unlocked funds
pub fn withdraw(
    ctx: Context<Withdraw>,
    amount: u64,
) -> Result<()>

// Admin can pause in emergency
pub fn pause_vault(
    ctx: Context<PauseVault>,
) -> Result<()>

// Month-end: redistribute unearned funds
pub fn finalize_period(
    ctx: Context<FinalizePeriod>,
) -> Result<()>
```

---

#### **Program 2: Work Verifier**

**Purpose:** Receive and verify daily work proofs from oracle

**Accounts:**

```rust
#[account]
pub struct OracleConfig {
    pub authority: Pubkey,              // Oracle wallet (backend)
    pub vault_program: Pubkey,          // Vault program ID
    pub active: bool,
    pub bump: u8,
}

#[account]
pub struct WorkProof {
    pub vault: Pubkey,                  // Employee vault
    pub submitter: Pubkey,              // Oracle that submitted
    pub date: i64,                      // Day of work
    pub hours_worked: u8,               // Calculated hours
    pub proof_hash: [u8; 32],           // SHA256 of work summary
    pub verified: bool,
    pub disputed: bool,
    pub dispute_reason: String,         // If employee disputes
    pub submitted_at: i64,
    pub bump: u8,
}
```

**Instructions:**

```rust
// Oracle submits daily work proof
pub fn submit_work_proof(
    ctx: Context<SubmitWorkProof>,
    date: i64,
    hours_worked: u8,
    proof_hash: [u8; 32],
) -> Result<()>

// Verify proof and trigger unlock in vault
pub fn verify_and_unlock(
    ctx: Context<VerifyAndUnlock>,
    proof_account: Pubkey,
) -> Result<()>

// Employee disputes AI verification
pub fn dispute_verification(
    ctx: Context<DisputeVerification>,
    proof_account: Pubkey,
    reason: String,
) -> Result<()>

// Admin reviews and resolves dispute
pub fn resolve_dispute(
    ctx: Context<ResolveDispute>,
    proof_account: Pubkey,
    approved: bool,
) -> Result<()>
```

---

#### **Program 3: Treasury Manager**

**Purpose:** Handle unearned funds redistribution

**Accounts:**

```rust
#[account]
pub struct Treasury {
    pub authority: Pubkey,              // Admin
    pub total_collected: u64,           // Total forfeited funds
    pub charity_sent: u64,              // Donated amount
    pub returned_to_admins: u64,        // Returned to employers
    pub burned: u64,                    // Burned amount
    pub bump: u8,
}

#[account]
pub struct CharityPartner {
    pub address: Pubkey,                // Charity wallet
    pub name: String,                   // Name
    pub verified: bool,                 // KYC'd
    pub total_received: u64,
    pub bump: u8,
}
```

**Instructions:**

```rust
// Collect unearned funds from vault
pub fn collect_unearned(
    ctx: Context<CollectUnearned>,
    vault: Pubkey,
) -> Result<()>

// Redistribute based on policy
pub fn redistribute(
    ctx: Context<Redistribute>,
    mode: u8,
    amount: u64,
) -> Result<()>

// Register charity partner
pub fn add_charity(
    ctx: Context<AddCharity>,
    charity_address: Pubkey,
    name: String,
) -> Result<()>
```

---

### Smart Contract Logic Flow

```
Day 1, 9:00 AM:
┌──────────────────────────────────────────────────┐
│ Admin calls: initialize_vault()                  │
│ - Deposits 3,000 USDC                            │
│ - Sets threshold: 6 hours/day                    │
│ - Sets daily unlock: 150 USDC                    │
│ - Period: Oct 1 - Oct 31                         │
└──────────────────────────────────────────────────┘
                    │
                    ▼
       ┌────────────────────────┐
       │  Vault PDA Created     │
       │  Status: Active        │
       │  Locked: 3,000 USDC    │
       │  Unlocked: 0 USDC      │
       └────────────────────────┘

Day 1, 4:30 PM:
┌──────────────────────────────────────────────────┐
│ Oracle calls: submit_work_proof()                │
│ - Date: Oct 1                                    │
│ - Hours: 7 hours                                 │
│ - Proof hash: 0xabc123...                        │
└──────────────────────────────────────────────────┘
                    │
                    ▼
       ┌────────────────────────┐
       │  Work Proof Created    │
       │  Verified: Pending     │
       └────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│ verify_and_unlock() (CPI to Vault)               │
│ - Check: 7 hours >= 6 hours? YES                 │
│ - Action: Unlock 150 USDC                        │
│ - Update vault.unlocked_balance += 150           │
└──────────────────────────────────────────────────┘
                    │
                    ▼
       ┌────────────────────────┐
       │  Vault Updated         │
       │  Locked: 2,850 USDC    │
       │  Unlocked: 150 USDC    │
       │  Days Achieved: 1      │
       └────────────────────────┘

Day 1, 5:00 PM:
┌──────────────────────────────────────────────────┐
│ Employee calls: withdraw()                        │
│ - Amount: 150 USDC                               │
└──────────────────────────────────────────────────┘
                    │
                    ▼
       ┌────────────────────────┐
       │  Transfer to Wallet    │
       │  Vault Unlocked: 0     │
       └────────────────────────┘

Day 2, 4:30 PM (bad day):
┌──────────────────────────────────────────────────┐
│ Oracle calls: submit_work_proof()                │
│ - Date: Oct 2                                    │
│ - Hours: 4 hours                                 │
│ - Proof hash: 0xdef456...                        │
└──────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│ verify_and_unlock()                              │
│ - Check: 4 hours >= 6 hours? NO                  │
│ - Action: No unlock                              │
│ - Update vault.days_missed += 1                  │
└──────────────────────────────────────────────────┘
                    │
                    ▼
       ┌────────────────────────┐
       │  Vault Unchanged       │
       │  Locked: 2,850 USDC    │
       │  Unlocked: 0 USDC      │
       │  Days Missed: 1        │
       └────────────────────────┘

Oct 31, 11:59 PM:
┌──────────────────────────────────────────────────┐
│ Admin calls: finalize_period()                    │
│ - Calculate unearned: days_missed * daily_unlock │
│ - Transfer unearned to Treasury                  │
└──────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│ Treasury calls: redistribute()                    │
│ - Mode: 1 (return to admin)                     │
│ - Amount: 150 USDC                               │
│ - Transfer to admin wallet                       │
└──────────────────────────────────────────────────┘
```

---

## Backend Architecture

### Python Backend (FastAPI)

**Why FastAPI?**
- Fast, async Python framework
- Auto-generated API docs (Swagger)
- Easy integration with existing Loggerheads codebase
- WebSocket support for real-time updates

### Architecture

```
loggerheads/
├── __init__.py
├── config.py                    # Existing config
├── activity_tracker.py          # Existing tracker
├── database.py                  # Enhanced with new tables
├── ai_summarizer.py             # Existing AI logic
│
├── api/                         # NEW: FastAPI server
│   ├── __init__.py
│   ├── server.py                # FastAPI app
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py            # Health checks
│   │   ├── work.py              # Work data endpoints
│   │   ├── vault.py             # Vault info endpoints
│   │   └── admin.py             # Admin endpoints
│   ├── models.py                # Pydantic models
│   ├── auth.py                  # JWT authentication
│   └── websocket.py             # Real-time updates
│
├── blockchain/                  # NEW: Solana integration
│   ├── __init__.py
│   ├── client.py                # Solana connection
│   ├── wallet.py                # Wallet management
│   ├── transactions.py          # Build & send txs
│   ├── vault_interface.py       # Interact with Vault program
│   ├── verifier_interface.py    # Interact with Verifier program
│   └── proof_generator.py       # Hash work summaries
│
├── oracle/                      # NEW: Oracle service
│   ├── __init__.py
│   ├── scheduler.py             # Cron jobs
│   ├── work_calculator.py       # Calculate hours worked
│   ├── proof_submitter.py       # Submit to chain
│   └── dispute_handler.py       # Handle disputes
│
└── cli.py                       # Enhanced CLI
```

### Database Schema (SQLite - Enhanced)

```sql
-- Existing tables: logs, screenshots

-- New table: work_proofs
CREATE TABLE work_proofs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_wallet TEXT NOT NULL,
    date DATE NOT NULL,
    hours_worked REAL NOT NULL,
    proof_hash TEXT NOT NULL,        -- SHA256 hex
    summary_text TEXT,               -- AI-generated summary
    submitted_to_chain BOOLEAN DEFAULT 0,
    tx_signature TEXT,               -- Solana tx
    verified BOOLEAN DEFAULT 0,
    disputed BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_wallet, date)
);

-- New table: vaults
CREATE TABLE vaults (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vault_pubkey TEXT UNIQUE NOT NULL,
    owner_wallet TEXT NOT NULL,
    admin_wallet TEXT NOT NULL,
    total_locked REAL NOT NULL,
    daily_unlock REAL NOT NULL,
    threshold_hours INTEGER NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    status TEXT DEFAULT 'active',    -- active, finalized, paused
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- New table: daily_records
CREATE TABLE daily_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vault_id INTEGER NOT NULL,
    date DATE NOT NULL,
    hours_worked REAL NOT NULL,
    threshold_met BOOLEAN NOT NULL,
    amount_unlocked REAL NOT NULL,
    proof_pubkey TEXT,
    tx_signature TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vault_id) REFERENCES vaults(id),
    UNIQUE(vault_id, date)
);

-- New table: disputes
CREATE TABLE disputes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proof_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    status TEXT DEFAULT 'pending',   -- pending, approved, rejected
    resolved_at DATETIME,
    resolver_wallet TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proof_id) REFERENCES work_proofs(id)
);
```

### API Endpoints

```python
# Health & Status
GET  /health                    # Server health
GET  /status/solana             # Solana connection status

# Work Data (Employee)
GET  /work/today                # Today's work summary
GET  /work/history?from=X&to=Y  # Historical data
POST /work/manual-entry         # Manual hours (if tracker fails)
GET  /work/proofs               # View submitted proofs

# Vault Info
GET  /vault/:wallet             # Vault details for user
GET  /vault/:wallet/balance     # Locked/unlocked balance
GET  /vault/:wallet/history     # Daily unlock history
POST /vault/:wallet/withdraw    # Request withdrawal

# Admin
POST /admin/vault/create        # Initialize new vault
GET  /admin/vaults              # List all vaults
POST /admin/vault/:id/finalize  # End period, redistribute
GET  /admin/analytics           # Aggregated stats
POST /admin/dispute/resolve     # Resolve employee dispute

# Oracle (Internal)
POST /oracle/submit-proof       # Called by cron
GET  /oracle/pending-proofs     # Proofs awaiting submission

# WebSocket
WS   /ws/work                   # Real-time work tracking
WS   /ws/vault/:wallet          # Real-time vault updates
```

---

### Work Calculation Logic

**How to calculate "hours worked"?**

Loggerheads currently tracks screenshots every 10 seconds and uses AI to categorize as work/non-work.

**Algorithm:**

```python
def calculate_productive_hours(screenshots_data, ai_summaries, user_context):
    """
    Calculate productive hours from a day's tracking data.

    Args:
        screenshots_data: List of (timestamp, screenshot_path)
        ai_summaries: AI-categorized work summaries
        user_context: User's work definition (from ~/.loggerheads_context.json)

    Returns:
        float: Hours of productive work
    """

    # Step 1: Categorize each screenshot
    work_intervals = []

    for screenshot in screenshots_data:
        timestamp = screenshot['timestamp']
        ocr_text = screenshot['extracted_text']

        # Check if this screenshot shows work
        is_work = categorize_activity(ocr_text, user_context)

        if is_work:
            work_intervals.append(timestamp)

    # Step 2: Consolidate into continuous work blocks
    work_blocks = []
    current_block_start = None

    for i, ts in enumerate(sorted(work_intervals)):
        if current_block_start is None:
            current_block_start = ts

        # If gap > 5 minutes, end current block
        if i < len(work_intervals) - 1:
            next_ts = work_intervals[i + 1]
            if (next_ts - ts).seconds > 300:  # 5 min gap
                work_blocks.append({
                    'start': current_block_start,
                    'end': ts,
                    'duration': (ts - current_block_start).seconds / 3600
                })
                current_block_start = None

    # Step 3: Sum up work blocks
    total_hours = sum(block['duration'] for block in work_blocks)

    # Step 4: Apply pauses (user pressed 'P')
    # Subtract paused periods from total
    paused_intervals = get_paused_intervals()  # From database
    for pause in paused_intervals:
        overlap = calculate_overlap(work_blocks, pause)
        total_hours -= overlap

    return round(total_hours, 2)


def categorize_activity(ocr_text, user_context):
    """
    Determine if activity is work-related.
    Uses existing Loggerheads AI logic.
    """
    # Use ai_summarizer.py logic
    # Check against user's work keywords, apps, etc.
    # Return True if work, False otherwise
    pass
```

**Example Calculation:**

```
Day's Activity:
9:00 AM - 10:30 AM: Coding in VSCode (90 min)
10:30 AM - 11:00 AM: Coffee break (30 min) [PAUSED]
11:00 AM - 12:30 PM: Code review on GitHub (90 min)
12:30 PM - 1:30 PM: Lunch (60 min) [PAUSED]
1:30 PM - 3:00 PM: Documentation (90 min)
3:00 PM - 3:30 PM: Twitter (30 min) [NOT WORK]
3:30 PM - 4:30 PM: Bug fixing (60 min)

Total Work: 90 + 90 + 90 + 60 = 330 min = 5.5 hours
Threshold: 6 hours
Result: FAIL (0.5 hours short)
```

---

### Oracle Service

**Cron Job Schedule:**

```python
# loggerheads/oracle/scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Submit daily proof at 4:30 PM
@scheduler.scheduled_job('cron', hour=16, minute=30, day_of_week='mon-fri')
async def submit_daily_proof():
    """
    Called every weekday at 4:30 PM.
    Aggregates day's work, generates proof, submits to Solana.
    """
    logger.info("⏰ Daily proof submission triggered")

    # 1. Get today's data from database
    today = datetime.now().date()
    screenshots = get_screenshots_for_date(today)

    if not screenshots:
        logger.warning("No screenshots today, skipping")
        return

    # 2. Generate AI summary (existing logic)
    ai_summary = summarize_work_with_ai(screenshots)

    # 3. Calculate hours worked
    hours = calculate_productive_hours(screenshots, ai_summary)

    # 4. Create cryptographic proof
    proof_hash = hash_work_proof(ai_summary, hours, today)

    # 5. Save to database
    proof_record = save_work_proof(
        date=today,
        hours=hours,
        proof_hash=proof_hash,
        summary=ai_summary
    )

    # 6. Submit to Solana
    try:
        tx_signature = await submit_proof_to_chain(
            date=today,
            hours=hours,
            proof_hash=proof_hash
        )

        # Update record with tx signature
        update_proof_record(proof_record.id, tx_signature, submitted=True)

        logger.info(f"✅ Proof submitted: {tx_signature}")

        # 7. Send notification (Discord, etc.)
        await notify_user(hours, tx_signature, ai_summary)

    except Exception as e:
        logger.error(f"❌ Failed to submit proof: {e}")
        # Retry logic here


def hash_work_proof(summary: dict, hours: float, date: date) -> str:
    """
    Create SHA256 hash of work proof.
    This hash is submitted on-chain for verification.
    """
    import hashlib
    import json

    proof_data = {
        'date': date.isoformat(),
        'hours': hours,
        'summary': summary,
        'version': '1.0'
    }

    # Canonical JSON for consistent hashing
    canonical = json.dumps(proof_data, sort_keys=True)
    hash_bytes = hashlib.sha256(canonical.encode()).digest()

    return hash_bytes.hex()
```

---

## Frontend Architecture

### Tech Stack

- **Framework:** React 18 + TypeScript
- **Wallet:** Solana Wallet Adapter
- **Solana Client:** @solana/web3.js + Anchor client
- **Styling:** TailwindCSS + shadcn/ui components
- **State:** Zustand (lightweight state management)
- **Charts:** Recharts
- **Real-time:** Socket.io-client (WebSocket)

### App Structure

```
workchain-frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx          # Wallet connect, nav
│   │   │   ├── Sidebar.tsx         # Navigation
│   │   │   └── Footer.tsx
│   │   ├── vault/
│   │   │   ├── VaultCard.tsx       # Balance display
│   │   │   ├── DailyProgress.tsx   # Hours tracked today
│   │   │   ├── WithdrawModal.tsx   # Withdrawal UI
│   │   │   └── HistoryTable.tsx    # Past days
│   │   ├── admin/
│   │   │   ├── CreateVault.tsx     # Initialize vault
│   │   │   ├── VaultList.tsx       # All vaults
│   │   │   └── Analytics.tsx       # Charts
│   │   └── shared/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       └── LoadingSpinner.tsx
│   ├── hooks/
│   │   ├── useWallet.ts            # Wallet state
│   │   ├── useVault.ts             # Vault data fetching
│   │   ├── useWorkData.ts          # Work tracking data
│   │   └── useSolanaProgram.ts     # Program interactions
│   ├── lib/
│   │   ├── solana.ts               # Solana connection
│   │   ├── anchor.ts               # Anchor program setup
│   │   ├── api.ts                  # Backend API calls
│   │   └── constants.ts            # Program IDs, etc.
│   ├── pages/
│   │   ├── Dashboard.tsx           # Employee main view
│   │   ├── AdminDashboard.tsx      # Employer view
│   │   ├── VaultDetails.tsx        # Single vault view
│   │   └── Settings.tsx            # Configuration
│   ├── store/
│   │   ├── vaultStore.ts           # Vault state
│   │   └── workStore.ts            # Work tracking state
│   ├── types/
│   │   ├── vault.ts                # TypeScript types
│   │   └── work.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

### Key Screens (Wireframes)

#### **Employee Dashboard**

```
┌────────────────────────────────────────────────────────────┐
│  WorkChain                    [Connect Wallet] [@user123]  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Today's Progress                       Oct 11, 2025      │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  ⏱️ 5.2 hours worked                                  │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░  86%       │ │
│  │                                                        │ │
│  │  Threshold: 6 hours      0.8 hours remaining          │ │
│  │  Status: 🟡 In Progress                               │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Vault Balance                                             │
│  ┌─────────────────────────┐  ┌─────────────────────────┐│
│  │ 🔒 Locked                │  │ ✅ Unlocked             ││
│  │ $2,700 USDC              │  │ $150 USDC               ││
│  │                          │  │ [Withdraw]              ││
│  └─────────────────────────┘  └─────────────────────────┘│
│                                                            │
│  This Month                                                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Days Achieved: 9 / 22         Days Missed: 2         │ │
│  │                                                        │ │
│  │  [Calendar View]                                       │ │
│  │   S  M  T  W  T  F  S                                  │ │
│  │      ✅ ✅ ❌ ✅ ✅ ✅                                      │ │
│  │   ✅ ✅ ❌ ✅                                             │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Recent Activity                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Oct 10  7.2h  ✅ Unlocked $150  [View Summary]        │ │
│  │ Oct 9   8.1h  ✅ Unlocked $150  [View Summary]        │ │
│  │ Oct 8   4.5h  ❌ No unlock      [Dispute]             │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

#### **Admin Dashboard**

```
┌────────────────────────────────────────────────────────────┐
│  WorkChain Admin                      [@employer_wallet]   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Overview                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│  │ Total Vaults│ │ Active Users│ │ Avg Success │         │
│  │     12      │ │      8      │ │    82%      │         │
│  └─────────────┘ └─────────────┘ └─────────────┘         │
│                                                            │
│  Active Vaults                           [+ Create Vault]  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Employee       Status    This Month    Unlocked       │ │
│  │ alice.sol      Active    18/22 days    $2,454        ││
│  │ bob.sol        Active    15/22 days    $2,045        ││
│  │ charlie.sol    Paused    12/22 days    $1,636        ││
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Unearned Funds (This Month)                               │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Total Forfeited: $865 USDC                           │ │
│  │  Redistribution Mode: Return to Treasury              │ │
│  │  [Change Policy]                                       │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Integration: Python Backend ↔ React Frontend

**How they connect:**

```
┌───────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                         │
│                                                           │
│  React App (localhost:5173 in dev)                        │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 1. User connects Phantom wallet                     │ │
│  │ 2. React calls: GET /vault/{wallet} (FastAPI)       │ │
│  │ 3. React calls: Anchor program (directly to Solana) │ │
│  │ 4. React subscribes: WS /ws/work (real-time)        │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────┬───────────────────────────────────┘
                        │
                        │ HTTP REST + WebSocket
                        │
┌───────────────────────▼───────────────────────────────────┐
│               PYTHON BACKEND (FastAPI)                    │
│               Running on localhost:8000                   │
│                                                           │
│  Responsibilities:                                        │
│  - Serve work data (from SQLite)                          │
│  - Provide AI summaries                                   │
│  - Handle authentication                                  │
│  - WebSocket for real-time tracking updates              │
│                                                           │
│  Does NOT:                                                │
│  - Execute Solana transactions (frontend does this)       │
│  - Hold user private keys                                 │
└───────────────────────┬───────────────────────────────────┘
                        │
                        │ Reads/Writes
                        │
┌───────────────────────▼───────────────────────────────────┐
│                  SQLite Database                          │
│  - Work logs                                              │
│  - Screenshots metadata                                   │
│  - AI summaries                                           │
│  - Work proofs (for auditing)                             │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│                   SOLANA BLOCKCHAIN                       │
│                                                           │
│  Frontend reads/writes here directly:                     │
│  - Query vault balances                                   │
│  - Submit withdrawals (signed by user wallet)             │
│  - View transaction history                               │
│                                                           │
│  Oracle (backend) writes here:                            │
│  - Submit daily work proofs (signed by oracle wallet)     │
│  - Trigger unlocks                                        │
└───────────────────────────────────────────────────────────┘
```

**Communication Pattern:**

1. **Frontend → Backend (REST API):**
   - Fetch work data: `GET /work/today`
   - Fetch AI summaries: `GET /work/history`
   - Fetch vault metadata: `GET /vault/:wallet` (cached from chain)

2. **Frontend → Solana (Direct RPC):**
   - Read vault balance: `program.account.employeeVault.fetch(vaultPDA)`
   - Submit withdrawal: User signs tx in browser, sent to chain
   - Read transaction history: Query Solana RPC

3. **Backend → Solana (Oracle):**
   - Submit work proofs: Cron job signs tx with oracle wallet
   - Trigger unlocks: CPI calls from Verifier to Vault program

4. **Real-time Updates (WebSocket):**
   - Frontend subscribes: `ws://localhost:8000/ws/work`
   - Backend pushes updates when:
     - New screenshot captured
     - Work hours updated
     - Proof submitted to chain

**Example API Call from React:**

```typescript
// src/hooks/useWorkData.ts

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useWorkData() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['work', 'today'],
    queryFn: async () => {
      const response = await api.get('/work/today');
      return response.data;
    },
    refetchInterval: 30000, // Poll every 30s
  });

  return { workData: data, isLoading, error };
}
```

**Example Solana Program Call from React:**

```typescript
// src/hooks/useVault.ts

import { useAnchorWallet, useConnection } from '@solana/wallet-adapter-react';
import { Program } from '@coral-xyz/anchor';
import { useQuery } from '@tanstack/react-query';
import { getVaultPDA } from '@/lib/solana';
import { IDL, SalaryVault } from '@/lib/idl/salary_vault';

export function useVault() {
  const wallet = useAnchorWallet();
  const { connection } = useConnection();

  const { data: vaultData } = useQuery({
    queryKey: ['vault', wallet?.publicKey.toString()],
    queryFn: async () => {
      if (!wallet) return null;

      const program = new Program<SalaryVault>(
        IDL,
        connection,
        wallet
      );

      const [vaultPDA] = getVaultPDA(wallet.publicKey);
      const vaultAccount = await program.account.employeeVault.fetch(vaultPDA);

      return {
        locked: vaultAccount.totalLocked / 1e6, // Convert lamports
        unlocked: vaultAccount.unlockedBalance / 1e6,
        daysAchieved: vaultAccount.daysAchieved,
        daysMissed: vaultAccount.daysMissed,
      };
    },
    enabled: !!wallet,
    refetchInterval: 10000, // Poll every 10s
  });

  return { vault: vaultData };
}
```

---

## Verification & Dispute System

### AI-Only Verification (MVP)

**Default Flow:**

1. Loggerheads tracks activity all day
2. At 4:30 PM: AI summarizes work
3. Backend calculates hours from screenshots/AI analysis
4. Oracle submits to chain: "User worked X hours"
5. Smart contract auto-approves if X >= threshold

**Trust Model:**
- User trusts their own AI (running locally via Ollama)
- Employer trusts the on-chain proof hash
- Proof hash = cryptographic fingerprint of work summary
- Cannot be faked without changing summary (which employee would see)

### Dispute Mechanism

**When employee disagrees with AI:**

```
Scenario: AI says 5.5 hours, but employee believes they worked 7 hours

Step 1: Employee clicks "Dispute" on that day's record
Step 2: Frontend calls: POST /work/dispute
        Body: { date: "2025-10-11", reason: "AI missed 1.5h of deep work in terminal" }

Step 3: Backend creates dispute record in database
Step 4: Backend calls Solana: dispute_verification()
        This pauses the forfeiture of that day's funds

Step 5: Admin reviews dispute:
        - Views original AI summary
        - Checks screenshot samples (if admin wants)
        - Makes decision

Step 6: Admin resolves:
        A) Approve: resolve_dispute(approved=true)
           → Unlocks the $150 retroactively
        B) Reject: resolve_dispute(approved=false)
           → Funds stay locked, moved to unearned

Step 7: Employee notified via Discord/email
```

**Smart Contract Implementation:**

```rust
// In verifier program

pub fn dispute_verification(
    ctx: Context<DisputeVerification>,
    proof_account: Pubkey,
    reason: String,
) -> Result<()> {
    let proof = &mut ctx.accounts.work_proof;

    require!(!proof.disputed, ErrorCode::AlreadyDisputed);
    require!(proof.verified, ErrorCode::NotYetVerified);

    proof.disputed = true;
    proof.dispute_reason = reason;

    // Emit event for backend to pick up
    emit!(DisputeEvent {
        vault: proof.vault,
        date: proof.date,
        reason: reason.clone(),
    });

    Ok(())
}

pub fn resolve_dispute(
    ctx: Context<ResolveDispute>,
    proof_account: Pubkey,
    approved: bool,
) -> Result<()> {
    let proof = &mut ctx.accounts.work_proof;
    let vault = &mut ctx.accounts.vault;

    require!(proof.disputed, ErrorCode::NotDisputed);
    require!(
        ctx.accounts.admin.key() == vault.admin,
        ErrorCode::Unauthorized
    );

    if approved {
        // Retroactively unlock funds
        vault.unlocked_balance += vault.daily_unlock_amount;
        vault.days_achieved += 1;
        if vault.days_missed > 0 {
            vault.days_missed -= 1;
        }
    }

    proof.disputed = false;
    proof.verified = approved;

    emit!(DisputeResolvedEvent {
        vault: proof.vault,
        date: proof.date,
        approved,
    });

    Ok(())
}
```

### Future: Decentralized Verification

**For post-MVP:**

- **Option 1: Random Peer Review**
  - Other WorkChain users review your summary
  - Earn tokens for accurate reviews
  - Slashed for bad reviews

- **Option 2: Decentralized Oracle Network**
  - Multiple oracles submit proofs
  - Consensus mechanism (majority vote)
  - Similar to Chainlink or Pyth

- **Option 3: Zero-Knowledge Proofs**
  - Prove work done without revealing details
  - Privacy-preserving verification
  - Advanced: requires ZK circuit development

---

## Monetization Strategy

### Revenue Models for WorkChain

#### **Option 1: Transaction Fee Model**

**How it works:**
- Charge small fee on each unlock transaction
- Example: 1% fee on unlocked funds
- User works, unlocks $150 → WorkChain takes $1.50

**Pros:**
- Direct revenue from usage
- Scales with user activity
- No upfront cost for users

**Cons:**
- Reduces employee earnings
- May discourage adoption
- Competes with Solana tx fees

**Calculation:**
- 100 active users
- Avg 20 workdays/month
- Avg $150/day unlock
- Fee: 1%
- Revenue: 100 * 20 * $150 * 0.01 = **$3,000/month**

---

#### **Option 2: Admin/Employer Subscription**

**How it works:**
- Free for employees
- Employers pay monthly per vault
- Tiered pricing:
  - Starter: $10/month for 1-5 vaults
  - Pro: $50/month for 6-25 vaults
  - Enterprise: $200/month for 26+ vaults

**Pros:**
- No impact on employee earnings
- Predictable recurring revenue
- Employers pay (they have budget)

**Cons:**
- Requires sales to companies
- Limits solo freelancer market

**Calculation:**
- 20 employer clients
- Avg tier: Pro ($50/month)
- Revenue: 20 * $50 = **$1,000/month**

---

#### **Option 3: Premium Features (Freemium)**

**How it works:**
- Basic WorkChain: Free forever
- Premium add-ons:
  - Advanced analytics: $5/month
  - Custom work categories: $3/month
  - Export reports: $2/month
  - Faster disputes: $5/month
  - API access: $10/month

**Pros:**
- Low barrier to entry
- Users pay for what they value
- Multiple revenue streams

**Cons:**
- Requires building premium features
- Conversion rate uncertainty

**Calculation:**
- 500 free users
- 50 convert to premium (10%)
- Avg premium spend: $8/month
- Revenue: 50 * $8 = **$400/month**

---

#### **Option 4: Treasury Yield Model**

**How it works:**
- Unearned funds (forfeited) go to WorkChain treasury
- Treasury stakes/invests in Solana DeFi (Marinade, Drift, etc.)
- WorkChain keeps the yield
- Principal redistributed per employer policy

**Pros:**
- No fees for users or employers
- Passive income from DeFi
- Aligns with crypto ethos

**Cons:**
- Requires significant TVL to be meaningful
- DeFi risk (smart contract bugs, depeg)
- Regulatory concerns (are we a fund?)

**Calculation:**
- $100,000 unearned funds in treasury (avg)
- 5% APY from staking
- Revenue: $100,000 * 0.05 = **$5,000/year** = **$417/month**

---

#### **Option 5: Charity Partnership Model**

**How it works:**
- Employers choose "donate to charity" mode
- WorkChain partners with charities
- Charities pay referral fee (10-20% of donations)
- Or: Charities sponsor the platform (grants)

**Pros:**
- Feel-good marketing
- Tax benefits for employers
- Grant funding from charities

**Cons:**
- Indirect revenue
- Depends on charity partnerships
- Lower margins

**Calculation:**
- $50,000 donated to charity/month
- 15% referral fee
- Revenue: $50,000 * 0.15 = **$7,500/month**

---

#### **Option 6: Data/Analytics Licensing**

**How it works:**
- Aggregate anonymous productivity data
- Sell insights to:
  - HR consulting firms
  - Productivity tool companies
  - Academic researchers
- Fully anonymized, GDPR-compliant

**Pros:**
- High-margin revenue
- Valuable unique dataset
- B2B sales

**Cons:**
- Privacy concerns
- Requires large user base
- Regulatory complexity

**Calculation:**
- 1,000 active users = sellable dataset
- Sell to 3 clients at $2,000/month each
- Revenue: **$6,000/month**

---

### Recommended Strategy for MVP

**Hybrid Model: Employer Subscription + Transaction Fees**

**Why:**
- Covers both individual and enterprise users
- Low fees won't deter users
- Subscription provides baseline revenue

**Pricing:**

- **Individuals (self-employed):**
  - Free up to $2,000 locked/month
  - 0.5% fee on unlocks
  - $10/month for premium features

- **Employers (companies/DAOs):**
  - $20/month per vault (employee)
  - Volume discount: 10+ vaults = $15/month each
  - No transaction fees (covered by subscription)

**Example Revenue (100 users):**
- 70 individuals: 70 * 20 days * $150 * 0.005 = **$1,050/month**
- 30 employer vaults: 30 * $20 = **$600/month**
- **Total: $1,650/month** ($20K/year)

**Scale Projection:**
- 1,000 users: ~$16K/month ($192K/year)
- 10,000 users: ~$160K/month ($1.92M/year)

---

## MVP Roadmap (Hackathon Timeline)

### **Week 1: Smart Contracts (Priority 1)**

**Days 1-2: Setup & Vault Program**
- [ ] Initialize Anchor workspace
- [ ] Create `salary_vault` program
- [ ] Implement `EmployeeVault` account
- [ ] Implement `initialize_vault()` instruction
- [ ] Implement `withdraw()` instruction
- [ ] Write tests for vault creation & withdrawal

**Days 3-4: Verifier Program**
- [ ] Create `work_verifier` program
- [ ] Implement `WorkProof` account
- [ ] Implement `submit_work_proof()` instruction
- [ ] Implement `verify_and_unlock()` with CPI to vault
- [ ] Write tests for proof submission & unlock

**Days 5-7: Integration & Testing**
- [ ] Implement `finalize_period()` in vault
- [ ] Create simple treasury (single account)
- [ ] Test full flow: deposit → work → unlock → withdraw
- [ ] Deploy to Solana devnet
- [ ] Document program IDs and account structures

**Deliverable:** Functional smart contracts on devnet

---

### **Week 2: Backend Integration (Priority 2)**

**Days 8-9: Solana Client**
- [ ] Create `loggerheads/blockchain/` module
- [ ] Implement Solana connection (solders or web3.py)
- [ ] Implement wallet management (keypair loading)
- [ ] Implement transaction building utilities
- [ ] Test: submit dummy proof to devnet

**Days 10-11: Oracle Service**
- [ ] Enhance database schema (work_proofs table)
- [ ] Implement `calculate_productive_hours()` logic
- [ ] Implement `hash_work_proof()` function
- [ ] Create proof submitter (call Solana from Python)
- [ ] Test: track work → calculate hours → submit to chain

**Days 12-13: FastAPI Server**
- [ ] Create basic FastAPI app
- [ ] Implement endpoints: `/work/today`, `/vault/:wallet`, `/work/history`
- [ ] Add CORS for frontend
- [ ] Add health check endpoints
- [ ] Test: API returns correct data

**Day 14: Cron Job**
- [ ] Implement scheduler (APScheduler)
- [ ] Schedule daily proof submission (4:30 PM)
- [ ] Add Discord notification on submission
- [ ] Test: manual trigger works

**Deliverable:** Backend submitting real proofs to devnet

---

### **Week 3: Frontend (Priority 3)**

**Days 15-16: Project Setup**
- [ ] Initialize React + Vite + TypeScript
- [ ] Install Solana Wallet Adapter
- [ ] Install TailwindCSS + shadcn/ui
- [ ] Create basic layout (header, sidebar)
- [ ] Implement wallet connection

**Days 17-18: Employee Dashboard**
- [ ] Create `Dashboard.tsx` page
- [ ] Implement `useVault()` hook (fetch from Solana)
- [ ] Implement `useWorkData()` hook (fetch from API)
- [ ] Build VaultCard component (locked/unlocked balance)
- [ ] Build DailyProgress component (hours worked today)
- [ ] Test: displays correct data from devnet + API

**Days 19-20: Admin Dashboard**
- [ ] Create `AdminDashboard.tsx` page
- [ ] Implement vault creation form
- [ ] Call Solana program: `initialize_vault()` from browser
- [ ] Display list of created vaults
- [ ] Test: create vault → see it on-chain

**Day 21: Polish**
- [ ] Add loading states
- [ ] Add error handling
- [ ] Add basic styling/animations
- [ ] Test end-to-end flow
- [ ] Deploy frontend (Vercel/Netlify)

**Deliverable:** Functional web app connected to devnet

---

### **Week 4: Demo Prep & Testing (Priority 4)**

**Days 22-23: Integration Testing**
- [ ] Test full user flow: create vault → track work → unlock → withdraw
- [ ] Test edge cases: no work, partial work, dispute
- [ ] Fix bugs

**Days 24-25: Demo Content**
- [ ] Record demo video (5 min)
- [ ] Create pitch deck (problem, solution, demo, traction)
- [ ] Write README with screenshots
- [ ] Deploy to mainnet-beta (if time permits) or clean devnet

**Day 26: Buffer**
- [ ] Last-minute fixes
- [ ] Practice demo
- [ ] Prepare Q&A responses

**Day 27-28: Hackathon Submission**
- [ ] Submit project
- [ ] Share on Twitter/Discord
- [ ] Gather feedback

**Deliverable:** Polished hackathon submission

---

### MVP Features (In-Scope)

✅ **Core Mechanics:**
- Lock salary in vault
- Track work with Loggerheads
- AI calculates hours worked
- Oracle submits proof to chain
- Auto-unlock if threshold met
- Manual withdrawal

✅ **Smart Contracts:**
- Salary vault (deposit, unlock, withdraw)
- Work verifier (submit proof, trigger unlock)
- Basic treasury (collect unearned funds)

✅ **Backend:**
- FastAPI server
- Solana integration
- Work calculation logic
- Daily cron job (proof submission)
- REST API for frontend

✅ **Frontend:**
- Wallet connection
- Employee dashboard (balance, progress, history)
- Admin dashboard (create vault, view analytics)
- Withdrawal UI

---

### Post-MVP Features (Out-of-Scope for Hackathon)

❌ **Not for MVP:**
- Streaks & bonuses
- NFT achievements
- Social features (leaderboards)
- Yield integration (DeFi staking)
- Advanced disputes (peer review)
- Mobile app
- Custom work categories (use existing Loggerheads logic)
- Multi-token support (USDC only for MVP)
- Advanced analytics/charts
- White-label for enterprises

---

## Technical Stack

### **Blockchain**
- **Solana:** Mainnet-beta (or devnet for testing)
- **Framework:** Anchor 0.30+
- **Language:** Rust 1.75+
- **Token:** SPL Token (USDC)
- **RPC:** Helius or QuickNode (for production)

### **Backend**
- **Language:** Python 3.11+
- **Framework:** FastAPI 0.100+
- **Solana Client:** solders (Rust-based Python bindings) OR solana-py
- **Database:** SQLite (existing Loggerheads DB)
- **Scheduler:** APScheduler 3.10+
- **AI:** Ollama (existing in Loggerheads)
- **Testing:** pytest

### **Frontend**
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Wallet:** @solana/wallet-adapter-react
- **Solana:** @solana/web3.js + @coral-xyz/anchor
- **Styling:** TailwindCSS 3.4+
- **Components:** shadcn/ui (based on Radix UI)
- **State:** Zustand
- **API Client:** Axios
- **Charts:** Recharts
- **Testing:** Vitest + React Testing Library

### **Infrastructure**
- **Hosting:**
  - Frontend: Vercel or Netlify
  - Backend: Railway or Fly.io
  - Database: Embedded SQLite (or upgrade to PostgreSQL on Railway)
- **CI/CD:** GitHub Actions
- **Monitoring:** Sentry (errors), PostHog (analytics)

---

## Security Considerations

### **Smart Contract Security**

1. **Access Control:**
   - Only admin can create/pause vaults
   - Only oracle can submit proofs
   - Only employee can withdraw & dispute

2. **Reentrancy Protection:**
   - Use Anchor's built-in reentrancy guards
   - No external calls in critical sections

3. **Overflow Protection:**
   - Rust's checked math (panics on overflow)
   - Use `checked_add`, `checked_sub`

4. **PDA Security:**
   - Derive PDAs with unique seeds (user pubkey + "vault")
   - Verify PDA ownership in every instruction

5. **Testing:**
   - Unit tests for all instructions
   - Integration tests for full flows
   - Fuzzing for edge cases

6. **Audit:**
   - Post-hackathon: hire auditor (Sec3, OtterSec)
   - Bug bounty on Immunefi

---

### **Backend Security**

1. **Oracle Wallet:**
   - Store keypair encrypted (Keystore)
   - Use environment variables for secrets
   - Rotate keys regularly

2. **API Authentication:**
   - JWT tokens for user sessions
   - Rate limiting (100 req/min per IP)
   - CORS whitelist

3. **Database:**
   - Encrypt sensitive fields (work summaries)
   - Regular backups
   - SQL injection prevention (ORM)

4. **Proof Integrity:**
   - SHA256 hashing for work proofs
   - Cannot be reverse-engineered
   - Store hash on-chain, full data off-chain

---

### **Frontend Security**

1. **Wallet Security:**
   - Never request private keys
   - Use Wallet Adapter (Phantom, Solflare, etc.)
   - Verify transaction contents before signing

2. **RPC Security:**
   - Use trusted RPC providers (Helius, Alchemy)
   - Verify program IDs before calling

3. **Data Privacy:**
   - Don't display private keys/seeds
   - Redact sensitive info in screenshots

---

### **Privacy Considerations**

1. **Work Data:**
   - Screenshots stored locally only
   - Auto-deleted after summary generation
   - AI summary hashed and stored on-chain (hash only)
   - Full summary stored in local DB (employee controls)

2. **Optional Encryption:**
   - Encrypt AI summaries with employee's public key
   - Admin sees only: hours worked, threshold met (yes/no)
   - Full summary only available to employee

3. **GDPR Compliance:**
   - Right to be forgotten: delete local DB
   - Data portability: export API
   - Transparency: user knows what's tracked

---

## Future Enhancements (Post-Hackathon)

### **Phase 2: Gamification**
- Streak tracking (7-day, 30-day)
- Bonus multipliers for consistency
- Leaderboards (opt-in)
- NFT achievement badges

### **Phase 3: Social**
- Team/DAO mode (group vaults)
- Public profiles (show streak, days achieved)
- Share achievements on Twitter
- Referral program

### **Phase 4: DeFi Integration**
- Stake unearned funds (Marinade, Drift)
- Yield credited at month-end
- Liquid staking tokens (mSOL, jitoSOL)
- Auto-compound option

### **Phase 5: Advanced Verification**
- Decentralized oracle network
- Peer review for disputes
- Zero-knowledge proofs (privacy-preserving)
- Multi-oracle consensus

### **Phase 6: Enterprise**
- White-label solution
- SSO integration
- Custom branding
- Advanced analytics dashboard
- API for HRIS integration

### **Phase 7: Mobile**
- React Native app
- iOS/Android tracking
- Push notifications
- Mobile-friendly vault management

---

## Appendix: Streamflow Comparison

| Feature | Streamflow | WorkChain |
|---------|------------|-----------|
| **Purpose** | Token vesting, salary streaming | Productivity accountability |
| **Unlock Trigger** | Time-based | Work-based (KPI) |
| **Funds Flow** | Sender → Recipient (automated) | Locked → Unlocked (conditional) |
| **Use Case** | Investor vesting, employee payroll | Remote work accountability |
| **Verification** | None (automatic) | AI + Oracle |
| **Gamification** | No | Yes (streaks, NFTs) |
| **Unique Value** | Payment automation | Loss aversion psychology |

**Inspiration Taken:**
- Conditional unlocks (Streamflow's "Aligned Unlocks")
- PDA structure for user accounts
- Cancellation/pause mechanisms

**Key Difference:**
- Streamflow: "Money flows TO you over time"
- WorkChain: "Money locked WITH you, work to keep it"

---

## Conclusion

WorkChain is a novel application of blockchain technology to solve real remote work challenges. By leveraging:

1. **Solana's speed & low fees** for daily transactions
2. **Existing Loggerheads infrastructure** for work tracking
3. **Streamflow's conditional unlock model** as inspiration
4. **Behavioral psychology** (loss aversion) for motivation

We create a system that:
- ✅ Proves productivity on-chain
- ✅ Aligns incentives between employers and employees
- ✅ Builds trust in remote work relationships
- ✅ Gamifies self-discipline

**Next Steps:**
1. Review this architecture document
2. Confirm MVP scope and timeline
3. Start with smart contract development (Week 1)
4. Build iteratively and test frequently
5. Prepare killer demo for hackathon

**Let's build this! 🚀**

---

**Document Version:** 1.0
**Last Updated:** Oct 11, 2025
**Authors:** AI Assistant (Claude) + User
**Project Status:** Pre-Development (Architecture Phase)
