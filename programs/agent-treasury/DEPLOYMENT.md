# Agent Treasury — deployment and verification runbook

**Unexecuted runbook, not a release receipt.** Do not deploy a System Program placeholder or fund mainnet from this source without audit.

## Local validation
1. Install the verified Solana CLI, Rust, Anchor CLI **0.30.1**, Node >=20, npm.
2. `solana config set --url localhost`; start `solana-test-validator --reset` in a dedicated terminal.
3. From `programs/agent-treasury/`, generate a *new local-only program key*: `solana-keygen new --no-bip39-passphrase --outfile target/deploy/parralax_agent_treasury-keypair.json`.
4. Record the public address with `solana-keygen pubkey target/deploy/parralax_agent_treasury-keypair.json`. Replace placeholder IDs in `src/lib.rs` and `Anchor.toml` with that exact address. Do not commit the deploy keypair or place it under a browser bundle.
5. `anchor build` and `anchor deploy --provider.cluster localnet`. Verify program account owner, executable state, correct program ID and upgrade authority with Solana CLI.
6. `npm install`; `npm run test:localnet`. Collect **actual** validator signatures, account deltas, and transaction logs. Run source check with `npm run test:source`.
7. Repeat tests for invalid token account, wrong beneficiary, forged agent, expired vault, wrong mint, vault drained, wrong nonce, over-budget, rolled day, and failed CPI rollback. Audit before any outside funding.

## Devnet
- Create a **separate** devnet program keypair; never reuse local program key or program ID without deliberate governance.
- Use dedicated devnet owner and agent wallets holding only airdropped SOL and an explicitly tagged test mint. Do not use real USDC or mainnet private keys.
- Deploy with `anchor deploy --provider.cluster devnet`; verify address, IDL, account owners, executable flag, upgrade authority and program data.
- Run the integration flow with devnet balances and store transaction signatures in a signed `receipts/devnet.json` manifest that explicitly lists network, program ID, mint, owner, agent, beneficiary, policy and post-transaction account balances.
- No staged source code, test mock or returned signature alone proves confirmation. Check transaction status and token balances independently.

## Funding and governance
- Owner wallet signs creation and funding.
- Agent wallet only signs a fixed-recipient payment bounded by hard cap/expiry/nonce; isolate agent signing service.
- PARRALAX server authenticates agent/workspace, checks durable off-chain policy, logs an immutable request; on-chain program is the final fund movement guard.
- Owner retains withdrawal/revocation. Document whether multisig governance, emergency freeze, upgrade locks and recovery are enabled before mainnet.

## Release status
`NODE`, `cargo`, `anchor`, and `solana` were not all available in the authoring runtime. GitHub source updates completed, but Rust compilation, local validator tests, devnet transaction, security audit and production deployment **have not run**.
