use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};

declare_id!("5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D");

#[program]
pub mod workchain_program {
    use super::*;

    /// Admin creates vault and locks USDC
    pub fn initialize_vault(
        ctx: Context<InitializeVault>,
        locked_amount: u64,
        daily_target_hours: u8,
        daily_unlock: u64,
    ) -> Result<()> {
        let vault = &mut ctx.accounts.vault;

        vault.owner = ctx.accounts.owner.key();
        vault.admin = ctx.accounts.admin.key();
        vault.oracle = ctx.accounts.oracle.key();
        vault.locked_amount = locked_amount;
        vault.unlocked_amount = 0;
        vault.daily_target_hours = daily_target_hours;
        vault.daily_unlock = daily_unlock;
        vault.bump = ctx.bumps.vault;

        // Transfer USDC from admin to vault
        token::transfer(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.admin_token_account.to_account_info(),
                    to: ctx.accounts.vault_token_account.to_account_info(),
                    authority: ctx.accounts.admin.to_account_info(),
                },
            ),
            locked_amount,
        )?;

        msg!("Vault initialized!");
        msg!("Owner: {}", vault.owner);
        msg!("Locked: {} USDC", locked_amount / 1_000_000); // Display in USDC
        msg!("Daily target: {} hours", daily_target_hours);
        msg!("Daily unlock: {} USDC", daily_unlock / 1_000_000);

        Ok(())
    }

    /// Oracle submits daily hours → auto-unlock if target met
    pub fn submit_hours(
        ctx: Context<SubmitHours>,
        hours_worked: u8,
    ) -> Result<()> {
        let vault = &mut ctx.accounts.vault;

        msg!("Hours worked: {}", hours_worked);
        msg!("Target hours: {}", vault.daily_target_hours);

        // Check if target met
        if hours_worked >= vault.daily_target_hours {
            // Target met → unlock funds
            let unlock_amount = vault.daily_unlock;

            // Ensure we don't unlock more than available
            let available = vault.locked_amount.checked_sub(vault.unlocked_amount)
                .ok_or(ErrorCode::InsufficientFunds)?;

            let actual_unlock = if unlock_amount > available {
                available
            } else {
                unlock_amount
            };

            vault.unlocked_amount = vault.unlocked_amount
                .checked_add(actual_unlock)
                .ok_or(ErrorCode::Overflow)?;

            msg!("✅ Target met! Unlocked {} USDC", actual_unlock / 1_000_000);
        } else {
            // Target not met → forfeit
            msg!("❌ Target not met. No unlock.");
        }

        Ok(())
    }

    /// Employee withdraws unlocked USDC
    pub fn withdraw(
        ctx: Context<Withdraw>,
        amount: u64,
    ) -> Result<()> {
        let vault = &mut ctx.accounts.vault;

        require!(
            amount <= vault.unlocked_amount,
            ErrorCode::InsufficientUnlockedFunds
        );

        // Transfer USDC from vault to employee
        let vault_seeds = &[
            b"vault",
            vault.owner.as_ref(),
            vault.admin.as_ref(),
            &[vault.bump],
        ];

        token::transfer(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.vault_token_account.to_account_info(),
                    to: ctx.accounts.owner_token_account.to_account_info(),
                    authority: vault.to_account_info(),
                },
                &[vault_seeds],
            ),
            amount,
        )?;

        // Update vault balance
        vault.unlocked_amount = vault.unlocked_amount
            .checked_sub(amount)
            .ok_or(ErrorCode::Underflow)?;

        msg!("💸 Withdrawn {} USDC", amount / 1_000_000);

        Ok(())
    }
}

// ========== ACCOUNTS ==========

#[account]
pub struct Vault {
    pub owner: Pubkey,              // Employee wallet (32)
    pub admin: Pubkey,              // Admin wallet (32)
    pub oracle: Pubkey,             // Oracle (Loggerheads) (32)
    pub locked_amount: u64,         // Total USDC locked (8)
    pub unlocked_amount: u64,       // USDC available to withdraw (8)
    pub daily_target_hours: u8,     // Target hours per day (1)
    pub daily_unlock: u64,          // USDC to unlock per successful day (8)
    pub bump: u8,                   // PDA bump (1)
}

impl Vault {
    pub const LEN: usize = 8 + 32 + 32 + 32 + 8 + 8 + 1 + 8 + 1; // 130 bytes
}

// ========== INSTRUCTION CONTEXTS ==========

#[derive(Accounts)]
pub struct InitializeVault<'info> {
    #[account(
        init,
        payer = admin,
        space = Vault::LEN,
        seeds = [b"vault", owner.key().as_ref(), admin.key().as_ref()],
        bump
    )]
    pub vault: Account<'info, Vault>,

    #[account(mut)]
    pub admin: Signer<'info>,

    /// CHECK: Employee wallet (doesn't need to sign)
    pub owner: AccountInfo<'info>,

    /// CHECK: Oracle wallet (Loggerheads backend)
    pub oracle: AccountInfo<'info>,

    #[account(mut)]
    pub admin_token_account: Account<'info, TokenAccount>,

    #[account(mut)]
    pub vault_token_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct SubmitHours<'info> {
    #[account(
        mut,
        seeds = [b"vault", vault.owner.as_ref(), vault.admin.as_ref()],
        bump = vault.bump,
        constraint = vault.oracle == oracle.key() @ ErrorCode::UnauthorizedOracle
    )]
    pub vault: Account<'info, Vault>,

    pub oracle: Signer<'info>,
}

#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(
        mut,
        seeds = [b"vault", vault.owner.as_ref(), vault.admin.as_ref()],
        bump = vault.bump,
        constraint = vault.owner == owner.key() @ ErrorCode::Unauthorized
    )]
    pub vault: Account<'info, Vault>,

    pub owner: Signer<'info>,

    #[account(mut)]
    pub vault_token_account: Account<'info, TokenAccount>,

    #[account(mut)]
    pub owner_token_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

// ========== ERRORS ==========

#[error_code]
pub enum ErrorCode {
    #[msg("Unauthorized oracle")]
    UnauthorizedOracle,

    #[msg("Unauthorized user")]
    Unauthorized,

    #[msg("Insufficient funds in vault")]
    InsufficientFunds,

    #[msg("Insufficient unlocked funds")]
    InsufficientUnlockedFunds,

    #[msg("Overflow")]
    Overflow,

    #[msg("Underflow")]
    Underflow,
}
