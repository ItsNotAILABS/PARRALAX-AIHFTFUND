//! PARRALAX agent treasury: a bounded SPL-token vault controlled by a PDA.
//!
//! Roles
//! - owner: creates, funds, configures, withdraws from and closes a treasury.
//! - agent: may only `spend` to the fixed beneficiary, within the caps.
//! - guardian (optional): may only `pause` and `revoke`.
//!
//! SOURCE ONLY / UNAUDITED. See ../../DEPLOYMENT.md before any deployment.
use anchor_lang::prelude::*;
use anchor_spl::associated_token::AssociatedToken;
use anchor_spl::token::{self, CloseAccount, Mint, Token, TokenAccount, TransferChecked};

pub mod error;
pub mod mint_policy;
pub mod policy;
pub mod state;

pub use error::TreasuryError;
pub use state::{Treasury, TREASURY_SEED, TREASURY_VERSION};

// LOCALNET / TEST ONLY program ID (keypair is not committed). Replace with the
// managed production program ID before any non-local deployment.
declare_id!("5HJCtwtWWvDDQiMLVuvrwyqaVfXgX3hZnzMTarTKv61p");

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, Debug, PartialEq, Eq)]
pub struct PolicyParams {
    pub per_tx_cap: u64,
    pub daily_cap: u64,
    pub lifetime_cap: u64,
    pub expires_at: i64,
}

impl PolicyParams {
    fn validate(&self, now: i64) -> Result<()> {
        require!(
            policy::valid_caps(self.per_tx_cap, self.daily_cap, self.lifetime_cap),
            TreasuryError::InvalidCaps
        );
        require!(self.expires_at > now, TreasuryError::InvalidExpiry);
        Ok(())
    }
}

/// PDA signer seeds for a treasury. The single source of truth used by every
/// instruction that moves funds out of the vault (review finding C1).
pub fn treasury_signer_seeds<'a>(
    owner: &'a Pubkey,
    mint: &'a Pubkey,
    seed_id: &'a [u8; 8],
    bump: &'a [u8; 1],
) -> [&'a [u8]; 5] {
    [TREASURY_SEED, owner.as_ref(), mint.as_ref(), seed_id, bump]
}

fn transfer_from_vault<'info>(
    treasury: &Account<'info, Treasury>,
    vault: &Account<'info, TokenAccount>,
    mint: &Account<'info, Mint>,
    to: AccountInfo<'info>,
    token_program: &Program<'info, Token>,
    amount: u64,
) -> Result<()> {
    let seed_id = treasury.seed_id.to_le_bytes();
    let bump = [treasury.bump];
    let seeds = treasury_signer_seeds(&treasury.owner, &treasury.mint, &seed_id, &bump);
    token::transfer_checked(
        CpiContext::new_with_signer(
            token_program.to_account_info(),
            TransferChecked {
                from: vault.to_account_info(),
                mint: mint.to_account_info(),
                to,
                authority: treasury.to_account_info(),
            },
            &[&seeds],
        ),
        amount,
        mint.decimals,
    )
}

fn validate_agent(
    agent: &Pubkey,
    owner: &Pubkey,
    beneficiary: &Pubkey,
    guardian: Option<Pubkey>,
) -> Result<()> {
    require_keys_neq!(*agent, *owner, TreasuryError::InvalidAuthority);
    require_keys_neq!(*agent, *beneficiary, TreasuryError::InvalidAuthority);
    require!(guardian != Some(*agent), TreasuryError::InvalidAuthority);
    Ok(())
}

#[program]
pub mod parralax_agent_treasury {
    use super::*;

