# WorkChain - Technical Architecture & Implementation

**Detailed technical specification for building the reverse salary accountability system**

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Component 1: Smart Contract](#component-1-smart-contract)
3. [Component 2: Python Backend (Oracle)](#component-2-python-backend-oracle)
4. [Component 3: React Frontend](#component-3-react-frontend)
5. [Data Flow](#data-flow)
6. [Oracle System](#oracle-system)
7. [Quality Metrics Calculation](#quality-metrics-calculation)
8. [Discord Integration](#discord-integration)
9. [Dispute Resolution](#dispute-resolution)
10. [Deployment Architecture](#deployment-architecture)
11. [Implementation Timeline](#implementation-timeline)
12. [Testing Strategy](#testing-strategy)

---

## System Architecture

### High-Level Overview

WorkChain is **ONE integrated application** with three interconnected components:

```
┌─────────────────────────────────────────────────────────────┐
│                    EMPLOYEE'S MACHINE                       │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Loggerheads (Enhanced Python CLI)                    │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  Activity Tracker (existing)                    │  │ │
│  │  │  • Screenshots every 10s                        │  │ │
│  │  │  • OCR extraction                               │  │ │
│  │  │  • Window title tracking                        │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  AI Analyzer (existing)                         │  │ │
│  │  │  • Ollama LLM (llama3.2)                        │  │ │
│  │  │  • Work categorization                          │  │ │
│  │  │  • Summary generation                           │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  Oracle Module (NEW)                            │  │ │
│  │  │  • Work calculator                              │  │ │
│  │  │  • Quality scorer                               │  │ │
│  │  │  • Blockchain submitter                         │  │ │
│  │  │  • Discord poster                               │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  SQLite Database (existing + enhanced)          │  │ │
│  │  │  • Activity logs                                │  │ │
│  │  │  • Screenshots metadata                         │  │ │
│  │  │  • Work proofs                                  │  │ │
│  │  │  • Daily scores                                 │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────┘ │
│                           │                                 │
│                           │ Solana RPC Calls                │
│                           │ (Submit attestations)           │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    SOLANA BLOCKCHAIN                        │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  WorkChain Program (ONE Anchor Program)               │ │
│  │                                                        │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  Vault Management                                │ │ │
│  │  │  • EmployeeVault account (PDA)                   │ │ │
│  │  │  • initialize_vault()                            │ │ │
│  │  │  • withdraw()                                    │ │ │
│  │  │  • pause_vault()                                 │ │ │
│  │  │  • finalize_period()                             │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  Oracle Verification                             │ │ │
│  │  │  • DailyRecord account (PDA)                     │ │ │
│  │  │  • submit_daily_attestation()                    │ │ │
│  │  │  • verify_and_unlock()                           │ │ │
│  │  │  • dispute_record()                              │ │ │
│  │  │  • resolve_dispute()                             │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  Treasury                                        │ │ │
│  │  │  • Treasury account (PDA)                        │ │ │
│  │  │  • collect_unearned()                            │ │ │
│  │  │  • redistribute()                                │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Solana RPC Calls
                            │ (Read vault state, withdraw, create vault)
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                    USER'S BROWSER                           │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  React Web Dashboard                                  │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  Employee View                                  │  │ │
│  │  │  • Real-time balance display                    │  │ │
│  │  │  • Daily progress bar                           │  │ │
│  │  │  • Withdraw button                              │  │ │
│  │  │  • History calendar                             │  │ │
│  │  │  • Dispute form                                 │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  Admin View                                     │  │ │
│  │  │  • Create vault form                            │  │ │
│  │  │  • Vault list                                   │  │ │
│  │  │  • Analytics dashboard                          │  │ │
│  │  │  • Resolve disputes                             │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  Solana Wallet Adapter                          │  │ │
│  │  │  • Connect Phantom/Solflare                     │  │ │
│  │  │  • Sign transactions                            │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                        │
├─────────────────────────────────────────────────────────────┤
│  • Discord (daily summaries via webhook)                    │
│  • Helius RPC (Solana connection)                           │
│  • Ollama (local AI, runs on employee machine)              │
└─────────────────────────────────────────────────────────────┘
```

### Key Clarifications

**Q: One app or three separate apps?**
**A:** ONE product (WorkChain) with three components that talk to each other:
- Component 1 (Loggerheads) runs locally on employee's machine
- Component 2 (Smart Contract) is deployed on Solana blockchain
- Component 3 (Web Dashboard) runs in user's browser

They work together but are developed separately because they use different tech stacks.

---

## Component 1: Smart Contract

### Architecture Decision: ONE Program (Not Three)

**Why one program?**
- Simpler for MVP/hackathon
- Cheaper to deploy (one deployment fee)
- Easier to maintain
- All state in one place
- Can still organize as modules internally

**Program Structure:**

```rust
// programs/workchain/src/lib.rs

use anchor_lang::prelude::*;

declare_id!("WrkChain11111111111111111111111111111111111");

#[program]
pub mod workchain {
    use super::*;

    // ========== VAULT MANAGEMENT ==========

    pub fn initialize_vault(
        ctx: Context<InitializeVault>,
        total_amount: u64,
        daily_unlock: u64,
        threshold_config: ThresholdConfig,
        period_start: i64,
        period_end: i64,
        redistribution_mode: RedistributionMode,
    ) -> Result<()> {
        // Admin creates vault, deposits USDC
        // Vault PDA derived from: [b"vault", employee_pubkey, admin_pubkey]
    }

    pub fn withdraw(
        ctx: Context<Withdraw>,
        amount: u64,
    ) -> Result<()> {
        // Employee withdraws unlocked funds
    }

    pub fn pause_vault(
        ctx: Context<PauseVault>,
    ) -> Result<()> {
        // Admin pauses (emergency or vacation)
    }

    // ========== ORACLE & VERIFICATION ==========

    pub fn submit_daily_attestation(
        ctx: Context<SubmitAttestation>,
        date: i64,
        work_metrics: WorkMetrics,
        proof_hash: [u8; 32],
    ) -> Result<()> {
        // Oracle submits daily work proof
        // Automatically calls verify_and_unlock() internally
    }

    pub fn dispute_record(
        ctx: Context<DisputeRecord>,
        date: i64,
        reason: String,
    ) -> Result<()> {
        // Employee disputes AI assessment
    }

    pub fn resolve_dispute(
        ctx: Context<ResolveDispute>,
        date: i64,
        approved: bool,
    ) -> Result<()> {
        // Admin resolves dispute (human override)
    }

    // ========== TREASURY & REDISTRIBUTION ==========

    pub fn finalize_period(
        ctx: Context<FinalizePeriod>,
    ) -> Result<()> {
        // Month-end: collect unearned funds
    }

    pub fn redistribute_funds(
        ctx: Context<RedistributeFunds>,
    ) -> Result<()> {
        // Execute redistribution per policy
    }
}
```

---

### Account Structures

```rust
// accounts.rs

#[account]
pub struct EmployeeVault {
    pub owner: Pubkey,                  // Employee wallet
    pub admin: Pubkey,                  // Employer/admin wallet
    pub oracle: Pubkey,                 // Authorized oracle (Loggerheads backend)

    // Financial
    pub total_locked: u64,              // Total USDC locked (lamports)
    pub unlocked_balance: u64,          // Available to withdraw
    pub daily_unlock_amount: u64,       // Per successful day

    // Threshold configuration
    pub threshold_config: ThresholdConfig,

    // Period
    pub period_start: i64,              // Unix timestamp
    pub period_end: i64,                // Unix timestamp

    // Stats
    pub days_achieved: u16,             // Days threshold met
    pub days_missed: u16,               // Days threshold missed

    // Settings
    pub redistribution_mode: RedistributionMode,
    pub charity_address: Option<Pubkey>,
    pub paused: bool,

    pub bump: u8,                       // PDA bump
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy)]
pub struct ThresholdConfig {
    pub min_hours: u8,                  // Minimum hours (e.g., 6)
    pub min_quality_score: u8,          // Minimum quality 0-100 (e.g., 70)
    pub min_tasks_completed: u8,        // Minimum tasks (e.g., 3)
    pub require_all: bool,              // AND vs OR logic
}

impl ThresholdConfig {
    pub fn check_threshold(&self, metrics: &WorkMetrics) -> bool {
        if self.require_all {
            // Must meet ALL criteria
            metrics.hours_worked >= self.min_hours
                && metrics.quality_score >= self.min_quality_score
                && metrics.tasks_completed >= self.min_tasks_completed
        } else {
            // Must meet ANY criterion (OR logic)
            metrics.hours_worked >= self.min_hours
                || metrics.quality_score >= self.min_quality_score
                || metrics.tasks_completed >= self.min_tasks_completed
        }
    }
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy)]
pub struct WorkMetrics {
    pub hours_worked: u8,               // 0-24
    pub quality_score: u8,              // 0-100
    pub tasks_completed: u8,            // Count
    pub blockers_encountered: u8,       // Count (for reporting)
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq)]
pub enum RedistributionMode {
    ReturnToAdmin,                      // Send back to employer
    DonateToCharity,                    // Send to configured charity
    Burn,                               // Destroy tokens
    BonusPool,                          // Roll into next period bonus
}

#[account]
pub struct DailyRecord {
    pub vault: Pubkey,                  // Parent vault
    pub date: i64,                      // Unix timestamp (day only, not time)
    pub work_metrics: WorkMetrics,      // Submitted by oracle
    pub proof_hash: [u8; 32],           // SHA256 of full work summary
    pub threshold_met: bool,            // Did they pass?
    pub amount_unlocked: u64,           // USDC unlocked (0 if failed)
    pub submitted_at: i64,              // When oracle submitted
    pub disputed: bool,                 // Employee disputed?
    pub dispute_reason: Option<String>, // Why disputed
    pub dispute_resolved: bool,         // Admin resolved?
    pub bump: u8,
}

#[account]
pub struct Treasury {
    pub authority: Pubkey,              // Program authority
    pub total_collected: u64,           // Total unearned funds collected
    pub total_redistributed: u64,       // Total sent out
    pub bump: u8,
}
```

---

### Key Instructions (Detailed)

#### 1. `initialize_vault`

**Who calls:** Admin (employer)

**What it does:**
1. Creates EmployeeVault PDA
2. Transfers USDC from admin to vault
3. Sets all configuration (threshold, dates, etc.)

**Implementation:**

```rust
#[derive(Accounts)]
pub struct InitializeVault<'info> {
    #[account(
        init,
        payer = admin,
        space = 8 + EmployeeVault::LEN,
        seeds = [b"vault", employee.key().as_ref(), admin.key().as_ref()],
        bump
    )]
    pub vault: Account<'info, EmployeeVault>,

    #[account(mut)]
    pub admin: Signer<'info>,

    /// CHECK: Employee wallet (doesn't need to sign)
    pub employee: AccountInfo<'info>,

    /// CHECK: Oracle wallet (Loggerheads backend)
    pub oracle: AccountInfo<'info>,

    #[account(mut)]
    pub admin_token_account: Account<'info, TokenAccount>,

    #[account(mut)]
    pub vault_token_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

pub fn initialize_vault(
    ctx: Context<InitializeVault>,
    total_amount: u64,
    daily_unlock: u64,
    threshold_config: ThresholdConfig,
    period_start: i64,
    period_end: i64,
    redistribution_mode: RedistributionMode,
) -> Result<()> {
    let vault = &mut ctx.accounts.vault;

    vault.owner = ctx.accounts.employee.key();
    vault.admin = ctx.accounts.admin.key();
    vault.oracle = ctx.accounts.oracle.key();
    vault.total_locked = total_amount;
    vault.unlocked_balance = 0;
    vault.daily_unlock_amount = daily_unlock;
    vault.threshold_config = threshold_config;
    vault.period_start = period_start;
    vault.period_end = period_end;
    vault.days_achieved = 0;
    vault.days_missed = 0;
    vault.redistribution_mode = redistribution_mode;
    vault.paused = false;
    vault.bump = ctx.bumps.vault;

    // Transfer USDC from admin to vault
    let cpi_ctx = CpiContext::new(
        ctx.accounts.token_program.to_account_info(),
        Transfer {
            from: ctx.accounts.admin_token_account.to_account_info(),
            to: ctx.accounts.vault_token_account.to_account_info(),
            authority: ctx.accounts.admin.to_account_info(),
        },
    );
    token::transfer(cpi_ctx, total_amount)?;

    emit!(VaultCreatedEvent {
        vault: vault.key(),
        employee: vault.owner,
        admin: vault.admin,
        total_locked: total_amount,
    });

    Ok(())
}
```

---

#### 2. `submit_daily_attestation`

**Who calls:** Oracle (Loggerheads backend)

**What it does:**
1. Creates DailyRecord PDA
2. Stores work metrics
3. Checks if threshold met
4. If yes → calls internal function to unlock funds

**Implementation:**

```rust
#[derive(Accounts)]
#[instruction(date: i64)]
pub struct SubmitAttestation<'info> {
    #[account(
        init,
        payer = oracle,
        space = 8 + DailyRecord::LEN,
        seeds = [b"record", vault.key().as_ref(), &date.to_le_bytes()],
        bump
    )]
    pub daily_record: Account<'info, DailyRecord>,

    #[account(
        mut,
        seeds = [b"vault", vault.owner.as_ref(), vault.admin.as_ref()],
        bump = vault.bump,
        constraint = vault.oracle == oracle.key() @ ErrorCode::UnauthorizedOracle
    )]
    pub vault: Account<'info, EmployeeVault>,

    #[account(mut)]
    pub oracle: Signer<'info>,

    pub system_program: Program<'info, System>,
}

pub fn submit_daily_attestation(
    ctx: Context<SubmitAttestation>,
    date: i64,
    work_metrics: WorkMetrics,
    proof_hash: [u8; 32],
) -> Result<()> {
    let vault = &mut ctx.accounts.vault;
    let record = &mut ctx.accounts.daily_record;

    // Check if vault is active
    require!(!vault.paused, ErrorCode::VaultPaused);

    let now = Clock::get()?.unix_timestamp;
    require!(
        now >= vault.period_start && now <= vault.period_end,
        ErrorCode::OutsideActivePeriod
    );

    // Store record
    record.vault = vault.key();
    record.date = date;
    record.work_metrics = work_metrics;
    record.proof_hash = proof_hash;
    record.submitted_at = now;
    record.disputed = false;
    record.dispute_resolved = false;
    record.bump = ctx.bumps.daily_record;

    // Check threshold
    let threshold_met = vault.threshold_config.check_threshold(&work_metrics);
    record.threshold_met = threshold_met;

    if threshold_met {
        // Unlock funds
        let unlock_amount = vault.daily_unlock_amount;

        // Ensure we don't unlock more than available
        let available = vault.total_locked.checked_sub(vault.unlocked_balance)
            .ok_or(ErrorCode::InsufficientLockedFunds)?;

        let actual_unlock = std::cmp::min(unlock_amount, available);

        vault.unlocked_balance = vault.unlocked_balance
            .checked_add(actual_unlock)
            .ok_or(ErrorCode::Overflow)?;

        vault.days_achieved += 1;
        record.amount_unlocked = actual_unlock;

        emit!(FundsUnlockedEvent {
            vault: vault.key(),
            date,
            amount: actual_unlock,
            work_metrics,
        });
    } else {
        // Threshold not met, no unlock
        vault.days_missed += 1;
        record.amount_unlocked = 0;

        emit!(ThresholdMissedEvent {
            vault: vault.key(),
            date,
            work_metrics,
        });
    }

    Ok(())
}
```

---

#### 3. `withdraw`

**Who calls:** Employee

**What it does:**
1. Transfers unlocked USDC from vault to employee wallet
2. Updates vault balance

**Implementation:**

```rust
#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(
        mut,
        seeds = [b"vault", vault.owner.as_ref(), vault.admin.as_ref()],
        bump = vault.bump,
        constraint = vault.owner == employee.key() @ ErrorCode::Unauthorized
    )]
    pub vault: Account<'info, EmployeeVault>,

    #[account(mut)]
    pub employee: Signer<'info>,

    #[account(mut)]
    pub vault_token_account: Account<'info, TokenAccount>,

    #[account(mut)]
    pub employee_token_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

pub fn withdraw(
    ctx: Context<Withdraw>,
    amount: u64,
) -> Result<()> {
    let vault = &mut ctx.accounts.vault;

    require!(amount <= vault.unlocked_balance, ErrorCode::InsufficientUnlockedFunds);

    // Transfer USDC
    let vault_seeds = &[
        b"vault",
        vault.owner.as_ref(),
        vault.admin.as_ref(),
        &[vault.bump],
    ];

    let cpi_ctx = CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        Transfer {
            from: ctx.accounts.vault_token_account.to_account_info(),
            to: ctx.accounts.employee_token_account.to_account_info(),
            authority: vault.to_account_info(),
        },
        &[vault_seeds],
    );
    token::transfer(cpi_ctx, amount)?;

    // Update balance
    vault.unlocked_balance = vault.unlocked_balance
        .checked_sub(amount)
        .ok_or(ErrorCode::Underflow)?;

    emit!(WithdrawalEvent {
        vault: vault.key(),
        employee: vault.owner,
        amount,
    });

    Ok(())
}
```

---

#### 4. `dispute_record`

**Who calls:** Employee

**What it does:**
1. Marks DailyRecord as disputed
2. Prevents finalization until resolved

**Implementation:**

```rust
pub fn dispute_record(
    ctx: Context<DisputeRecord>,
    date: i64,
    reason: String,
) -> Result<()> {
    let record = &mut ctx.accounts.daily_record;
    let vault = &ctx.accounts.vault;

    require!(!record.disputed, ErrorCode::AlreadyDisputed);
    require!(!record.threshold_met, ErrorCode::CannotDisputePassedRecord);
    require!(vault.owner == ctx.accounts.employee.key(), ErrorCode::Unauthorized);

    record.disputed = true;
    record.dispute_reason = Some(reason.clone());

    emit!(DisputeFiledEvent {
        vault: vault.key(),
        date,
        reason,
    });

    Ok(())
}
```

---

#### 5. `resolve_dispute`

**Who calls:** Admin

**What it does:**
1. Reviews dispute
2. If approved → retroactively unlock funds
3. Marks as resolved

**Implementation:**

```rust
pub fn resolve_dispute(
    ctx: Context<ResolveDispute>,
    date: i64,
    approved: bool,
) -> Result<()> {
    let record = &mut ctx.accounts.daily_record;
    let vault = &mut ctx.accounts.vault;

    require!(record.disputed, ErrorCode::NotDisputed);
    require!(!record.dispute_resolved, ErrorCode::AlreadyResolved);
    require!(vault.admin == ctx.accounts.admin.key(), ErrorCode::Unauthorized);

    if approved {
        // Retroactively unlock
        let unlock_amount = vault.daily_unlock_amount;
        vault.unlocked_balance = vault.unlocked_balance
            .checked_add(unlock_amount)
            .ok_or(ErrorCode::Overflow)?;

        vault.days_achieved += 1;
        if vault.days_missed > 0 {
            vault.days_missed -= 1;
        }

        record.threshold_met = true;
        record.amount_unlocked = unlock_amount;
    }

    record.dispute_resolved = true;

    emit!(DisputeResolvedEvent {
        vault: vault.key(),
        date,
        approved,
    });

    Ok(())
}
```

---

### Error Codes

```rust
#[error_code]
pub enum ErrorCode {
    #[msg("Unauthorized oracle")]
    UnauthorizedOracle,

    #[msg("Unauthorized user")]
    Unauthorized,

    #[msg("Vault is paused")]
    VaultPaused,

    #[msg("Outside active period")]
    OutsideActivePeriod,

    #[msg("Insufficient locked funds")]
    InsufficientLockedFunds,

    #[msg("Insufficient unlocked funds")]
    InsufficientUnlockedFunds,

    #[msg("Already disputed")]
    AlreadyDisputed,

    #[msg("Not disputed")]
    NotDisputed,

    #[msg("Already resolved")]
    AlreadyResolved,

    #[msg("Cannot dispute passed record")]
    CannotDisputePassedRecord,

    #[msg("Overflow")]
    Overflow,

    #[msg("Underflow")]
    Underflow,
}
```

---

## Component 2: Python Backend (Oracle)

### Role of the Oracle

**Oracle = Loggerheads backend** (runs on employee's machine)

**Responsibilities:**
1. Track work activity all day
2. Analyze with AI at 4:30 PM
3. Calculate metrics (hours, quality, tasks)
4. Submit attestation to Solana
5. Post summary to Discord

**Key Point:** Oracle does NOT need to be a separate server. It's just Loggerheads with new blockchain functionality added.

---

### Enhanced Loggerheads Architecture

```
loggerheads/
├── __init__.py
├── config.py                    # Add oracle wallet, program IDs
├── activity_tracker.py          # Existing
├── database.py                  # Add new tables
├── ai_summarizer.py             # Existing
├── cli.py                       # Add new commands
│
├── blockchain/                  # NEW MODULE
│   ├── __init__.py
│   ├── solana_client.py         # Connection to Solana
│   ├── wallet_manager.py        # Load oracle keypair
│   ├── program_interface.py     # Call smart contract
│   └── transaction_builder.py   # Build & send transactions
│
├── oracle/                      # NEW MODULE
│   ├── __init__.py
│   ├── metrics_calculator.py    # Calculate hours, quality, tasks
│   ├── attestation_submitter.py # Submit to blockchain
│   ├── scheduler.py             # Cron job (4:30 PM daily)
│   └── proof_generator.py       # Hash summaries
│
└── integrations/                # NEW MODULE
    ├── __init__.py
    └── discord_client.py        # Enhanced Discord posting
```

---

### Metrics Calculation (Detailed)

**Question:** How do we calculate not just hours but also quality and tasks?

**Answer:** Enhanced AI analysis + heuristics

#### Algorithm: `calculate_work_metrics()`

```python
# loggerheads/oracle/metrics_calculator.py

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

@dataclass
class WorkMetrics:
    hours_worked: int        # 0-24
    quality_score: int       # 0-100
    tasks_completed: int     # Count
    blockers_encountered: int

def calculate_work_metrics(
    screenshots: List[Dict],
    ai_summary: Dict,
    user_context: Dict
) -> WorkMetrics:
    """
    Calculate comprehensive work metrics from day's data.

    Args:
        screenshots: List of screenshot metadata
        ai_summary: AI-generated summary from Ollama
        user_context: User's work definition

    Returns:
        WorkMetrics object
    """

    # 1. HOURS WORKED (existing logic)
    hours = calculate_productive_hours(screenshots, user_context)

    # 2. QUALITY SCORE (NEW)
    quality = calculate_quality_score(screenshots, ai_summary, user_context)

    # 3. TASKS COMPLETED (NEW)
    tasks = count_tasks_completed(ai_summary)

    # 4. BLOCKERS (NEW)
    blockers = count_blockers(ai_summary)

    return WorkMetrics(
        hours_worked=int(hours),
        quality_score=quality,
        tasks_completed=tasks,
        blockers_encountered=blockers
    )


def calculate_productive_hours(screenshots, user_context):
    """
    Existing logic from Loggerheads.
    Counts screenshots showing work activity, consolidates into blocks.
    """
    # (Same as before - uses existing code)
    pass


def calculate_quality_score(screenshots, ai_summary, user_context) -> int:
    """
    NEW: Calculate quality score 0-100 based on multiple factors.

    Quality Indicators:
    - Deep work sessions (long uninterrupted blocks)
    - Completed tasks (from AI summary)
    - Meaningful commits (if coding)
    - Output produced (code written, docs created)
    - Focus (not jumping between many apps)
    - Blockers resolved (problems fixed)

    Returns:
        Score 0-100
    """

    score = 50  # Base score

    # Factor 1: Deep work blocks (+20 points max)
    work_blocks = get_work_blocks(screenshots)
    long_blocks = [b for b in work_blocks if b['duration'] >= 1.5]  # 1.5+ hour blocks
    deep_work_bonus = min(20, len(long_blocks) * 5)
    score += deep_work_bonus

    # Factor 2: Tasks completed (+30 points max)
    completed_tasks = ai_summary.get('completed_tasks', [])
    if len(completed_tasks) > 0:
        # Has completed tasks section and it's not empty placeholder
        real_completions = [t for t in completed_tasks if len(t) > 20]  # Non-trivial
        task_bonus = min(30, len(real_completions) * 10)
        score += task_bonus

    # Factor 3: Code commits / tangible output (+20 points max)
    if detect_output_produced(screenshots):
        score += 20

    # Factor 4: Focus vs distraction (-10 points max penalty)
    distraction_penalty = calculate_distraction_penalty(screenshots)
    score -= distraction_penalty

    # Factor 5: Blockers resolved (+10 bonus)
    blockers = ai_summary.get('problems_blockers', [])
    if any('resolved' in b.lower() or 'fixed' in b.lower() for b in blockers):
        score += 10

    # Clamp to 0-100
    return max(0, min(100, score))


def count_tasks_completed(ai_summary: Dict) -> int:
    """
    NEW: Count actual completed tasks from AI summary.

    Looks at 'completed_tasks' section.
    Filters out placeholder text.
    """

    completed = ai_summary.get('completed_tasks', [])

    # Filter placeholders
    real_tasks = [
        t for t in completed
        if len(t) > 20  # Not too short
        and not t.lower().startswith('[')  # Not placeholder like "[List tasks...]"
        and not t.lower().startswith('no ')  # Not "No tasks completed"
    ]

    return len(real_tasks)


def count_blockers(ai_summary: Dict) -> int:
    """
    NEW: Count blockers from AI summary.
    """
    blockers = ai_summary.get('problems_blockers', [])

    real_blockers = [
        b for b in blockers
        if len(b) > 20
        and not b.lower().startswith('[')
        and not b.lower().startswith('no ')
    ]

    return len(real_blockers)


def detect_output_produced(screenshots: List[Dict]) -> bool:
    """
    Detect if tangible output was produced.

    Indicators:
    - Git commit messages in terminal
    - File save notifications
    - "Build successful" messages
    - Document export
    """

    output_keywords = [
        'git commit',
        'git push',
        'saved',
        'build successful',
        'deployed',
        'published',
        'exported',
        'PR merged',
    ]

    for screenshot in screenshots:
        text = screenshot.get('extracted_text', '').lower()
        if any(keyword in text for keyword in output_keywords):
            return True

    return False


def calculate_distraction_penalty(screenshots: List[Dict]) -> int:
    """
    Calculate penalty for distracted work (app switching, social media).

    Returns penalty 0-10 points.
    """

    # Count unique apps used
    apps = set()
    for s in screenshots:
        app_name = extract_app_name(s['window_name'])
        if app_name:
            apps.add(app_name)

    # Too many different apps = distracted
    if len(apps) > 10:
        return 10
    elif len(apps) > 7:
        return 5

    # Check for social media / entertainment
    distraction_apps = ['twitter', 'instagram', 'facebook', 'youtube', 'netflix', 'reddit']
    distraction_count = sum(
        1 for s in screenshots
        if any(app in s['window_name'].lower() for app in distraction_apps)
    )

    distraction_ratio = distraction_count / len(screenshots)

    if distraction_ratio > 0.3:  # 30%+ distraction
        return 8
    elif distraction_ratio > 0.1:
        return 4

    return 0
```

---

### Attestation Submission

**How oracle submits to Solana:**

```python
# loggerheads/oracle/attestation_submitter.py

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from anchorpy import Provider, Wallet, Program, Context
import hashlib
import json

async def submit_daily_attestation(
    employee_wallet: Pubkey,
    admin_wallet: Pubkey,
    metrics: WorkMetrics,
    ai_summary: dict,
    date: int
) -> str:
    """
    Submit daily work attestation to Solana smart contract.

    Returns:
        Transaction signature
    """

    # 1. Load oracle wallet (stored encrypted on disk)
    oracle_keypair = load_oracle_wallet()

    # 2. Connect to Solana
    client = AsyncClient("https://api.devnet.solana.com")  # Or Helius RPC
    provider = Provider(client, Wallet(oracle_keypair))

    # 3. Load program
    program = await Program.at(
        Pubkey.from_string("WrkChain11111111111111111111111111111111111"),
        provider
    )

    # 4. Generate proof hash
    proof_hash = generate_proof_hash(ai_summary, metrics, date)

    # 5. Derive PDAs
    vault_pda, vault_bump = Pubkey.find_program_address(
        [b"vault", bytes(employee_wallet), bytes(admin_wallet)],
        program.program_id
    )

    record_pda, record_bump = Pubkey.find_program_address(
        [b"record", bytes(vault_pda), date.to_bytes(8, 'little')],
        program.program_id
    )

    # 6. Build transaction
    tx = await program.rpc["submit_daily_attestation"](
        date,
        {
            "hours_worked": metrics.hours_worked,
            "quality_score": metrics.quality_score,
            "tasks_completed": metrics.tasks_completed,
            "blockers_encountered": metrics.blockers_encountered,
        },
        proof_hash,
        ctx=Context(
            accounts={
                "daily_record": record_pda,
                "vault": vault_pda,
                "oracle": oracle_keypair.pubkey(),
                "system_program": Pubkey.from_string("11111111111111111111111111111111"),
            },
        ),
    )

    print(f"✅ Attestation submitted: {tx}")
    return str(tx)


def generate_proof_hash(ai_summary: dict, metrics: WorkMetrics, date: int) -> bytes:
    """
    Generate SHA256 hash of work proof.
    This hash goes on-chain, full data stays off-chain.
    """

    proof_data = {
        'date': date,
        'metrics': {
            'hours': metrics.hours_worked,
            'quality': metrics.quality_score,
            'tasks': metrics.tasks_completed,
            'blockers': metrics.blockers_encountered,
        },
        'summary': ai_summary,
        'version': '1.0'
    }

    # Canonical JSON
    canonical = json.dumps(proof_data, sort_keys=True)
    hash_bytes = hashlib.sha256(canonical.encode()).digest()

    return hash_bytes


def load_oracle_wallet() -> Keypair:
    """
    Load oracle wallet from encrypted storage.
    """
    # Read from config or environment
    import os
    keypair_path = os.path.expanduser("~/.workchain_oracle_keypair.json")

    with open(keypair_path, 'r') as f:
        keypair_data = json.load(f)

    return Keypair.from_bytes(bytes(keypair_data))
```

---

### Scheduler (Cron Job)

```python
# loggerheads/oracle/scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=16, minute=30, day_of_week='mon-fri')
async def daily_attestation_job():
    """
    Runs every weekday at 4:30 PM.
    """

    print("⏰ 4:30 PM - Starting daily attestation process...")

    # 1. Get today's screenshots
    today = datetime.now().date()
    screenshots = get_screenshots_for_date(today)

    if not screenshots:
        print("⚠️  No screenshots today, skipping attestation")
        return

    # 2. Generate AI summary (existing Loggerheads logic)
    from ..ai_summarizer import summarize_work_with_ai
    ai_summary = summarize_work_with_ai(
        all_ocr_text=[s['extracted_text'] for s in screenshots],
        ollama_url="http://localhost:11434",
        ollama_model="llama3.2"
    )

    # 3. Calculate metrics
    from .metrics_calculator import calculate_work_metrics
    user_context = get_user_context()
    metrics = calculate_work_metrics(screenshots, ai_summary, user_context)

    print(f"📊 Metrics calculated:")
    print(f"   Hours: {metrics.hours_worked}")
    print(f"   Quality: {metrics.quality_score}/100")
    print(f"   Tasks: {metrics.tasks_completed}")
    print(f"   Blockers: {metrics.blockers_encountered}")

    # 4. Submit to blockchain
    from .attestation_submitter import submit_daily_attestation
    from ..config import EMPLOYEE_WALLET, ADMIN_WALLET

    try:
        tx_signature = await submit_daily_attestation(
            employee_wallet=EMPLOYEE_WALLET,
            admin_wallet=ADMIN_WALLET,
            metrics=metrics,
            ai_summary=ai_summary,
            date=int(today.timestamp())
        )

        print(f"✅ Blockchain submission successful: {tx_signature}")

        # 5. Post to Discord
        from ..integrations.discord_client import post_daily_summary
        await post_daily_summary(ai_summary, metrics, tx_signature)

        print(f"✅ Discord summary posted")

    except Exception as e:
        print(f"❌ Error submitting attestation: {e}")
        # TODO: Retry logic, alert user


def start_scheduler():
    """
    Start the scheduler (called by CLI).
    """
    scheduler.start()
    print("✅ Scheduler started - will run attestation daily at 4:30 PM")

    # Keep running
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
```

---

## Component 3: React Frontend

### Purpose

Web dashboard for both employees and admins to:
- View vault status
- Withdraw funds
- Create vaults (admin)
- Resolve disputes (admin)

### Architecture

```
workchain-frontend/
├── src/
│   ├── components/
│   │   ├── EmployeeDashboard.tsx
│   │   ├── AdminDashboard.tsx
│   │   ├── VaultCard.tsx
│   │   ├── DailyProgress.tsx
│   │   ├── WithdrawButton.tsx
│   │   └── DisputeForm.tsx
│   ├── hooks/
│   │   ├── useWorkChainProgram.ts
│   │   ├── useVault.ts
│   │   └── useDailyRecords.ts
│   ├── lib/
│   │   ├── solana.ts
│   │   └── idl/
│   │       └── workchain.json
│   └── App.tsx
```

### Key Hook: `useVault`

```typescript
// src/hooks/useVault.ts

import { useAnchorWallet, useConnection } from '@solana/wallet-adapter-react';
import { Program, AnchorProvider } from '@coral-xyz/anchor';
import { PublicKey } from '@solana/web3.js';
import { useQuery } from '@tanstack/react-query';
import IDL from '../lib/idl/workchain.json';

const PROGRAM_ID = new PublicKey('WrkChain11111111111111111111111111111111111');

export function useVault(employeeWallet?: PublicKey, adminWallet?: PublicKey) {
  const wallet = useAnchorWallet();
  const { connection } = useConnection();

  const { data: vaultData, isLoading } = useQuery({
    queryKey: ['vault', employeeWallet?.toString()],
    queryFn: async () => {
      if (!wallet || !employeeWallet || !adminWallet) return null;

      const provider = new AnchorProvider(connection, wallet, {});
      const program = new Program(IDL, PROGRAM_ID, provider);

      // Derive vault PDA
      const [vaultPDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from('vault'),
          employeeWallet.toBuffer(),
          adminWallet.toBuffer(),
        ],
        program.programId
      );

      // Fetch vault account
      const vaultAccount = await program.account.employeeVault.fetch(vaultPDA);

      return {
        address: vaultPDA,
        totalLocked: vaultAccount.totalLocked.toNumber() / 1e6, // Convert to USDC
        unlockedBalance: vaultAccount.unlockedBalance.toNumber() / 1e6,
        dailyUnlock: vaultAccount.dailyUnlockAmount.toNumber() / 1e6,
        daysAchieved: vaultAccount.daysAchieved,
        daysMissed: vaultAccount.daysMissed,
        thresholdConfig: vaultAccount.thresholdConfig,
        paused: vaultAccount.paused,
      };
    },
    enabled: !!wallet && !!employeeWallet && !!adminWallet,
    refetchInterval: 10000, // Poll every 10s
  });

  return { vault: vaultData, isLoading };
}
```

### Withdraw Function

```typescript
// src/hooks/useWithdraw.ts

import { useAnchorWallet, useConnection } from '@solana/wallet-adapter-react';
import { Program, AnchorProvider } from '@coral-xyz/anchor';
import { PublicKey } from '@solana/web3.js';
import { getAssociatedTokenAddress, TOKEN_PROGRAM_ID } from '@solana/spl-token';

export function useWithdraw() {
  const wallet = useAnchorWallet();
  const { connection } = useConnection();

  const withdraw = async (amount: number) => {
    if (!wallet) throw new Error('Wallet not connected');

    const provider = new AnchorProvider(connection, wallet, {});
    const program = new Program(IDL, PROGRAM_ID, provider);

    // Derive vault PDA
    const [vaultPDA] = PublicKey.findProgramAddressSync(
      [Buffer.from('vault'), wallet.publicKey.toBuffer(), adminWallet.toBuffer()],
      program.programId
    );

    // Get token accounts
    const USDC_MINT = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'); // Mainnet USDC
    const vaultTokenAccount = await getAssociatedTokenAddress(USDC_MINT, vaultPDA, true);
    const employeeTokenAccount = await getAssociatedTokenAddress(USDC_MINT, wallet.publicKey);

    // Call withdraw instruction
    const tx = await program.methods
      .withdraw(new BN(amount * 1e6)) // Convert to lamports
      .accounts({
        vault: vaultPDA,
        employee: wallet.publicKey,
        vaultTokenAccount,
        employeeTokenAccount,
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .rpc();

    console.log('Withdrawal successful:', tx);
    return tx;
  };

  return { withdraw };
}
```

---

## Data Flow

### Complete Day Cycle

```
8:00 AM - Employee starts work
└─> Loggerheads starts tracking (activity_tracker.py)
    └─> Screenshot every 10s
    └─> OCR extraction (ocr_processor.py)
    └─> Save to SQLite (database.py)

4:30 PM - End of day
└─> Scheduler triggers (oracle/scheduler.py)
    ├─> Fetch all screenshots from DB
    ├─> Call AI summarizer (ai_summarizer.py)
    │   └─> Ollama analyzes → generates summary
    ├─> Calculate metrics (oracle/metrics_calculator.py)
    │   ├─> Hours: 7.2
    │   ├─> Quality: 85/100
    │   ├─> Tasks: 4
    │   └─> Blockers: 1
    ├─> Generate proof hash (SHA256)
    └─> Submit to Solana (oracle/attestation_submitter.py)
        └─> Smart contract: submit_daily_attestation()
            ├─> Create DailyRecord PDA
            ├─> Check threshold: 7.2 >= 6? YES
            ├─> Unlock $150 USDC
            └─> Emit event

4:31 PM - Post to Discord
└─> Discord integration (integrations/discord_client.py)
    └─> POST to webhook
        └─> Admin sees summary in Discord channel

5:00 PM - Employee withdraws
└─> Opens web dashboard (React)
    ├─> Connects Phantom wallet
    ├─> Sees unlocked balance: $150
    └─> Clicks "Withdraw"
        └─> Smart contract: withdraw()
            └─> Transfer $150 USDC to employee wallet

Next day - Repeat
```

---

## Discord Integration

### Enhanced Discord Posting

```python
# loggerheads/integrations/discord_client.py

import aiohttp
import os
from datetime import datetime

async def post_daily_summary(
    ai_summary: dict,
    metrics: WorkMetrics,
    tx_signature: str
):
    """
    Post daily work summary to Discord via webhook.

    Admin sees full summary.
    Employee only sees "Summary posted to admin channel."
    """

    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        print("⚠️  No Discord webhook configured, skipping")
        return

    # Format summary for Discord
    embed = {
        "title": f"📊 Daily Work Summary - {datetime.now().strftime('%B %d, %Y')}",
        "color": 0x00ff00 if metrics.hours_worked >= 6 else 0xff9900,
        "fields": [
            {
                "name": "⏱️ Hours Worked",
                "value": f"{metrics.hours_worked} hours",
                "inline": True
            },
            {
                "name": "⭐ Quality Score",
                "value": f"{metrics.quality_score}/100",
                "inline": True
            },
            {
                "name": "✅ Tasks Completed",
                "value": str(metrics.tasks_completed),
                "inline": True
            },
            {
                "name": "🔨 What I Worked on Today",
                "value": format_list(ai_summary.get('tasks_worked_on', [])),
                "inline": False
            },
        ],
        "footer": {
            "text": f"Verified on Solana | TX: {tx_signature[:16]}..."
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    # Add completed tasks if any
    completed = ai_summary.get('completed_tasks', [])
    if completed and completed[0] != "No specific completions identified from screenshots":
        embed['fields'].append({
            "name": "🏁 What I Completed",
            "value": format_list(completed),
            "inline": False
        })

    # Add blockers if any
    blockers = ai_summary.get('problems_blockers', [])
    if blockers and blockers[0] != "No significant blockers identified":
        embed['fields'].append({
            "name": "⚠️ Issues / Blockers",
            "value": format_list(blockers),
            "inline": False
        })

    # Send to Discord
    async with aiohttp.ClientSession() as session:
        payload = {
            "embeds": [embed],
            "username": "WorkChain Bot",
            "avatar_url": "https://workchain.xyz/logo.png"  # Your logo
        }

        async with session.post(webhook_url, json=payload) as resp:
            if resp.status == 204:
                print("✅ Discord summary posted")
            else:
                print(f"❌ Discord post failed: {resp.status}")


def format_list(items: list) -> str:
    """Format list items for Discord embed."""
    if not items:
        return "_No items_"

    return "\n".join(f"• {item}" for item in items[:5])  # Max 5 items
```

---

## Dispute Resolution

### Full Flow

```
Scenario: Employee worked 7 hours, AI says 5 hours

Step 1: Employee sees daily record in dashboard
        ├─> Date: Oct 11
        ├─> Hours: 5 hours
        ├─> Threshold met: NO ❌
        └─> Unlocked: $0

Step 2: Employee clicks "Dispute"
        └─> Opens DisputeForm.tsx
            └─> Employee enters reason: "AI missed 2 hours of terminal work"
            └─> Submits

Step 3: Frontend calls smart contract: dispute_record()
        └─> Updates DailyRecord.disputed = true
        └─> Emits DisputeFiledEvent

Step 4: Admin sees notification in Discord
        └─> "⚠️ Dispute filed by alice.sol for Oct 11"
        └─> Link to resolve: https://dashboard.workchain.xyz/disputes

Step 5: Admin reviews in dashboard
        ├─> Views original AI summary
        ├─> Checks sample screenshots (if stored)
        ├─> Makes decision: "Employee is correct, AI missed terminal work"

Step 6: Admin clicks "Approve Dispute"
        └─> Frontend calls: resolve_dispute(approved=true)
            └─> Smart contract retroactively unlocks $150
            └─> Updates vault.days_achieved += 1
            └─> Updates vault.days_missed -= 1

Step 7: Employee sees update in dashboard
        └─> Unlocked balance: $150 (updated)
        └─> Notification: "Dispute approved! Funds unlocked."
```

### Dispute Resolution UI (React)

```typescript
// src/components/DisputeForm.tsx

import { useState } from 'react';
import { useAnchorWallet } from '@solana/wallet-adapter-react';
import { useProgram } from '../hooks/useWorkChainProgram';

export function DisputeForm({ date }: { date: number }) {
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const wallet = useAnchorWallet();
  const program = useProgram();

  const handleSubmit = async () => {
    if (!wallet || !program) return;

    setSubmitting(true);

    try {
      // Derive PDAs
      const [vaultPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('vault'), wallet.publicKey.toBuffer(), adminWallet.toBuffer()],
        program.programId
      );

      const [recordPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from('record'), vaultPDA.toBuffer(), dateToBytes(date)],
        program.programId
      );

      // Call dispute_record
      const tx = await program.methods
        .disputeRecord(date, reason)
        .accounts({
          dailyRecord: recordPDA,
          vault: vaultPDA,
          employee: wallet.publicKey,
        })
        .rpc();

      console.log('Dispute filed:', tx);
      alert('Dispute submitted! Admin will review.');
    } catch (error) {
      console.error('Error filing dispute:', error);
      alert('Failed to file dispute');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="dispute-form">
      <h3>Dispute This Record</h3>
      <p>Explain why you believe the AI assessment was incorrect:</p>
      <textarea
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        placeholder="E.g., AI missed 2 hours of terminal work where I was debugging..."
        rows={4}
      />
      <button onClick={handleSubmit} disabled={submitting || !reason}>
        {submitting ? 'Submitting...' : 'Submit Dispute'}
      </button>
    </div>
  );
}
```

---

## Deployment Architecture

### Development

```
Employee Machine:
├─> Loggerheads (Python)
│   └─> Connects to Solana Devnet
│
└─> React Frontend (localhost:5173)
    └─> Connects to Solana Devnet

Solana Devnet:
└─> WorkChain Program deployed

Discord:
└─> Test webhook
```

### Production

```
Employee Machines (multiple):
├─> Loggerheads (Python) - installed locally
│   └─> Connects to Solana Mainnet (Helius RPC)
│   └─> Oracle wallet (encrypted keypair)
│
└─> Web browser
    └─> Opens https://app.workchain.xyz

Hosting:
├─> Frontend: Vercel (React app)
└─> Smart Contract: Solana Mainnet

External Services:
├─> Helius RPC (Solana connection)
├─> Discord (webhooks)
└─> Ollama (local on each employee machine)
```

---

## Implementation Timeline

### Week 1: Smart Contract

**Day 1-2:**
- [x] Setup Anchor workspace
- [x] Define account structures
- [x] Implement initialize_vault()
- [x] Write tests

**Day 3-4:**
- [x] Implement submit_daily_attestation()
- [x] Implement verify_and_unlock() logic
- [x] Implement withdraw()
- [x] Write tests

**Day 5:**
- [x] Implement dispute_record() & resolve_dispute()
- [x] Implement finalize_period()
- [x] Write comprehensive tests

**Day 6-7:**
- [x] Deploy to devnet
- [x] Test all instructions
- [x] Document program IDs

---

### Week 2: Python Backend

**Day 8-9:**
- [x] Create blockchain/ module
- [x] Implement Solana client (solders)
- [x] Implement wallet manager
- [x] Test: submit dummy attestation to devnet

**Day 10-11:**
- [x] Create oracle/ module
- [x] Implement metrics_calculator.py (hours + quality + tasks)
- [x] Implement proof_generator.py
- [x] Test: calculate metrics from sample data

**Day 12:**
- [x] Implement attestation_submitter.py
- [x] Test: full flow (track → calculate → submit to chain)

**Day 13:**
- [x] Implement scheduler.py (4:30 PM cron)
- [x] Enhance Discord integration
- [x] Test: automated daily cycle

**Day 14:**
- [x] Integration testing
- [x] Bug fixes

---

### Week 3: React Frontend

**Day 15-16:**
- [x] Setup React + Vite + TypeScript
- [x] Install Solana Wallet Adapter
- [x] Create basic layout
- [x] Implement wallet connection

**Day 17-18:**
- [x] Build EmployeeDashboard
- [x] Implement useVault() hook
- [x] Build VaultCard component
- [x] Build DailyProgress component
- [x] Test: displays real data from devnet

**Day 19-20:**
- [x] Build AdminDashboard
- [x] Implement create vault form
- [x] Test: create vault from browser

**Day 21:**
- [x] Implement withdraw UI
- [x] Implement dispute form
- [x] Polish & styling
- [x] Deploy to Vercel

---

### Week 4: Demo & Polish

**Day 22-23:**
- [x] End-to-end testing
- [x] Bug fixes

**Day 24-25:**
- [x] Record demo video
- [x] Create pitch deck
- [x] Write documentation

**Day 26-27:**
- [x] Deploy to mainnet (if ready)
- [x] Onboard 5 beta users
- [x] Gather feedback

**Day 28:**
- [x] Submit to hackathon
- [x] Social media launch

---

## Testing Strategy

### Smart Contract Tests

```rust
// tests/workchain.ts

describe('WorkChain', () => {
  it('Creates vault and locks funds', async () => {
    // Test initialize_vault()
  });

  it('Submits attestation and unlocks funds when threshold met', async () => {
    // Test submit_daily_attestation() with passing metrics
  });

  it('Does not unlock when threshold missed', async () => {
    // Test submit_daily_attestation() with failing metrics
  });

  it('Allows employee to withdraw unlocked funds', async () => {
    // Test withdraw()
  });

  it('Allows employee to dispute record', async () => {
    // Test dispute_record()
  });

  it('Allows admin to resolve dispute', async () => {
    // Test resolve_dispute()
  });

  it('Finalizes period and redistributes unearned funds', async () => {
    // Test finalize_period()
  });
});
```

### Python Tests

```python
# tests/test_metrics_calculator.py

def test_calculate_hours():
    """Test hour calculation from screenshots."""
    pass

def test_quality_score():
    """Test quality scoring algorithm."""
    pass

def test_task_counting():
    """Test task completion detection."""
    pass

# tests/test_attestation_submitter.py

@pytest.mark.asyncio
async def test_submit_attestation():
    """Test submission to Solana devnet."""
    pass
```

### Frontend Tests

```typescript
// src/components/__tests__/VaultCard.test.tsx

describe('VaultCard', () => {
  it('displays locked and unlocked balances', () => {
    // Test component rendering
  });

  it('calls withdraw function on button click', () => {
    // Test user interaction
  });
});
```

---

## Summary

### What We're Building

**ONE application (WorkChain) with:**

1. **Enhanced Loggerheads (Python)** - Runs on employee's machine
   - Tracks work
   - Analyzes with AI
   - Calculates metrics (hours, quality, tasks)
   - Submits attestations to Solana
   - Posts summaries to Discord

2. **Smart Contract (Rust)** - ONE Anchor program on Solana
   - Manages vaults (lock/unlock/withdraw)
   - Verifies oracle attestations
   - Handles disputes
   - Redistributes unearned funds

3. **Web Dashboard (React)** - Browser-based UI
   - Employee view (balance, progress, withdraw)
   - Admin view (create vaults, resolve disputes)
   - Connects to Solana via wallet

### Key Innovations

1. **Quality-Based Unlocking** (not just hours)
   - Hours + Quality + Tasks = comprehensive assessment
   - Configurable thresholds (AND/OR logic)

2. **AI + Blockchain** (trust but verify)
   - AI does analysis (off-chain)
   - Oracle submits attestation (on-chain)
   - Employee can dispute (human override)

3. **Discord Integration** (transparent reporting)
   - Admin sees daily summaries automatically
   - On-chain proof links
   - No manual reporting needed

4. **Loss Aversion Psychology**
   - Money locked upfront (not earned later)
   - Daily stakes (not monthly)
   - Transparent metrics (know where you stand)

---

**Ready to build? Let's start with Week 1: Smart Contracts!**

*Last Updated: October 11, 2025*
*Version: 1.0*
