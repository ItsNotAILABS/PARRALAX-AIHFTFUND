const assert = require('assert');
const { WalletOS } = require('../src/wallet');
const { ParallaxAOS } = require('../src/aos');
const { listAcyilaInterfaces } = require('../src/acyila');
const { RAILS } = require('../src/rails');

function testInternalTransfer() {
  const os = new WalletOS();
  const a = os.createWallet({ ownerId: 'alice', walletId: 'wallet_a', kycStatus: 'verified' });
  const b = os.createWallet({ ownerId: 'bob', walletId: 'wallet_b', kycStatus: 'verified' });
  os.creditSandbox({ walletId: a.walletId, amountMinor: 100000 });
  const p = os.proposeTransfer({ sourceWalletId: a.walletId, destination: { walletId: b.walletId }, amountMinor: 35000, rail: 'internal_ledger_sandbox' });
  assert.strictEqual(p.policy.ok, true);
  os.approveTransfer({ proposalId: p.proposalId, operatorId: 'operator' });
  os.settleTransfer({ proposalId: p.proposalId });
  assert.strictEqual(os.balance(a.walletId).available, 65000);
  assert.strictEqual(os.balance(b.walletId).available, 35000);
  assert.strictEqual(os.ledger.verify().ok, true);
}

function testPolicyBlocksExternalWithoutKyc() {
  const os = new WalletOS();
  const w = os.createWallet({ ownerId: 'no_kyc', walletId: 'wallet_unverified', kycStatus: 'unverified' });
  os.creditSandbox({ walletId: w.walletId, amountMinor: 100000 });
  const p = os.proposeTransfer({ sourceWalletId: w.walletId, destination: { account: 'sandbox-bank' }, amountMinor: 10000, rail: 'ach_sandbox' });
  assert.strictEqual(p.policy.ok, false);
  assert.ok(p.policy.errors.includes('kyc_required_for_external_rail'));
}

function testAosAndInterfaces() {
  const aos = new ParallaxAOS();
  assert.ok(aos.listCommands().some(c => c.name === 'transfer.propose'));
  assert.ok(listAcyilaInterfaces().some(i => i.id === 'rail_gateway'));
  assert.strictEqual(RAILS.crypto_sandbox.live, false);
}

testInternalTransfer();
testPolicyBlocksExternalWithoutKyc();
testAosAndInterfaces();
console.log('PARALLAX Wallet AOS tests passed');
