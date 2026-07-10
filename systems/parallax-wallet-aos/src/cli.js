const { ParallaxAOS } = require('./aos');
const { listAcyilaInterfaces } = require('./acyila');

function print(value) {
  console.log(JSON.stringify(value, null, 2));
}

function demo() {
  const aos = new ParallaxAOS();
  const alice = aos.execute('wallet.create', { ownerId: 'alice', walletId: 'wallet_alice', currency: 'USD', kycStatus: 'verified' }).result;
  const bob = aos.execute('wallet.create', { ownerId: 'bob', walletId: 'wallet_bob', currency: 'USD', kycStatus: 'verified' }).result;
  aos.execute('wallet.creditSandbox', { walletId: alice.walletId, amountMinor: 100000, memo: 'demo funding' });
  const proposal = aos.execute('transfer.propose', {
    sourceWalletId: alice.walletId,
    destination: { walletId: bob.walletId },
    amountMinor: 25000,
    currency: 'USD',
    rail: 'internal_ledger_sandbox',
    memo: 'demo transfer'
  }).result;
  aos.execute('transfer.approve', { proposalId: proposal.proposalId, operatorId: 'operator_demo' });
  aos.execute('transfer.settleSandbox', { proposalId: proposal.proposalId });
  return aos.execute('system.snapshot').result;
}

const [,, command] = process.argv;

try {
  if (command === 'demo') print(demo());
  else if (command === 'interfaces') print({ interfaces: listAcyilaInterfaces() });
  else print({ commands: ['demo', 'interfaces'], usage: 'node src/cli.js demo' });
} catch (error) {
  console.error(error.stack || error.message);
  process.exit(1);
}
