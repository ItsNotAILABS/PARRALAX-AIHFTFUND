# PARRALAX Agent Treasury: Solana program

**SOURCE ONLY / UNDEPLOYED / UNAUDITED.** Anchor 0.30.1 program: an SPL-token
vault owned by a PDA, from which an agent key may pay one fixed beneficiary
within hard limits. See [DEPLOYMENT.md](DEPLOYMENT.md) for the build/test steps
and the release blockers.

## Layout
```
solana/
  Anchor.toml  Cargo.toml  Cargo.lock  rust-toolchain.toml  package.json
  programs/agent-treasury/src/
    lib.rs          instructions and account validation
    state.rs        Treasury account and spend accounting
    policy.rs       cap validation and decaying daily allowance (pure, unit tested)
    mint_policy.rs  accepted mints
    error.rs        error codes (6000+)
  programs/agent-treasury/tests/program.rs   program tests (solana-program-test)
  tests/*.test.mjs                           source gates + localnet end-to-end
```

## Accounts (layout v2)
`Treasury` PDA, seeds `["treasury", owner, mint, seed_id (u64 LE)]`, holds:
owner, mint, fixed beneficiary, rotatable agent, optional guardian, per-tx /
daily / lifetime caps, decaying daily usage, lifetime usage, expiry, sequential
nonce, `revoked`, `paused`. The vault is the treasury's associated token account.

v2 is a breaking change from the v1 draft: agent and beneficiary are no longer
seeds (so the agent can be rotated in place), and `seed_id` lets one owner run
several treasuries per mint. Clients (Senda instruction builder) must derive the
new PDA and pass `seed_id`, `PolicyParams` and `guardian` to `initialize`.

## Instructions
| Instruction | Signer | Effect |
|---|---|---|
| `initialize(seed_id, params, guardian)` | owner | create treasury + vault; validates caps, expiry, distinct roles, mint policy |
| `deposit(amount)` | owner | owner token account to vault |
| `spend(amount, nonce)` | agent | vault to beneficiary's token account, within caps |
| `withdraw(amount)` | owner | vault to owner, any time (also after revoke/expiry) |
| `update_policy(params)` | owner | replace caps and expiry |
| `rotate_agent(new_agent)` | owner | replace agent key; clears `revoked` |
| `set_guardian(guardian?)` | owner | set or remove guardian |
| `pause` / `revoke` | owner or guardian | stop spends (revoke is undone only by `rotate_agent`) |
| `unpause` | owner | resume spends |
| `close` | owner | drain vault to owner, close vault and treasury, refund rent |

## Spending limits
- **Per transaction**: `0 < amount <= per_tx_cap`.
- **Daily**: a leaky bucket. Usage decays linearly at `daily_cap` per 24 h. Burst is
  at most `daily_cap`. Over any period T, spending is at most `daily_cap * (1 + T/24h)`.
  The v1 fixed window allowed 2x `daily_cap` within seconds across a window boundary.
- **Lifetime**: `lifetime_spent <= lifetime_cap`. This is never reset; the owner can raise it.
- **Expiry, pause, revoke**: each blocks spends. None of them blocks owner withdrawal.
- **Nonce**: `spend` requires `nonce == next_nonce`. Solana already rejects
  replays of the same transaction. The nonce exists so an agent retrying after an
  unknown outcome (e.g. an expired blockhash) cannot pay twice. The trade-off is that
  an agent's spends on one treasury are serialized.
- **Scope**: caps are per treasury, not per agent key. See DEPLOYMENT.md.

## Mints
Mints with a freeze authority are rejected unless they are on `ALLOWED_MINTS`
(USDC mainnet and devnet). The `allowlist-only` feature accepts only listed mints.
Token-2022 mints are not supported.

## Not provided
Not a bank, custodian or payment processor. It does not guard against a
malicious agent spending within its caps. The agent key must live in an isolated
signer and is never exposed to a model prompt.
