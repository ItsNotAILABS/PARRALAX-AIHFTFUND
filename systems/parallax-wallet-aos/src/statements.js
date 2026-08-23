const { sha256 } = require('./ledger');

function accountStatement(snapshot, accountId, { from = null, to = null } = {}) {
  const account = snapshot.ledger.accounts.find(a => a.accountId === accountId);
  if (!account) throw new Error(`unknown account for statement: ${accountId}`);
  const fromTime = from ? new Date(from).getTime() : Number.NEGATIVE_INFINITY;
  const toTime = to ? new Date(to).getTime() : Number.POSITIVE_INFINITY;
  const entries = snapshot.ledger.entries.filter(entry => {
    const ts = new Date(entry.timestamp).getTime();
    const inRange = ts >= fromTime && ts <= toTime;
    const touches = entry.accountId === accountId || entry.creditAccountId === accountId || entry.debitAccountId === accountId;
    return inRange && touches;
  });

  let runningBalance = 0;
  const lines = entries.map(entry => {
    let delta = 0;
    if (entry.type === 'external_credit' && entry.creditAccountId === accountId) delta = entry.amount;
    if (entry.type === 'double_entry_transfer' && entry.creditAccountId === accountId) delta = entry.amount;
    if (entry.type === 'double_entry_transfer' && entry.debitAccountId === accountId) delta = -entry.amount;
    runningBalance += delta;
    return { timestamp: entry.timestamp, type: entry.type, referenceId: entry.referenceId, memo: entry.memo || '', amountMinor: entry.amount, deltaMinor: delta, runningBalanceMinor: runningBalance, hash: entry.hash };
  });

  const statement = {
    schema: 'parallax-account-statement-v0.2',
    generatedAt: new Date().toISOString(),
    account: { accountId: account.accountId, ownerId: account.ownerId, currency: account.currency },
    period: { from, to },
    ending: { balance: account.balance, available: account.available, held: account.held },
    lines
  };
  statement.statementHash = sha256(statement);
  return statement;
}

function walletStatement(snapshot, walletId, options = {}) {
  const wallet = snapshot.wallets.find(w => w.walletId === walletId);
  if (!wallet) throw new Error(`unknown wallet for statement: ${walletId}`);
  return accountStatement(snapshot, wallet.settlementAccountId, options);
}

module.exports = { accountStatement, walletStatement };
