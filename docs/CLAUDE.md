# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**WorkChain (Loggerheads)** is a blockchain-powered work tracking application that automatically pays workers based on verified hours. It combines traditional activity tracking with Solana smart contracts to create trustless, automated payments.

### Key Components

- **Activity Tracker**: Monitors active windows and captures screenshots
- **Solana Integration**: Smart contracts on Solana for payment automation
- **Python CLI**: User-friendly command-line interface for employees and employers
- **Oracle System**: Verifies and submits work hours to blockchain

## Critical UX Philosophy ⭐

**THIS IS THE MOST IMPORTANT RULE FOR THIS PROJECT:**

### Hide Blockchain Complexity from End Users

Crypto's poor UX is the #1 barrier to adoption. We must be RUTHLESS about hiding unnecessary blockchain details.

#### ✅ DO: Keep crypto where NECESSARY
- Wallet addresses (needed for setup)
- Transaction confirmations (users need proof)
- Balance information (users want to see their money)
- Explicit blockchain operations (withdraw, submit to chain)

#### ❌ DON'T: Show crypto where NOT NECESSARY
- **PDAs (Program Derived Addresses)** - users don't need to see these
- **Token account addresses** - auto-derived, hide from users
- **Discriminators, bumps, seeds** - pure implementation details
- **Technical blockchain terms** - use human language instead
- **Internal IDs** - use human-friendly names

#### Examples of Good UX

**BAD (Too Technical):**
```
Vault PDA: 5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D
Vault Token Account: 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU
Employee Token Account: HzVwVx...
Discriminator: [48, 191, 163, 44, 71, 129, 63, 164]
```

**GOOD (User-Friendly):**
```
Employer: Acme Corp
Your Balance: $150.00 available
```

**BAD (Blockchain Jargon):**
```
Transaction simulation failed: InstructionError(2, Custom(1))
```

**GOOD (Actionable):**
```
Not enough funds in your wallet.
Get devnet USDC: https://faucet.solana.com/
```

### Rules for All User-Facing Messages

1. **Use human language**: "employer" not "admin pubkey", "balance" not "unlocked_amount"
2. **Hide internal IDs**: Show wallet addresses only when absolutely necessary
3. **Actionable errors**: Tell users what to DO, not what went wrong technically
4. **Progressive disclosure**: Show basic info by default, technical details only if requested
5. **Familiar metaphors**: "wallet" over "keypair", "balance" over "token account"

### Configuration Display Guidelines

**Employee Should See:**
- Employer name/identifier
- Their wallet (short form)
- Balance (in dollars)
- Auto-submit status

**Employee Should NOT See:**
- Vault PDA
- Token account addresses
- Bumps, seeds, discriminators
- Oracle addresses (they don't need to know this exists)

**When in doubt:** If a normal person using PayPal wouldn't see it, hide it from our users.

## Architecture

### Directory Structure

```
loggerheads/
├── cli.py                 # User-facing CLI commands
├── activity_tracker.py    # Window monitoring
├── blockchain.py          # Solana smart contract integration
├── vault_creation.py      # Employer vault setup
├── vault_config.py        # Configuration management
├── token_utils.py         # Balance checking utilities
├── idl_utils.py           # IDL/discriminator management
├── oracle.py              # Oracle for submitting hours
├── database.py            # SQLite for local tracking
└── scheduler.py           # Background tracking daemon
```

### Data Flow

1. **Tracking**: Activity tracker → Screenshots → Local database
2. **Submission**: Calculate hours → Oracle signs → Submit to Solana
3. **Payment**: Smart contract verifies → Auto-unlock funds → Employee withdraws

## Running the Application

```bash
# Interactive setup (recommended for first-time users)
loggerheads

# Start tracking
loggerheads start

# Check status
loggerheads status

# Check balance
loggerheads balance

# Submit hours to blockchain
loggerheads submit

# Withdraw earned funds
loggerheads withdraw
```

## Development Commands

```bash
# View logs
loggerheads logs

# Check discriminators (technical)
python3 -m loggerheads.idl_utils

# Test token utilities
python3 -m loggerheads.token_utils
```

## Key Files for UX Improvements

When improving user-facing text, focus on:
- `loggerheads/cli.py` - All command outputs
- `loggerheads/vault_creation.py` - Employer onboarding
- `loggerheads/vault_config.py` - Configuration display
- Error messages in `loggerheads/blockchain.py`

## Testing Philosophy

Always test from a non-technical user perspective:
1. Would my parent understand this message?
2. Does this require blockchain knowledge to use?
3. Can they complete the task without googling crypto terms?

If answer is NO to any question, simplify the UX.
