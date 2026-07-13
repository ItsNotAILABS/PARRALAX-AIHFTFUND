# PARALLAX HFT Agentic Platform Alignment

**Repo:** `ItsNotAILABS/PARRALAX-AIHFTFUND`  
**Runtime agent:** `parallax-hft-fund-agent` / `NOVA-HFT`  
**Platform role:** agentic trading research, strategy simulation, paper/testnet execution proposal, market-data/benchmark lane.

## Why this exists

PARALLAX is being consolidated into a multi-repo agentic platform. This repository should not drift into unsupported live-fund or live-broker language. It should act as the **agentic trading and strategy runtime** that proposes work to the canonical Clearinghouse lane and can later receive governance state from the SNS/token lane.

## Three-agent map

| Agent | Repo | Responsibility |
|---|---|---|
| `parallax-clearinghouse-agent` | `PARALLAX-Exchange-Clearinghouse` | settlement, proof room, runtime tokenomics, receipt source of truth |
| `parallax-hft-fund-agent` | `PARRALAX-AIHFTFUND` | strategy, signal, benchmark, market-data, paper/testnet proposal lane |
| `sns-token-governor-agent` | `SNS---TOKEN` | SNS/ICP governance, voting, upgrade posture, token-law boundary |

## HFT runtime loop

```text
market data / strategy signal
-> HFT agent risk precheck
-> paper/testnet proposal
-> benchmark and compute receipt
-> Clearinghouse settlement/proof decision
-> optional SNS governance record when policy requires it
```

## Tokenomics alignment

The HFT lane may consume or record internal accounting units only:

- `PXGPU`: compute budget / simulation usage
- `PXNOVA`: local orchestration cycle accounting
- `PXBYTE`: measured artifact/output byte accounting
- `PXAI`: agent work/research credit
- `PXRCPT`: receipt/proof event accounting
- `PXCRED`: internal receipt credit after Clearinghouse acceptance

None of these should be represented as public money, yield, security, wage, external hardware entitlement, fund share, or redeemable asset.

## Production boundary

This repo can become a serious agentic trading platform while still keeping a hard boundary:

- paper/testnet first
- human/operator gates where required
- no live broker routing until audited and explicitly enabled
- no custody/private-key handling
- no regulated fund, adviser, broker, exchange, bank, or money-transmitter claim
- no autonomous live trading claim

## Next implementation target

Create an executable adapter that converts `strategy_signal` into a signed/hashed `paper_order_request` and forwards it to the Clearinghouse agent for policy evaluation and receipt-backed accounting.
