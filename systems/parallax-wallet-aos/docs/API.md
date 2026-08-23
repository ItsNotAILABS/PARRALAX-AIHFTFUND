# PARALLAX Wallet AOS API

Start server:

```bash
npm run server
```

Default base URL:

```text
http://127.0.0.1:8799
```

## GET /health

Returns service status.

## GET /interfaces

Returns the ACYILA interface registry.

## GET /commands

Returns AOS command names and risk metadata.

## GET /snapshot

Returns wallets, proposals, ledger state, and receipts.

## POST /execute

Generic command execution envelope.

```json
{
  "command": "wallet.create",
  "input": {
    "ownerId": "alice",
    "walletId": "wallet_alice",
    "currency": "USD",
    "kycStatus": "verified"
  }
}
```

Supported commands:

- `wallet.create`
- `wallet.creditSandbox`
- `wallet.balance`
- `transfer.propose`
- `transfer.approve`
- `transfer.settleSandbox`
- `system.snapshot`

All live rails remain blocked. The server does not expose private keys, bank credentials, exchange credentials, or direct settlement credentials.
