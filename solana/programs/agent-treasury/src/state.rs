use anchor_lang::prelude::*;

use crate::error::TreasuryError;
use crate::policy;

pub const TREASURY_SEED: &[u8] = b"treasury";
pub const TREASURY_VERSION: u8 = 2;

/// Treasury PDA, seeds = ["treasury", owner, mint, seed_id (u64 LE)].
///
/// Layout v2 (breaking vs. v1): `agent` and `beneficiary` are no longer PDA
/// seeds, so the owner can rotate the agent key without moving funds; the
/// owner picks `seed_id` to run several treasuries per (owner, mint).
#[account]
#[derive(InitSpace)]
pub struct Treasury {
    pub version: u8,
    pub bump: u8,
    pub seed_id: u64,
    pub owner: Pubkey,
    pub mint: Pubkey,
    /// Fixed for the life of the treasury: one recipient per treasury.
    pub beneficiary: Pubkey,
    /// Spending key; owner may rotate it.
    pub agent: Pubkey,
    /// Optional emergency role: may pause and revoke, nothing else.
    pub guardian: Option<Pubkey>,
    pub per_tx_cap: u64,
    pub daily_cap: u64,
    pub lifetime_cap: u64,
    /// Decaying (leaky-bucket) daily usage; see `policy::refill`.
    pub daily_spent: u64,
    pub lifetime_spent: u64,
    pub last_refill_at: i64,
    pub expires_at: i64,
    /// Strictly sequential spend nonce: idempotency guard for agent retries.
    pub next_nonce: u64,
    pub revoked: bool,
    pub paused: bool,
}

impl Treasury {
    /// Validate and record an agent spend. All checks run before any state is
    /// written, and the caller performs the token CPI only after this succeeds.
    pub fn record_spend(&mut self, amount: u64, nonce: u64, now: i64) -> Result<()> {
        require!(!self.revoked, TreasuryError::Revoked);
        require!(!self.paused, TreasuryError::Paused);
        require!(now < self.expires_at, TreasuryError::Expired);
        require!(
            amount > 0 && amount <= self.per_tx_cap,
            TreasuryError::PerTransactionLimit
        );
        require!(nonce == self.next_nonce, TreasuryError::InvalidNonce);

        let (spent, refill_at) =
            policy::refill(self.daily_spent, self.daily_cap, self.last_refill_at, now);
        let daily = spent.checked_add(amount).ok_or(TreasuryError::Overflow)?;
        require!(daily <= self.daily_cap, TreasuryError::DailyLimit);
        let lifetime = self
            .lifetime_spent
            .checked_add(amount)
            .ok_or(TreasuryError::Overflow)?;
        require!(lifetime <= self.lifetime_cap, TreasuryError::LifetimeLimit);

        self.daily_spent = daily;
        self.last_refill_at = refill_at;
        self.lifetime_spent = lifetime;
        self.next_nonce = nonce.checked_add(1).ok_or(TreasuryError::Overflow)?;
        Ok(())
    }
}
