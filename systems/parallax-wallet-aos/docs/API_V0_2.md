# PARALLAX Wallet AOS API v0.2

v0.2 keeps the v0.1 command envelope and adds operating-core endpoints.

## GET /dashboard-contract

Returns the operator dashboard contract for UI/API builders.

## POST /reconcile

Runs reconciliation against the in-memory Wallet AOS snapshot.

```json
{
  "externalBalances": {
    "USD": 200000
  }
}
```

## POST /statement

Generates a wallet statement.

```json
{
  "walletId": "wallet_alice",
  "options": {
    "from": null,
    "to": null
  }
}
```

## Existing v0.1 endpoints preserved

- `GET /health`
- `GET /interfaces`
- `GET /commands`
- `GET /snapshot`
- `POST /execute`

## Boundary

The new endpoints expose reporting, proof, and operations surfaces only. They do not activate live money movement.