    pub fn initialize(
        ctx: Context<Initialize>,
        seed_id: u64,
        params: PolicyParams,
        guardian: Option<Pubkey>,
    ) -> Result<()> {
        let now = Clock::get()?.unix_timestamp;
        params.validate(now)?;
        let mint = &ctx.accounts.mint;
        require!(
            mint_policy::is_mint_allowed(&mint.key(), mint.freeze_authority.is_some()),
            TreasuryError::MintNotAllowed
        );
        let owner = ctx.accounts.owner.key();
        let agent = ctx.accounts.agent.key();
        let beneficiary = ctx.accounts.beneficiary.key();
        validate_agent(&agent, &owner, &beneficiary, guardian)?;
        let mint_key = mint.key();

        let t = &mut ctx.accounts.treasury;
        t.set_inner(Treasury {
            version: TREASURY_VERSION,
            bump: ctx.bumps.treasury,
            seed_id,
            owner,
            mint: mint_key,
            beneficiary,
            agent,
            guardian,
            per_tx_cap: params.per_tx_cap,
            daily_cap: params.daily_cap,
            lifetime_cap: params.lifetime_cap,
            daily_spent: 0,
            lifetime_spent: 0,
            last_refill_at: now,
            expires_at: params.expires_at,
            next_nonce: 0,
            revoked: false,
            paused: false,
        });
        emit!(TreasuryCreated {
            treasury: t.key(),
            owner,
            agent,
            beneficiary,
            mint: mint_key,
            seed_id,
            guardian
        });
        Ok(())
    }

    pub fn deposit(ctx: Context<Deposit>, amount: u64) -> Result<()> {
        require!(amount > 0, TreasuryError::InvalidAmount);
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
        emit!(TreasuryDeposit {
            treasury: ctx.accounts.treasury.key(),
            amount
        });
        Ok(())
    }

    /// Agent-signed transfer to the fixed beneficiary. `nonce` must equal
    /// `next_nonce`: a retried spend (e.g. after blockhash expiry with unknown
    /// status) cannot pay twice, at the cost of serializing an agent's spends.
    pub fn spend(ctx: Context<Spend>, amount: u64, nonce: u64) -> Result<()> {
        let now = Clock::get()?.unix_timestamp;
        ctx.accounts.treasury.record_spend(amount, nonce, now)?;
        let a = &ctx.accounts;
        transfer_from_vault(
            &a.treasury,
            &a.vault,
            &a.mint,
            a.beneficiary_token.to_account_info(),
            &a.token_program,
            amount,
        )?;
        emit!(TreasurySpend {
            treasury: a.treasury.key(),
            agent: a.agent.key(),
            beneficiary: a.treasury.beneficiary,
            mint: a.treasury.mint,
            amount,
            nonce,
            daily_spent: a.treasury.daily_spent,
            lifetime_spent: a.treasury.lifetime_spent,
        });
        Ok(())
    }

    pub fn withdraw(ctx: Context<OwnerVault>, amount: u64) -> Result<()> {
        require!(amount > 0, TreasuryError::InvalidAmount);
        let a = &ctx.accounts;
        transfer_from_vault(
            &a.treasury,
            &a.vault,
            &a.mint,
            a.owner_token.to_account_info(),
            &a.token_program,
            amount,
        )?;
        emit!(TreasuryWithdrawal {
            treasury: a.treasury.key(),
            owner: a.owner.key(),
            amount
        });
        Ok(())
    }

    /// Owner replaces caps and expiry. Accrued usage is kept, so lowering a
    /// cap below current usage simply blocks spends until usage decays.
    pub fn update_policy(ctx: Context<OwnerAction>, params: PolicyParams) -> Result<()> {
        params.validate(Clock::get()?.unix_timestamp)?;
        let t = &mut ctx.accounts.treasury;
        t.per_tx_cap = params.per_tx_cap;
        t.daily_cap = params.daily_cap;
        t.lifetime_cap = params.lifetime_cap;
        t.expires_at = params.expires_at;
        emit!(PolicyUpdated {
            treasury: t.key(),
            params
        });
        Ok(())
    }

    /// Owner replaces the agent key. This also clears `revoked`, since a
    /// revocation is of the old agent key; `paused` is left unchanged.
    pub fn rotate_agent(ctx: Context<OwnerAction>, new_agent: Pubkey) -> Result<()> {
        let t = &mut ctx.accounts.treasury;
        validate_agent(&new_agent, &t.owner, &t.beneficiary, t.guardian)?;
        let old_agent = t.agent;
        t.agent = new_agent;
        t.revoked = false;
        emit!(AgentRotated {
            treasury: t.key(),
            old_agent,
            new_agent
        });
        Ok(())
    }

