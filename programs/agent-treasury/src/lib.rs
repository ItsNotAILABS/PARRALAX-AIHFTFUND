use anchor_lang::prelude::*;
use anchor_spl::associated_token::AssociatedToken;
use anchor_spl::token::{self, Mint, Token, TokenAccount, TransferChecked};

declare_id!("11111111111111111111111111111111");

// PLACEHOLDER PROGRAM ID: Replace with a freshly generated, verifiable program key
// before any build/deployment. This source is NOT deployed.
#[program]
pub mod parralax_agent_treasury {
    use super::*;

    pub fn initialize(
        ctx: Context<Initialize>,
        per_tx_cap: u64,
        daily_cap: u64,
        lifetime_cap: u64,
        expires_at: i64,
    ) -> Result<()> {
        require!(valid_caps(per_tx_cap, daily_cap, lifetime_cap), ErrorCode::InvalidCaps);
        require_keys_neq!(ctx.accounts.owner.key(), ctx.accounts.agent.key(), ErrorCode::InvalidAuthority);
        require_keys_neq!(ctx.accounts.agent.key(), ctx.accounts.beneficiary.key(), ErrorCode::InvalidAuthority);
        let now = Clock::get()?.unix_timestamp;
        require!(expires_at > now, ErrorCode::Expired);
        let t = &mut ctx.accounts.treasury;
        t.owner = ctx.accounts.owner.key();
        t.agent = ctx.accounts.agent.key();
        t.beneficiary = ctx.accounts.beneficiary.key();
        t.mint = ctx.accounts.mint.key();
        t.bump = ctx.bumps.treasury;
        t.per_tx_cap = per_tx_cap;
        t.daily_cap = daily_cap;
        t.lifetime_cap = lifetime_cap;
        t.daily_spent = 0;
        t.lifetime_spent = 0;
        t.window_start = now;
        t.expires_at = expires_at;
        t.next_nonce = 0;
        t.revoked = false;
        emit!(TreasuryCreated { treasury: t.key(), owner: t.owner, agent: t.agent, mint: t.mint });
        Ok(())
    }

