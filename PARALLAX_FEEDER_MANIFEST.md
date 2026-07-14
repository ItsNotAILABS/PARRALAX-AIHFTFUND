# PARALLAX Feeder Manifest

This repository feeds the PARALLAX authority repo:

```text
ItsNotAILABS/PARALLAX-Exchange-Clearinghouse
```

## Lane

```text
hft_signal_and_strategy
```

## What this repo may feed

- paper trading signal schemas,
- HFT signal approval requirements,
- strategy research notes,
- paper/testnet backtest receipts,
- demo broker adapter requirements,
- risk and latency constraints for paper/testnet execution.

## What this repo must not feed

- live HFT execution claims,
- autonomous live broker routing,
- custody or brokerage credential material,
- unsupported fund performance claims,
- live money movement instructions,
- production exchange or mainnet bridge claims.

## PARALLAX target surfaces

- AI Execution,
- Trade,
- Native Interface,
- Proof Room,
- Agent Execution Protocol.

## Promotion rule

A signal, strategy, benchmark, or adapter requirement from this repo becomes PARALLAX authority only after:

1. source commit or artifact hash is recorded,
2. private/public boundary is assigned,
3. paper/testnet/live boundary is checked,
4. proof or receipt expectation is mapped,
5. explicit integration PR is opened in `PARALLAX-Exchange-Clearinghouse`.

## Current boundary

This feeder is **paper/testnet-first**. It may support paper trading demos and HFT signal approval loops, but it must not enable live execution in PARALLAX alpha.