    pub fn set_guardian(ctx: Context<OwnerAction>, guardian: Option<Pubkey>) -> Result<()> {
        let t = &mut ctx.accounts.treasury;
        require!(guardian != Some(t.agent), TreasuryError::InvalidAuthority);
        t.guardian = guardian;
        emit!(GuardianSet {
            treasury: t.key(),
            guardian
        });
        Ok(())
    }

    /// Owner or guardian: temporarily stop agent spends.
    pub fn pause(ctx: Context<GuardianAction>) -> Result<()> {
        ctx.accounts.treasury.paused = true;
        emit!(TreasuryPaused {
            treasury: ctx.accounts.treasury.key(),
            by: ctx.accounts.authority.key()
        });
        Ok(())
    }

    /// Owner only.
    pub fn unpause(ctx: Context<OwnerAction>) -> Result<()> {
        ctx.accounts.treasury.paused = false;
        emit!(TreasuryUnpaused {
            treasury: ctx.accounts.treasury.key()
        });
        Ok(())
    }

    /// Owner or guardian: revoke the current agent key (undo via rotate_agent).
    pub fn revoke(ctx: Context<GuardianAction>) -> Result<()> {
        ctx.accounts.treasury.revoked = true;
        emit!(TreasuryRevoked {
            treasury: ctx.accounts.treasury.key(),
            by: ctx.accounts.authority.key()
        });
        Ok(())
    }

    /// Owner only: drain the vault to the owner, close the vault token account
    /// and the treasury, and return all rent to the owner.
    pub fn close(ctx: Context<Close>) -> Result<()> {
        let a = &ctx.accounts;
        let remaining = a.vault.amount;
        if remaining > 0 {
            transfer_from_vault(
                &a.treasury,
                &a.vault,
                &a.mint,
                a.owner_token.to_account_info(),
                &a.token_program,
                remaining,
            )?;
        }
        let seed_id = a.treasury.seed_id.to_le_bytes();
        let bump = [a.treasury.bump];
        let seeds = treasury_signer_seeds(&a.treasury.owner, &a.treasury.mint, &seed_id, &bump);
        token::close_account(CpiContext::new_with_signer(
            a.token_program.to_account_info(),
            CloseAccount {
                account: a.vault.to_account_info(),
                destination: a.owner.to_account_info(),
                authority: a.treasury.to_account_info(),
            },
            &[&seeds],
        ))?;
        emit!(TreasuryClosed {
            treasury: a.treasury.key(),
            owner: a.owner.key(),
            drained: remaining
        });
        Ok(())
    }
}

#[derive(Accounts)]
#[instruction(seed_id: u64)]
pub struct Initialize<'info> {
    #[account(mut)]
    pub owner: Signer<'info>,
    /// CHECK: stored as a public key; must sign every spend.
    pub agent: UncheckedAccount<'info>,
    /// CHECK: stored as a public key; spends go only to its token account for `mint`.
    pub beneficiary: UncheckedAccount<'info>,
    pub mint: Account<'info, Mint>,
    #[account(
        init,
        payer = owner,
        space = 8 + Treasury::INIT_SPACE,
        seeds = [TREASURY_SEED, owner.key().as_ref(), mint.key().as_ref(), &seed_id.to_le_bytes()],
        bump
    )]
    pub treasury: Account<'info, Treasury>,
    #[account(
        init,
        payer = owner,
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
    pub owner: Signer<'info>,
    #[account(
        seeds = [TREASURY_SEED, treasury.owner.as_ref(), treasury.mint.as_ref(), &treasury.seed_id.to_le_bytes()],
        bump = treasury.bump,
        has_one = owner,
        has_one = mint
    )]
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
    pub agent: Signer<'info>,
    #[account(
        mut,
        seeds = [TREASURY_SEED, treasury.owner.as_ref(), treasury.mint.as_ref(), &treasury.seed_id.to_le_bytes()],
        bump = treasury.bump,
        has_one = agent,
        has_one = mint
    )]
    pub treasury: Account<'info, Treasury>,
    pub mint: Account<'info, Mint>,
    #[account(mut, associated_token::mint = mint, associated_token::authority = treasury)]
    pub vault: Account<'info, TokenAccount>,
    #[account(mut, token::mint = mint, token::authority = treasury.beneficiary)]
    pub beneficiary_token: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
}