    pub fn deposit(ctx: Context<Deposit>, amount: u64) -> Result<()> {
        require!(amount > 0, ErrorCode::InvalidAmount);
        token::transfer_checked(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                TransferChecked {
                    from: ctx.accounts.owner_token.to_account_info(),
                    mint: ctx.accounts.mint.to_account_info(),
                    to: ctx.accounts.vault.to_account_info(),
                    authority: ctx.accounts.owner.to_account_info(),
                },
            ),
            amount,
            ctx.accounts.mint.decimals,
        )?;
        emit!(TreasuryDeposit { treasury: ctx.accounts.treasury.key(), amount });
        Ok(())
    }

    pub fn spend(ctx: Context<Spend>, amount: u64, nonce: u64) -> Result<()> {
        let t = &mut ctx.accounts.treasury;
        let now = Clock::get()?.unix_timestamp;
        require!(!t.revoked, ErrorCode::Revoked);
        require!(now < t.expires_at, ErrorCode::Expired);
        require!(amount > 0 && amount <= t.per_tx_cap, ErrorCode::PerTransactionLimit);
        require!(nonce == t.next_nonce, ErrorCode::InvalidNonce);
        require!(now >= t.window_start, ErrorCode::ClockRegression);
        if now.saturating_sub(t.window_start) >= 86_400 {
            t.window_start = now;
            t.daily_spent = 0;
        }
        require!(checked_spend(t.daily_spent, amount, t.daily_cap), ErrorCode::DailyLimit);
        require!(checked_spend(t.lifetime_spent, amount, t.lifetime_cap), ErrorCode::LifetimeLimit);
        let daily = t.daily_spent.checked_add(amount).ok_or(ErrorCode::Overflow)?;
        let lifetime = t.lifetime_spent.checked_add(amount).ok_or(ErrorCode::Overflow)?;
        require!(daily <= t.daily_cap, ErrorCode::DailyLimit);
        require!(lifetime <= t.lifetime_cap, ErrorCode::LifetimeLimit);
        t.daily_spent = daily;
        t.lifetime_spent = lifetime;
        t.next_nonce = nonce.checked_add(1).ok_or(ErrorCode::Overflow)?;

        let owner = t.owner;
        let agent = t.agent;
        let beneficiary = t.beneficiary;
        let mint = t.mint;
        let bump = [t.bump];
        let seeds: &[&[u8]] = &[b"treasury", owner.as_ref(), agent.as_ref(), beneficiary.as_ref(), mint.as_ref(), &bump];
        token::transfer_checked(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                TransferChecked {
                    from: ctx.accounts.vault.to_account_info(),
                    mint: ctx.accounts.mint.to_account_info(),
                    to: ctx.accounts.beneficiary_token.to_account_info(),
                    authority: t.to_account_info(),
                },
                &[seeds],
            ),
            amount,
            ctx.accounts.mint.decimals,
        )?;
        emit!(TreasurySpend { treasury: t.key(), agent, beneficiary: t.beneficiary, mint: t.mint, amount, nonce });
        Ok(())
    }

    pub fn revoke(ctx: Context<OwnerAction>) -> Result<()> {
        ctx.accounts.treasury.revoked = true;
        emit!(TreasuryRevoked { treasury: ctx.accounts.treasury.key() });
        Ok(())
    }

    pub fn withdraw(ctx: Context<Withdraw>, amount: u64) -> Result<()> {
        require!(amount > 0, ErrorCode::InvalidAmount);
        let t = &ctx.accounts.treasury;
        let owner = t.owner;
        let agent = t.agent;
        let bump = [t.bump];
        let seeds: &[&[u8]] = &[b"treasury", owner.as_ref(), agent.as_ref(), &bump];
        token::transfer_checked(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                TransferChecked {
                    from: ctx.accounts.vault.to_account_info(),
                    mint: ctx.accounts.mint.to_account_info(),
                    to: ctx.accounts.owner_token.to_account_info(),
                    authority: t.to_account_info(),
                },
                &[seeds],
            ),
            amount,
            ctx.accounts.mint.decimals,
        )?;
        emit!(TreasuryWithdrawal { treasury: t.key(), owner, amount });
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(mut)]
    pub owner: Signer<'info>,
    /// CHECK: Agent is stored as a public key, and must sign each spend.
    pub agent: UncheckedAccount<'info>,
    /// CHECK: Beneficiary public key is pinned. SPL destination verified on spends.
    pub beneficiary: UncheckedAccount<'info>,
    pub mint: Account<'info, Mint>,
    #[account(
        init, payer = owner, space = 8 + Treasury::INIT_SPACE,
        seeds = [b"treasury", owner.key().as_ref(), agent.key().as_ref(), beneficiary.key().as_ref(), mint.key().as_ref()],
        bump
    )]
    pub treasury: Account<'info, Treasury>,
    #[account(
        init, payer = owner,
        associated_token::mint = mint,
        associated_token::authority = treasury
    )]
    pub vault: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Deposit<'info> {
    #[account(mut, address = treasury.owner)]
    pub owner: Signer<'info>,
    #[account(has_one = owner, has_one = mint)]
    pub treasury: Account<'info, Treasury>,
    pub mint: Account<'info, Mint>,
    #[account(mut, token::mint = mint, token::authority = owner)]
    pub owner_token: Account<'info, TokenAccount>,
    #[account(mut, associated_token::mint = mint, associated_token::authority = treasury)]
    pub vault: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct Spend<'info> {
    #[account(address = treasury.agent)]
    pub agent: Signer<'info>,
    #[account(mut, has_one = agent, has_one = mint)]
    pub treasury: Account<'info, Treasury>,
    pub mint: Account<'info, Mint>,
    #[account(mut, associated_token::mint = mint, associated_token::authority = treasury)]
    pub vault: Account<'info, TokenAccount>,
    #[account(mut, token::mint = mint, token::authority = treasury.beneficiary)]
    pub beneficiary_token: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct OwnerAction<'info> {
    #[account(address = treasury.owner)]
    pub owner: Signer<'info>,
    #[account(mut, has_one = owner)]
    pub treasury: Account<'info, Treasury>,
}

