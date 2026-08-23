const crypto = require('crypto');

function sha256(value) {
  return crypto.createHash('sha256').update(typeof value === 'string' ? value : JSON.stringify(value)).digest('hex');
}

function now() {
  return new Date().toISOString();
}

class LedgerError extends Error {}

class HashChainedLedger {
  constructor() {
    this.entries = [];
    this.accounts = new Map();
    this.lastHash = 'GENESIS';
  }

  createAccount({ accountId, ownerId, currency = 'USD', accountType = 'wallet', metadata = {} }) {
    if (!accountId || !ownerId) throw new LedgerError('accountId and ownerId are required');
    if (this.accounts.has(accountId)) throw new LedgerError(`account already exists: ${accountId}`);
    const account = { accountId, ownerId, currency, accountType, balance: 0, available: 0, held: 0, metadata, createdAt: now() };
    this.accounts.set(accountId, account);
    return account;
  }

  getAccount(accountId) {
    const account = this.accounts.get(accountId);
    if (!account) throw new LedgerError(`unknown account: ${accountId}`);
    return account;
  }

  post({ debitAccountId, creditAccountId, amount, currency = 'USD', memo = '', referenceId, metadata = {} }) {
    if (!referenceId) throw new LedgerError('referenceId is required');
    if (!Number.isInteger(amount) || amount <= 0) throw new LedgerError('amount must be a positive integer in minor units');
    const debit = this.getAccount(debitAccountId);
    const credit = this.getAccount(creditAccountId);
    if (debit.currency !== currency || credit.currency !== currency) throw new LedgerError('currency mismatch');
    if (debit.available < amount) throw new LedgerError('insufficient available balance');

    debit.balance -= amount;
    debit.available -= amount;
    credit.balance += amount;
    credit.available += amount;

    const entry = {
      index: this.entries.length + 1,
      timestamp: now(),
      type: 'double_entry_transfer',
      debitAccountId,
      creditAccountId,
      amount,
      currency,
      memo,
      referenceId,
      metadata,
      previousHash: this.lastHash
    };
    entry.hash = sha256(entry);
    this.entries.push(entry);
    this.lastHash = entry.hash;
    return entry;
  }

  credit({ creditAccountId, amount, currency = 'USD', memo = 'external credit', referenceId, metadata = {} }) {
    if (!referenceId) throw new LedgerError('referenceId is required');
    if (!Number.isInteger(amount) || amount <= 0) throw new LedgerError('amount must be positive integer minor units');
    const credit = this.getAccount(creditAccountId);
    if (credit.currency !== currency) throw new LedgerError('currency mismatch');
    credit.balance += amount;
    credit.available += amount;
    const entry = { index: this.entries.length + 1, timestamp: now(), type: 'external_credit', creditAccountId, amount, currency, memo, referenceId, metadata, previousHash: this.lastHash };
    entry.hash = sha256(entry);
    this.entries.push(entry);
    this.lastHash = entry.hash;
    return entry;
  }

  hold({ accountId, amount, referenceId, memo = 'hold' }) {
    if (!Number.isInteger(amount) || amount <= 0) throw new LedgerError('amount must be positive integer minor units');
    const account = this.getAccount(accountId);
    if (account.available < amount) throw new LedgerError('insufficient available balance');
    account.available -= amount;
    account.held += amount;
    const entry = { index: this.entries.length + 1, timestamp: now(), type: 'hold', accountId, amount, currency: account.currency, referenceId, memo, previousHash: this.lastHash };
    entry.hash = sha256(entry);
    this.entries.push(entry);
    this.lastHash = entry.hash;
    return entry;
  }

  release({ accountId, amount, referenceId, memo = 'release' }) {
    const account = this.getAccount(accountId);
    if (account.held < amount) throw new LedgerError('insufficient held balance');
    account.held -= amount;
    account.available += amount;
    const entry = { index: this.entries.length + 1, timestamp: now(), type: 'release', accountId, amount, currency: account.currency, referenceId, memo, previousHash: this.lastHash };
    entry.hash = sha256(entry);
    this.entries.push(entry);
    this.lastHash = entry.hash;
    return entry;
  }

  verify() {
    let previousHash = 'GENESIS';
    for (const entry of this.entries) {
      const clone = { ...entry };
      const stored = clone.hash;
      delete clone.hash;
      if (clone.previousHash !== previousHash) return { ok: false, reason: 'broken_previous_hash', index: entry.index };
      if (sha256(clone) !== stored) return { ok: false, reason: 'entry_hash_mismatch', index: entry.index };
      previousHash = stored;
    }
    return { ok: true, entries: this.entries.length, lastHash: previousHash };
  }

  snapshot() {
    return { accounts: Array.from(this.accounts.values()), entries: this.entries, verification: this.verify() };
  }
}

module.exports = { HashChainedLedger, LedgerError, sha256 };