/// Owner moves funds out of the vault (withdraw).
#[derive(Accounts)]
pub struct OwnerVault<'info> {
    pub owner: Signer<'info>,
    #[account(
        seeds = [TREASURY_SEED, treasury.owner.as_ref(), treasury.mint.as_ref(), &treasury.seed_id.to_le_bytes()],
        bump = treasury.bump,
        has_one = owner,
        has_one = mint
    )]
    pub treasury: Account<'info, Treasury>,
    pub mint: Account<'info, Mint>,
    #[account(mut, associated_token::mint = mint, associated_token::authority = treasury)]
    pub vault: Account<'info, TokenAccount>,
    #[account(mut, token::mint = mint, token::authority = owner)]
    pub owner_token: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct OwnerAction<'info> {
    pub owner: Signer<'info>,
    #[account(
        mut,
        seeds = [TREASURY_SEED, treasury.owner.as_ref(), treasury.mint.as_ref(), &treasury.seed_id.to_le_bytes()],
        bump = treasury.bump,
        has_one = owner
    )]
    pub treasury: Account<'info, Treasury>,
}

#[derive(Accounts)]
pub struct GuardianAction<'info> {
    #[account(
        constraint = authority.key() == treasury.owner
            || Some(authority.key()) == treasury.guardian @ TreasuryError::Unauthorized
    )]
    pub authority: Signer<'info>,
    #[account(
        mut,
        seeds = [TREASURY_SEED, treasury.owner.as_ref(), treasury.mint.as_ref(), &treasury.seed_id.to_le_bytes()],
        bump = treasury.bump
    )]
    pub treasury: Account<'info, Treasury>,
}

#[derive(Accounts)]
pub struct Close<'info> {
    #[account(mut)]
    pub owner: Signer<'info>,
    #[account(
        mut,
        close = owner,
        seeds = [TREASURY_SEED, treasury.owner.as_ref(), treasury.mint.as_ref(), &treasury.seed_id.to_le_bytes()],
        bump = treasury.bump,
        has_one = owner,
        has_one = mint
    )]
    pub treasury: Account<'info, Treasury>,
    pub mint: Account<'info, Mint>,
    #[account(mut, associated_token::mint = mint, associated_token::authority = treasury)]
    pub vault: Account<'info, TokenAccount>,
    #[account(mut, token::mint = mint, token::authority = owner)]
    pub owner_token: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
}

#[event]
pub struct TreasuryCreated {
    pub treasury: Pubkey,
    pub owner: Pubkey,
    pub agent: Pubkey,
    pub beneficiary: Pubkey,
    pub mint: Pubkey,
    pub seed_id: u64,
    pub guardian: Option<Pubkey>,
}
#[event]
pub struct TreasuryDeposit {
    pub treasury: Pubkey,
    pub amount: u64,
}
#[event]
pub struct TreasurySpend {
    pub treasury: Pubkey,
    pub agent: Pubkey,
    pub beneficiary: Pubkey,
    pub mint: Pubkey,
    pub amount: u64,
    pub nonce: u64,
    pub daily_spent: u64,
    pub lifetime_spent: u64,
}
#[event]
pub struct TreasuryWithdrawal {
    pub treasury: Pubkey,
    pub owner: Pubkey,
    pub amount: u64,
}
#[event]
pub struct PolicyUpdated {
    pub treasury: Pubkey,
    pub params: PolicyParams,
}
#[event]
pub struct AgentRotated {
    pub treasury: Pubkey,
    pub old_agent: Pubkey,
    pub new_agent: Pubkey,
}
#[event]
pub struct GuardianSet {
    pub treasury: Pubkey,
    pub guardian: Option<Pubkey>,
}
#[event]
pub struct TreasuryPaused {
    pub treasury: Pubkey,
    pub by: Pubkey,
}
#[event]
pub struct TreasuryUnpaused {
    pub treasury: Pubkey,
}
#[event]
pub struct TreasuryRevoked {
    pub treasury: Pubkey,
    pub by: Pubkey,
}
#[event]
pub struct TreasuryClosed {
    pub treasury: Pubkey,
    pub owner: Pubkey,
    pub drained: u64,
}