#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(address = treasury.owner)]
    pub owner: Signer<'info>,
    #[account(has_one = owner, has_one = mint)]
    pub treasury: Account<'info, Treasury>,
    pub mint: Account<'info, Mint>,
    #[account(mut, associated_token::mint = mint, associated_token::authority = treasury)]
    pub vault: Account<'info, TokenAccount>,
    #[account(mut, token::mint = mint, token::authority = owner)]
    pub owner_token: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
}

#[account]
#[derive(InitSpace)]
pub struct Treasury {
    pub owner: Pubkey,
    pub agent: Pubkey,
    pub beneficiary: Pubkey,
    pub mint: Pubkey,
    pub bump: u8,
    pub per_tx_cap: u64,
    pub daily_cap: u64,
    pub lifetime_cap: u64,
    pub daily_spent: u64,
    pub lifetime_spent: u64,
    pub window_start: i64,
    pub expires_at: i64,
    pub next_nonce: u64,
    pub revoked: bool,
}

#[event]
pub struct TreasuryCreated { pub treasury: Pubkey, pub owner: Pubkey, pub agent: Pubkey, pub mint: Pubkey }
#[event]
pub struct TreasuryDeposit { pub treasury: Pubkey, pub amount: u64 }
#[event]
pub struct TreasurySpend { pub treasury: Pubkey, pub agent: Pubkey, pub beneficiary: Pubkey, pub mint: Pubkey, pub amount: u64, pub nonce: u64 }
#[event]
pub struct TreasuryRevoked { pub treasury: Pubkey }
#[event]
pub struct TreasuryWithdrawal { pub treasury: Pubkey, pub owner: Pubkey, pub amount: u64 }

#[error_code]
pub enum ErrorCode {
    #[msg("Owner, agent and beneficiary must have distinct authority")] InvalidAuthority,
    #[msg("Invalid spending caps")] InvalidCaps,
    #[msg("Treasury expired")] Expired,
    #[msg("Treasury revoked")] Revoked,
    #[msg("Invalid amount")] InvalidAmount,
    #[msg("Per-transaction limit reached")] PerTransactionLimit,
    #[msg("Daily limit reached")] DailyLimit,
    #[msg("Lifetime limit reached")] LifetimeLimit,
    #[msg("Invalid replay nonce")] InvalidNonce,
    #[msg("Arithmetic overflow")] Overflow,
    #[msg("Clock regression")] ClockRegression,
}

fn valid_caps(per_tx: u64, daily: u64, lifetime: u64) -> bool {
    per_tx > 0 && per_tx <= daily && daily <= lifetime
}
fn checked_spend(current: u64, amount: u64, cap: u64) -> bool {
    current.checked_add(amount).map(|next| next <= cap).unwrap_or(false)
}
#[cfg(test)]
mod invariant_tests {
    use super::*;
    #[test]
    fn cap_ordering() {
        assert!(valid_caps(1, 10, 100));
        assert!(!valid_caps(0, 10, 100));
        assert!(!valid_caps(11, 10, 100));
        assert!(!valid_caps(1, 101, 100));
    }
    #[test]
    fn spending_arithmetic_and_limits() {
        assert!(checked_spend(7, 3, 10));
        assert!(!checked_spend(8, 3, 10));
        assert!(!checked_spend(u64::MAX, 1, u64::MAX));
        assert!(checked_spend(0, 1, 1));
    }
}
