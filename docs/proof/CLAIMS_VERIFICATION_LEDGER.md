# Claims Verification Ledger

Status: initial proof-control ledger  
Purpose: map PARRALAX claims to implementation evidence, tests, receipts, and safe public wording.

## 1. Claim Status Legend

| Status | Meaning |
| --- | --- |
| `verified` | Evidence and test/proof exist in the repo. |
| `partially verified` | Some implementation exists, but tests or proof are incomplete. |
| `architecture` | Design exists; implementation not complete. |
| `roadmap` | Future product direction. |
| `blocked` | Requires legal, compliance, custody, security, credentials, or deployment gate. |
| `avoid public claim` | Should not be used externally until evidence changes. |

## 2. Product Claims

| Claim | Current status | Evidence/gap | Allowed wording |
| --- | --- | --- | --- |
| PARRALAX is a Control Tower for paper-first exchange/fund operations. | architecture | `docs/PRODUCT_ARCHITECTURE.md` and product docs exist. | "paper-first Control Tower architecture." |
| PARRALAX is a live AI HFT fund. | blocked | Live capital, custody, compliance, broker, audit, and deployment evidence not established. | Avoid public claim. |
| PARRALAX can support wallet, ledger, trading, and transfer flows. | architecture | `docs/product/WALLET_TRADING_TRANSFER_APP_ARCHITECTURE.md` defines flows. | "designed to support wallet, ledger, paper trading, and transfer workflows." |
| PARRALAX has real money transfer rails. | blocked | No verified provider, custody, compliance, reconciliation, or live rail evidence in this ledger. | Avoid public claim until implemented and approved. |
| PARRALAX has a proof/receipt direction. | partially verified | Existing receipt docs and new proof ledger exist; verifier implementation pending. | "receipt-oriented proof architecture." |

## 3. Token and Ledger Claims

| Claim | Current status | Evidence/gap | Allowed wording |
| --- | --- | --- | --- |
| PARRALAX has an ICP token/ledger architecture. | architecture | `docs/architecture/ICP_TOKEN_LEDGER_ARCHITECTURE.md`. | "ICP token and ledger architecture is specified." |
| PARRALAX token is deployed. | avoid public claim | No canister id, ledger config, deployment receipt, or transaction proof recorded here. | Do not claim deployed. |
| PARRALAX supports ICRC-ledger payment flows. | architecture | ICRC-1/2/3 design specified; implementation pending. | "planned standards-based ICRC ledger support." |
| PARRALAX can issue access/receipt NFTs. | roadmap | ICRC-7/37 optional architecture only. | "future receipt/access NFT option." |
| PARRALAX issues fund/share/yield tokens. | blocked | Potential securities/fund boundary. | Avoid until legal and compliance gates complete. |

## 4. Trading Claims

| Claim | Current status | Evidence/gap | Allowed wording |
| --- | --- | --- | --- |
| Paper order flow is the first vertical slice. | architecture | `docs/PRODUCT_ARCHITECTURE.md`. | "first build target is paper order -> risk gate -> receipt." |
| Live broker execution is ready. | blocked | Broker credentials, sandbox tests, risk gates, reconciliation, legal review absent from this ledger. | Avoid public claim. |
| HFT execution is production-grade. | avoid public claim | Needs benchmarks, market simulator, latency evidence, exchange adapter proof. | Use only as roadmap until proven. |
| Risk gates are required before execution. | architecture | Risk docs and product docs specify gate. | "risk-gated architecture." |

## 5. Wallet and Transfer Claims

| Claim | Current status | Evidence/gap | Allowed wording |
| --- | --- | --- | --- |
| Wallet UI can be designed now. | architecture | Product architecture defines surfaces. | "wallet surface architecture." |
| Internal paper transfers are first money-runtime slice. | architecture | Product architecture defines ledger proof flow. | "planned internal paper transfer slice." |
| External crypto/bank transfers are live. | blocked | Provider integrations, custody, compliance, and reconciliation not verified. | Avoid public claim. |
| Multi-ledger reconciliation is part of the design. | architecture | Product architecture defines reconciliation module. | "multi-ledger reconciliation design." |

## 6. CI/Test Claims

| Claim | Current status | Evidence/gap | Allowed wording |
| --- | --- | --- | --- |
| CI workflow parses and can run. | partially verified | This branch repairs malformed `ci.yml`; must be verified by GitHub Actions. | "CI syntax repair submitted." |
| Frontend typecheck is fixed. | partially verified | Missing `quantitative` module and actor hook compatibility patched; further generated-backend drift may remain. | "frontend compatibility fixes submitted." |
| Motoko backend typecheck passes. | unknown | Backend job failure details require authenticated logs or rerun. | Do not claim passing until Actions verify. |
| Webpack workflow is aligned with app stack. | partially verified | `webpack.yml` replaced with pnpm/Vite frontend checks. | "legacy webpack workflow replaced with frontend compatibility build." |

## 7. Evidence Required For Promotion

| Promotion | Required evidence |
| --- | --- |
| Public product paper | Claims ledger rows marked verified/architecture with safe wording. |
| Token announcement | Ledger canister id, deployment commit, ICRC metadata, transaction proof, compliance approval. |
| Wallet launch | Idempotency, double-entry ledger, receipt chain, reconciliation, security review. |
| Trading launch | Paper tests, risk gates, order receipts, benchmark pack, sandbox broker proof. |
| Live money movement | Legal/compliance approval, custody model, provider contracts, security review, incident plan. |
| Production-grade claim | Passing CI, benchmark matrix, chaos tests, proof pack, release readiness packet. |

## 8. Monitor Next

After GitHub Actions runs on this branch, update the CI/Test claims with the actual results. Do not upgrade any claim to `verified` until the linked evidence is visible.
