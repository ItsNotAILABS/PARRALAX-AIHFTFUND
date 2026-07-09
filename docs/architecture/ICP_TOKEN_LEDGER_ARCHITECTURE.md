# ICP Token and Ledger Architecture

Status: architecture scaffold, not deployment proof  
Scope: ICP-first token, ledger, payment, entitlement, receipt, and canister-boundary plan for PARRALAX.

## 1. Core Position

PARRALAX should become real on ICP by using standards-based ledgers and canister-owned authority, not by inventing a custom token ledger first.

This document does not claim that a PARRALAX token is deployed. It defines how tokens, ledgers, wallet flows, and receipts should be built and verified before deployment.

## 2. Token Standard Posture

| Standard | Role in PARRALAX | Activation stage |
| --- | --- | --- |
| ICRC-1 | Fungible token balances, transfers, metadata, fees. | Required for local/test ledger. |
| ICRC-2 | Approvals and transfer-from flows for subscriptions, fees, and controlled payments. | Required for wallet/payment slice. |
| ICRC-3 | Transaction log, archive/index compatibility, auditability. | Required before external proof claims. |
| ICRC-21 | Consent-message support for safer wallet UX. | Strongly recommended before public wallet flows. |
| ICRC-7 | NFT receipts, access passes, strategy licenses, non-financial certificates. | Optional after receipt model is stable. |
| ICRC-37 | NFT approvals and transfer-from. | Optional only if secondary transfer/delegation is needed. |

## 3. Token Classes

| Token class | Example | Allowed in v0? | Boundary |
| --- | --- | --- | --- |
| Payment asset | ICP, ckBTC, ckETH, ckUSDC-style asset | Read/test only unless ledger is configured | Use existing trusted ledgers first. |
| Local test PARRALAX token | `PXLX_TEST` | Yes, local/testnet only | No public value, no fund/share claim. |
| Utility/access token | Platform access, API credits | Later | Must avoid investment/yield language. |
| Receipt NFT | Access certificate, compute receipt, strategy license | Later | Non-financial proof/access only. |
| Fund/share/security token | Fund ownership, profits, yield, managed exposure | No | Requires legal/compliance/custody gating. |

## 4. Canister Boundary Map

| Canister | Owns | Must not own |
| --- | --- | --- |
| `parralax_core` | Supported ledgers, product config, version gates, system mode. | Raw off-chain trading compute. |
| `parralax_identity_access` | Principals, roles, consent records, KYC status pointer. | Private KYC files unless explicitly designed. |
| `parralax_subscription` | ICRC-2 allowance checks, payment receipts, service entitlement. | Custom token balances. |
| `parralax_job_ledger` | Strategy job envelopes, proof hashes, simulation report status. | Unverifiable performance claims. |
| `parralax_vault_router` | Deposit subaccount mapping, withdrawal request state, treasury policy. | Unregulated custody or unmanaged fund assets. |
| `parralax_proof_oracle` | Off-chain result hashes, benchmark hashes, provenance records. | Off-chain model execution. |
| `pxlx_ledger` | Optional local/test ICRC-1/2/3 token ledger. | Fund-share semantics. |
| `parralax_receipt_nft` | Optional ICRC-7/37 receipt/access NFTs. | Yield or profit promises. |

## 5. First Buildable ICP Slice

Name: `parralax_icp_access_receipt_v0`

Flow:

1. User authenticates with Internet Identity.
2. Frontend reads supported payment ledger from `parralax_core`.
3. User grants bounded ICRC-2 allowance to `parralax_subscription`.
4. `parralax_subscription` calls `transfer_from` on a local/test ICRC ledger.
5. Payment receipt is recorded with block index, token canister id, principal, amount, and timestamp.
6. `parralax_job_ledger` opens a strategy-access job envelope.
7. Off-chain/simulation engine returns a simulated strategy report hash.
8. `parralax_job_ledger` records result hash and provenance hash.
9. User can query entitlement, payment receipt, and report proof.
10. Tests reject duplicate payment, replay, expired allowance, wrong caller, and wrong ledger id.

## 6. Candid Contract Sketch

```did
// parralax_core
service : {
  get_supported_ledgers : () -> (vec SupportedLedger) query;
  get_system_mode : () -> (SystemMode) query;
  set_system_mode : (SystemMode, text) -> (GovernanceDecision);
}

// parralax_subscription
service : {
  quote_access : (AccessQuoteRequest) -> (AccessQuote) query;
  purchase_access : (AccessPurchaseCommand) -> (AccessReceipt);
  get_entitlement : (principal) -> (opt Entitlement) query;
  get_payment_receipts : (principal, nat) -> (vec AccessReceipt) query;
}

// parralax_job_ledger
service : {
  open_job : (JobOpenCommand) -> (JobEnvelope);
  record_job_result_hash : (JobResultCommand) -> (JobReceipt);
  get_job : (text) -> (opt JobEnvelope) query;
}
```

## 7. Test Matrix

| Area | Required test |
| --- | --- |
| Ledger config | Unknown ledger id is rejected. |
| Allowance | Expired or insufficient allowance fails before entitlement is granted. |
| Idempotency | Duplicate purchase command returns original receipt. |
| Replay | Replayed transfer block cannot mint duplicate entitlement. |
| Authority | Non-admin cannot change supported ledger list. |
| Proof | Job result hash cannot be overwritten without append-only correction receipt. |
| Mode gate | Live/fund/security token mode remains disabled until compliance gate is complete. |

## 8. Deployment Posture

| Stage | What can happen | What cannot happen |
| --- | --- | --- |
| Local | Deploy local ICRC test ledger and PARRALAX canisters. | Public token claims. |
| Testnet/public canister | Test payments, entitlements, receipts, simulated reports. | Fund/share/yield token issuance. |
| Closed alpha | Controlled users, bounded test assets, proof export. | Third-party capital management. |
| Regulated launch candidate | Only after legal, custody, compliance, and security review. | Ungated live trading or public investment language. |

## 9. Monitor Next

The next code artifact should scaffold `parralax_core`, `parralax_subscription`, and `parralax_job_ledger` around local/test ICRC flows, then wire the Control Tower frontend to read ledgers, quote access, purchase access, and display receipts.
