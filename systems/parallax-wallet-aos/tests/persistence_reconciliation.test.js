const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { WalletOS } = require('../src/wallet');
const { JsonVault } = require('../src/storage');
const { reconcileSnapshot } = require('../src/reconciliation');
const { walletStatement } = require('../src/statements');
const { TreasuryRoles } = require('../src/roles');
const { dashboardContract } = require('../src/dashboard_contract');

function buildSnapshot() {
  const walletOS = new WalletOS();
  const alice = walletOS.createWallet({ ownerId: 'alice', walletId: 'wallet_alice_v02', kycStatus: 'verified' });
  const bob = walletOS.createWallet({ ownerId: 'bob', walletId: 'wallet_bob_v02', kycStatus: 'verified' });
  walletOS.creditSandbox({ walletId: alice.walletId, amountMinor: 200000, memo: 'v0.2 test funding' });
  const proposal = walletOS.proposeTransfer({
    sourceWalletId: alice.walletId,
    destination: { walletId: bob.walletId },
    amountMinor: 75000,
    currency: 'USD',
    rail: 'internal_ledger_sandbox',
    memo: 'v0.2 transfer'
  });
  walletOS.approveTransfer({ proposalId: proposal.proposalId, operatorId: 'operator_one' });
  walletOS.settleTransfer({ proposalId: proposal.proposalId });
  return walletOS.snapshot();
}

function testVaultRoundTrip() {
  const snapshot = buildSnapshot();
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'parallax-wallet-aos-'));
  const vault = new JsonVault(root);
  const saved = vault.save(snapshot);
  assert.ok(saved.envelope.snapshotHash);
  const loaded = vault.load();
  assert.strictEqual(loaded.snapshotHash, saved.envelope.snapshotHash);
  assert.strictEqual(vault.listReceipts().length, 1);
}

function testReconciliation() {
  const snapshot = buildSnapshot();
  const okReport = reconcileSnapshot(snapshot, { USD: 200000 });
  assert.strictEqual(okReport.ok, true);
  assert.strictEqual(okReport.ledgerVerification.ok, true);
  const mismatch = reconcileSnapshot(snapshot, { USD: 199999 });
  assert.strictEqual(mismatch.ok, false);
  assert.ok(mismatch.exceptions.some(e => e.type === 'external_balance_mismatch'));
}

function testStatements() {
  const snapshot = buildSnapshot();
  const statement = walletStatement(snapshot, 'wallet_alice_v02');
  assert.ok(statement.statementHash);
  assert.ok(statement.lines.length >= 2);
  assert.strictEqual(statement.ending.available, 125000);
}

function testRolesAndDashboard() {
  const roles = new TreasuryRoles();
  roles.assign('ops_a', 'approver');
  roles.assign('ops_b', 'approver');
  roles.setQuorum({ approvalsRequired: 2 });
  assert.strictEqual(roles.quorumMet([{ operatorId: 'ops_a' }]), false);
  assert.strictEqual(roles.quorumMet([{ operatorId: 'ops_a' }, { operatorId: 'ops_b' }]), true);
  assert.throws(() => roles.require('ops_a', 'canSettle'));
  const contract = dashboardContract();
  assert.ok(contract.surfaces.some(surface => surface.id === 'reconciliation'));
  assert.strictEqual(contract.liveModeDefault, false);
}

testVaultRoundTrip();
testReconciliation();
testStatements();
testRolesAndDashboard();
console.log('PARALLAX Wallet AOS v0.2 persistence/reconciliation tests passed');
