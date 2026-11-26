//! Mint acceptance policy (review finding M1).
//!
//! A mint with a freeze authority lets that authority freeze the vault. Such
//! mints are only accepted when explicitly allow-listed (USDC has a freeze
//! authority held by Circle, so it must be listed to be usable). With the
//! `allowlist-only` cargo feature, only allow-listed mints are accepted at all.
//!
//! Token-2022 mints are rejected structurally: accounts are typed against the
//! classic SPL Token program (`anchor_spl::token`).
use anchor_lang::prelude::*;

/// Edit this list (and rebuild) to configure accepted freezable mints.
pub const ALLOWED_MINTS: &[Pubkey] = &[
    // USDC (mainnet-beta) EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
    Pubkey::new_from_array([
        198, 250, 122, 243, 190, 219, 173, 58, 61, 101, 243, 106, 171, 201, 116, 49, 177, 187, 228,
        194, 210, 246, 224, 228, 124, 166, 2, 3, 69, 47, 93, 97,
    ]),
    // USDC (devnet, Circle) 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU
    Pubkey::new_from_array([
        59, 68, 44, 179, 145, 33, 87, 241, 58, 147, 61, 1, 52, 40, 45, 3, 43, 95, 254, 205, 1, 162,
        219, 241, 183, 121, 6, 8, 223, 0, 46, 167,
    ]),
];

pub fn is_mint_allowed(mint: &Pubkey, has_freeze_authority: bool) -> bool {
    let listed = ALLOWED_MINTS.contains(mint);
    if cfg!(feature = "allowlist-only") {
        listed
    } else {
        listed || !has_freeze_authority
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn allowlist_bytes_match_documented_addresses() {
        assert_eq!(
            ALLOWED_MINTS[0].to_string(),
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        );
        assert_eq!(
            ALLOWED_MINTS[1].to_string(),
            "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"
        );
    }

    #[test]
    fn usdc_allowed_even_with_freeze_authority() {
        assert!(is_mint_allowed(&ALLOWED_MINTS[0], true));
    }

    #[test]
    #[cfg(not(feature = "allowlist-only"))]
    fn unlisted_mint_needs_no_freeze_authority() {
        let m = Pubkey::new_unique();
        assert!(is_mint_allowed(&m, false));
        assert!(!is_mint_allowed(&m, true));
    }
}
