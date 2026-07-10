# PARALLAX Money Transfer Protocol

The transfer protocol is intentionally staged.

```text
intent
  -> source wallet
  -> amount in minor units
  -> destination descriptor
  -> rail selection
  -> policy check
  -> proposal hash
  -> operator approval
  -> sandbox settlement packet
  -> receipt hash
```

## States

- `proposed`
- `approved`
- `settled_sandbox`
- future: `submitted_live`, `confirmed_live`, `failed_live`, `reversed`, `disputed`

## Rails

Current rails are sandbox-only:

- `internal_ledger_sandbox`
- `bank_wire_sandbox`
- `ach_sandbox`
- `card_sandbox`
- `crypto_sandbox`
- `icp_sandbox`

Live rails are explicitly blocked until compliance activation.
