# Agent Treasury: deployment and verification runbook

**Unexecuted for devnet/mainnet. Not a release receipt.** Nothing here has been
deployed outside a local validator, and the program has not been audited.

All commands run from `solana/` (the single Anchor + Cargo workspace).

## Pinned toolchain
| Tool | Version | Where pinned |
|---|---|---|
| Rust (host, tests, clippy) | 1.79.0 | `rust-toolchain.toml` |
| Rust nightly (IDL build only) | nightly-2024-11-01 | CI `IDL_NIGHTLY`; run `RUSTUP_TOOLCHAIN=nightly-2024-11-01 anchor build` |
| Solana / Agave CLI + platform-tools | 1.18.26 | `Anchor.toml [toolchain]`, CI |
| Anchor CLI / crates | 0.30.1 | `Anchor.toml`, `Cargo.toml` (`=0.30.1`), `Cargo.lock` |
| JS test deps | exact | `package.json`, `package-lock.json` |

`Cargo.lock` is committed and resolved for rustc 1.75 (the SBF platform-tools
compiler). Do not `cargo update` without re-running the full suite; several
transitive crates are deliberately held back (blake3, proc-macro2, ahash, ...).

## Local validation (reproducible)
1. Install the pinned tools above, Node >= 20 and `bzip2` (the test validator needs it).
2. `solana-keygen new --no-bip39-passphrase -o ~/.config/solana/id.json` (throwaway localnet wallet).
3. `anchor keys sync` if your `target/deploy/parralax_agent_treasury-keypair.json` differs from `declare_id!`.
4. `cargo fmt --check && cargo clippy --all-targets -- -D warnings`
5. `cargo test` (unit + native program tests)
6. `RUSTUP_TOOLCHAIN=nightly-2024-11-01 anchor build`
7. `SBF_OUT_DIR=$PWD/target/deploy cargo test --test program` (same tests against the SBF binary)
8. `npm ci && anchor test --skip-build` (end-to-end on `solana-test-validator`)

CI (`.github/workflows/agent-treasury-source-gates.yml`) runs exactly these steps.

## Hard requirements before any non-local deployment
These are release blockers, not recommendations.

1. **Upgrade authority is a multisig.** Deploy, then immediately transfer the
   upgrade authority to a Squads (or equivalent) multisig with a timelock:
   `solana program set-upgrade-authority <PROGRAM_ID> --new-upgrade-authority <MULTISIG_VAULT>`.
   A single hot key as upgrade authority can replace the program and drain every
   vault regardless of caps. Alternatively make the program immutable
   (`--final`) after audit. Record the authority in `RELEASE_STATUS.json`.
2. **Verifiable build.** Build with `anchor build --verifiable` (or
   `solana-verify build`) from a tagged commit, deploy that artifact, and publish
   the hash so anyone can check the on-chain program matches the source
   (`solana-verify verify-from-repo`).
3. **Managed program keypair.** Generate the production program keypair inside
   the release process, replace the localnet `declare_id!` and add a
   `[programs.<cluster>]` entry in the same reviewed commit. Never commit keypairs
   (`*-keypair.json` is git-ignored).
4. **Owner is a multisig** (Squads vault PDA) for any treasury holding real
   funds. The owner can withdraw everything at any time by design.
5. **Guardian configured.** Set a separate guardian key (incident responder) on
   every funded treasury so spending can be paused without the owner multisig.
6. **Production mint policy.** Build with `--features allowlist-only` and review
   `src/mint_policy.rs::ALLOWED_MINTS` (USDC mainnet/devnet).
7. **Independent security audit** of the program and this deployment process.

## Devnet
- Separate devnet program keypair and multisig; never reuse localnet keys.
- Dedicated owner/agent/guardian wallets holding only airdropped SOL and a tagged test mint.
- Verify program ID, IDL, upgrade authority, executable flag and program data hash after deploy.
- Store transaction signatures and post-transaction balances in a signed
  `receipts/devnet.json`. A returned signature alone does not prove settlement; check
  confirmation status and token balances independently.

## Operating model
- Owner (multisig): initialize, deposit, withdraw, update_policy, rotate_agent, set_guardian, unpause, close.
- Guardian: pause, revoke. Nothing else.
- Agent (isolated signer service): spend to the fixed beneficiary within caps,
  using a strictly sequential nonce. Serialize spends per treasury; on an unknown
  outcome, re-read `next_nonce` before retrying, so a retry can never pay twice.
- Off-chain PARRALAX policy is advisory; the on-chain caps are the hard guard.
- Caps are per treasury. An agent key attached to N treasuries can spend the sum
  of their caps; keep one agent key per treasury, or track aggregate exposure off-chain.
