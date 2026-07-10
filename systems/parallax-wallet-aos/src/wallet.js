const crypto = require('crypto');
const { HashChainedLedger, sha256 } = require('./ledger');
const { DEFAULT_POLICY, policyCheck } = require('./policy');
const { prepareRailPacket } = require('./rails');

function id(prefix) {
  return `${prefix}_${crypto.randomBytes(8).toString('hex')}`;
}

class WalletOS {
  constructor({ policy = DEFAULT_POLICY } = {}) {
    this.policy = policy;
    this.ledger = new HashChainedLedger();
    this.wallets = new Map();
    this.proposals = new Map();
    this.receipts = [];
  }

  createWallet({ ownerId, walletId = id('wallet'), currency = 'USD', kycStatus = 'unverified', metadata = {} }) {
    const settlementAccountId = `${walletId}:settlement:${currency}`;
    const account = this.ledger.createAccount({ accountId: settlementAccountId, ownerId, currency, accountType: 'wallet_settlement', metadata });
    const wallet = { walletId, ownerId, currency, kycStatus, settlementAccountId, metadata, createdAt: new Date().toISOString() };
    this.wallets.set(walletId, wallet);
    this.receipt('wallet_created', { wallet, account });
    return wallet;
  }

  getWallet(walletId) {
    const wallet = this.wallets.get(walletId);
    if (!wallet) throw new Error(`unknown wallet: ${walletId}`);
    return wallet;
  }

  creditSandbox({ walletId, amountMinor, memo = 'sandbox credit', referenceId = id('credit') }) {
    const wallet = this.getWallet(walletId);
    const entry = this.ledger.credit({ creditAccountId: wallet.settlementAccountId, amount: amountMinor, currency: wallet.currency, memo, referenceId, metadata: { sandbox: true } });
    this.receipt('sandbox_credit', { walletId, amountMinor, entryHash: entry.hash });
    return entry;
  }

  proposeTransfer({ sourceWalletId, destination, amountMinor, currency = 'USD', rail = 'internal_ledger_sandbox', memo = '', metadata = {} }) {
    const wallet = this.getWallet(sourceWalletId);
    const proposal = {
      proposalId: id('proposal'),
      sourceWalletId,
      sourceAccountId: wallet.settlementAccountId,
      destination,
      amountMinor,
      currency,
      rail,
      memo,
      metadata,
      status: 'proposed',
      approvals: [],
      createdAt: new Date().toISOString()
    };
    proposal.policy = policyCheck({ wallet, proposal, policy: this.policy });
    proposal.proposalHash = sha256(proposal);
    this.proposals.set(proposal.proposalId, proposal);
    this.receipt('transfer_proposed', { proposalId: proposal.proposalId, proposalHash: proposal.proposalHash, policy: proposal.policy });
    return proposal;
  }

  approveTransfer({ proposalId, operatorId, note = '' }) {
    const proposal = this.proposals.get(proposalId);
    if (!proposal) throw new Error(`unknown proposal: ${proposalId}`);
    if (!proposal.policy.ok) throw new Error(`proposal failed policy: ${proposal.policy.errors.join(',')}`);
    if (proposal.status !== 'proposed' && proposal.status !== 'approved') throw new Error(`proposal status cannot approve: ${proposal.status}`);
    proposal.approvals.push({ operatorId, note, approvedAt: new Date().toISOString() });
    proposal.status = 'approved';
    this.receipt('transfer_approved', { proposalId, operatorId });
    return proposal;
  }

  settleTransfer({ proposalId }) {
    const proposal = this.proposals.get(proposalId);
    if (!proposal) throw new Error(`unknown proposal: ${proposalId}`);
    if (proposal.status !== 'approved') throw new Error('proposal must be approved before settlement');

    const railPacket = prepareRailPacket(proposal);
    let ledgerEntry = null;

    if (proposal.rail === 'internal_ledger_sandbox') {
      if (!proposal.destination || !proposal.destination.walletId) throw new Error('internal transfer requires destination.walletId');
      const destWallet = this.getWallet(proposal.destination.walletId);
      ledgerEntry = this.ledger.post({
        debitAccountId: proposal.sourceAccountId,
        creditAccountId: destWallet.settlementAccountId,
        amount: proposal.amountMinor,
        currency: proposal.currency,
        memo: proposal.memo,
        referenceId: proposal.proposalId,
        metadata: { railPacketHash: railPacket.packet.packetHash }
      });
    }

    proposal.status = 'settled_sandbox';
    proposal.settledAt = new Date().toISOString();
    proposal.railPacket = railPacket.packet;
    proposal.ledgerEntryHash = ledgerEntry ? ledgerEntry.hash : null;
    this.receipt('transfer_settled_sandbox', { proposalId, railPacketHash: railPacket.packet.packetHash, ledgerEntryHash: proposal.ledgerEntryHash });
    return proposal;
  }

  balance(walletId) {
    const wallet = this.getWallet(walletId);
    return this.ledger.getAccount(wallet.settlementAccountId);
  }

  receipt(type, payload) {
    const receipt = { index: this.receipts.length + 1, type, timestamp: new Date().toISOString(), payload };
    receipt.hash = sha256(receipt);
    this.receipts.push(receipt);
    return receipt;
  }

  snapshot() {
    return { wallets: Array.from(this.wallets.values()), proposals: Array.from(this.proposals.values()), ledger: this.ledger.snapshot(), receipts: this.receipts };
  }
}

module.exports = { WalletOS };
