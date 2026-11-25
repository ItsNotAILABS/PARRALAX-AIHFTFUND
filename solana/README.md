# PARRALAX Agent Treasury — Solana-native program source

**SOURCE ONLY / UNDEPLOYED / UNAUDITED.** Rust/Anchor 0.30.1 implementation for an SPL token vault controlled by a PDA. The `declare_id!` is deliberately a placeholder: never deploy without changing it and recording the on-chain program ID, transactions, upgrade authority, reproducible build and review receipts.

## Mechanism
- Owner signs initialize and deposit; treasury and vault are PDA/ATA accounts.
- Owner sets a fixed agent signer, one recipient, token mint, per-tx/day/lifetime caps, and expiry.
- Agent signs each spend. A transfer_checked CPI moves the token on-chain; the PDA enforces caps and a monotonic nonce.
- The owner can revoke future agent spending and withdraw vault funds. An agent cannot change caps or destination.
- USDC requires mint selection and verification at wallet creation; this program accepts an explicit SPL mint, not a claim that every SPL token is stable.
- The v1 beneficiary is single-recipient by design. Open separate treasuries per agent and recipient rather than using unrestricted destinations.

## Production gates
1. Replace placeholder program ID; verify Anchor compile, SBF build and devnet tests with actual validator.
2. Fuzz arithmetic, nonce replay, CPI account spoofing, PDA/ATA ownership, midnight/day-window expiry, revocation, insufficient vault balance and failed transaction rollback.
3. Add wallet-side transaction review and independent simulation. No secret keys stored in Senda localStorage.
4. Fund only limited isolated test vaults after security review. Make rent, fees, costs and recovery visible.
5. Integrate Senda client & PARRALAX tenant-auth budget registry, with the on-chain cap as the hard guard.
6. Support configurable multisig owner, emergency pause and upgrade authority governance before production funds.
7. Published signature != settled transaction. Verify on-chain commitment and balances, then reconcile to PARRALAX receipts.

## Explicit limitations
Not a bank, custody provider, credit facility, merchant processor, autonomous AI model, supported issuer, or guarantee against malicious agent spend inside the permitted cap. The agent's signing key remains sensitive and must live in a secure isolated signer with strong tenant controls; it is never returned to a model prompt.
