const { sha256 } = require('./ledger');

function sumAccountBalances(accounts) {
  return accounts.reduce((acc, account) => {
    const key = account.currency || 'UNKNOWN';
    if (!acc[key]) acc[key] = { balance: 0, available: 0, held: 0, accounts: 0 };
    acc[key].balance += account.balance || 0;
    acc[key].available += account.available || 0;
    acc[key].held += account.held || 0;
    acc[key].accounts += 1;
    return acc;
  }, {});
}

function reconcileSnapshot(snapshot, externalBalances = {}) {
  const accounts = snapshot && snapshot.ledger && Array.isArray(snapshot.ledger.accounts) ? snapshot.ledger.accounts : [];
  const ledgerVerification = snapshot && snapshot.ledger && snapshot.ledger.verification ? snapshot.ledger.verification : { ok: false, reason: 'missing_ledger_verification' };
  const ledgerTotals = sumAccountBalances(accounts);
  const exceptions = [];

  for (const [currency, totals] of Object.entries(ledgerTotals)) {
    const external = externalBalances[currency];
    if (typeof external === 'number' && external !== totals.balance) {
      exceptions.push({ type: 'external_balance_mismatch', currency, ledgerBalance: totals.balance, externalBalance: external, delta: totals.balance - external });
    }
    if (totals.balance !== totals.available + totals.held) {
      exceptions.push({ type: 'available_plus_held_mismatch', currency, totals });
    }
  }

  if (!ledgerVerification.ok) {
    exceptions.push({ type: 'ledger_hash_chain_failed', verification: ledgerVerification });
  }

  const report = {
    schema: 'parallax-reconciliation-report-v0.2',
    generatedAt: new Date().toISOString(),
    ledgerVerification,
    ledgerTotals,
    externalBalances,
    exceptions,
    ok: exceptions.length === 0
  };
  report.reportHash = sha256(report);
  return report;
}

module.exports = { reconcileSnapshot, sumAccountBalances };
