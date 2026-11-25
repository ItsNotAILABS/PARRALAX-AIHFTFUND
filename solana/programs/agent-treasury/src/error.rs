use anchor_lang::prelude::*;

/// Custom program errors. Codes are 6000 + declaration index; append new
/// variants at the end so existing client error codes stay stable.
#[error_code]
pub enum TreasuryError {
    #[msg("Owner, agent, beneficiary and guardian must be distinct where required")]
    InvalidAuthority, // 6000
    #[msg("Invalid spending caps: require 0 < per_tx <= daily <= lifetime")]
    InvalidCaps, // 6001
    #[msg("Treasury expired")]
    Expired, // 6002
    #[msg("Treasury revoked")]
    Revoked, // 6003
    #[msg("Invalid amount")]
    InvalidAmount, // 6004
    #[msg("Per-transaction limit reached")]
    PerTransactionLimit, // 6005
    #[msg("Daily limit reached")]
    DailyLimit, // 6006
    #[msg("Lifetime limit reached")]
    LifetimeLimit, // 6007
    #[msg("Invalid replay nonce")]
    InvalidNonce, // 6008
    #[msg("Arithmetic overflow")]
    Overflow, // 6009
    #[msg("Treasury paused")]
    Paused, // 6010 (was ClockRegression; the clock is now clamped instead)
    #[msg("Signer is not the owner or guardian")]
    Unauthorized, // 6011
    #[msg("Mint is not allowed: it has a freeze authority and is not allow-listed")]
    MintNotAllowed, // 6012
    #[msg("Expiry must be in the future")]
    InvalidExpiry, // 6013
}
