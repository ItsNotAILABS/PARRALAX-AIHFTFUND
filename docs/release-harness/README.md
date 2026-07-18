# PARRALAX AIHFT Ecosystem Release Harness

This harness turns `ItsNotAILABS/PARRALAX-AIHFTFUND` into a research/backtest production-feeder repo for the NOVA model-family root.

## Purpose

The repo feeds strategy research, wallet boundaries, sandbox ledgers, receipts, backtest evidence, and operator-controlled trading-readiness gates into NOVA.

## Release package

- `docs/release-harness/release-packages/v1.0.0/RELEASE.md`
- `docs/release-harness/release-packages/v1.0.0/release-manifest.json`

## Model

- PARALLAX AIHFT Research Model: strategy evaluation, sandbox wallet boundaries, receipts, and research-only release promotion.

## Required evidence

- model card
- research-backtest schema
- feeder schema
- release manifest
- validator script
- GitHub Actions harness

## Promotion gates

1. CI success.
2. Operator approval.
3. Strategy/backtest receipts.
4. Demo/sandbox evidence before any live bridge.
5. Explicit approval before any trading integration.

## Boundaries

- research backtest only
- no live trading authority
- no investment advice
- no custody claim
- no performance guarantee
- no capital deployment without operator approval
