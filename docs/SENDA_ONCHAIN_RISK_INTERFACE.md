# PARRALAX -> Senda Solana utility risk interface

Status: DESIGN CONTRACT ONLY. No deployed adapter, oracle or active trade authorization is claimed.

## Separation of concerns
- Senda owns wallet UX, Jupiter quote/simulate/sign, user USDC transfers and position display.
- PARRALAX owns off-chain market evidence, risk scoring, limit proposals, governance receipts and agent recommendations.
- On-chain Solana programs alone enforce USDC escrow movement, signer constraints, replay protection, revocation and immutable conditions; PARRALAX risk output is never a substitute for an on-chain proof.

## Proposed signed risk-decision schema
```json
{
  "version": 1,
  "market_id": "<verified mint or market identifier>",
  "source_id": "<approved oracle/feed identifier>",
  "observed_slot": 0,
  "observed_at": 0,
  "price_exponent": 0,
  "price_mantissa": 0,
  "confidence_mantissa": 0,
  "eligible": false,
  "max_cover_atoms": 0,
  "max_agent_budget_atoms": 0,
  "max_ltv_bps": 0,
  "valid_until": 0,
  "evidence_hash": "<sha256 digest>",
  "authority_scope": "<wallet/mission>"
}
```
All numeric fields are examples of *types*; zero is a fail-closed default, not evidence of a live feed.

## Governance gates
- Proposal and simulation are not execution. Only the wallet may approve a new authority.
- A risk decision must be bound to wallet/mission, market, nonce, expiry and exact budget; no user approval may be widened by an agent.
- Enforce feed whitelists and staleness/confidence rules; reject unsupported PreStock reference prices rather than substituting an unrelated token feed.
- Require prefunded reserves for cover payouts; PARRALAX cannot manufacture a lender or insurer balance.
- Audit trail records proposal ID, source hashes, on-chain transaction signature, status and deny reason.
- Circuit breaker must fail closed for oracle disagreement, halted markets, exhausted reserve or unavailable execution infrastructure.

## Phase ordering
A. Audit and harden Senda's terms registry.
B. Implement funded USDC conditional-release escrow and agent budget pilot, with adversarial tests.
C. Price-based, fully reserved cover after oracle/reference legitimacy and legal review.
D. Collateralized borrowing only with funded liquidity, controlled collateral escrow, liquidation tests and compliance signoff.

See corresponding Senda branch `feature/cover-program-guardrails-20261101`.
