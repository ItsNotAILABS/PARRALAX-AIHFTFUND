const { sha256 } = require('./ledger');

const RAILS = {
  internal_ledger_sandbox: { kind: 'internal', live: false, description: 'Internal PARALLAX ledger transfer only.' },
  bank_wire_sandbox: { kind: 'bank_wire', live: false, description: 'Sandbox bank wire adapter. No bank file is sent.' },
  ach_sandbox: { kind: 'ach', live: false, description: 'Sandbox ACH adapter. No NACHA file is originated.' },
  card_sandbox: { kind: 'card', live: false, description: 'Sandbox card adapter. No issuer/acquirer call is made.' },
  crypto_sandbox: { kind: 'crypto', live: false, description: 'Sandbox crypto adapter. No transaction is signed or broadcast.' },
  icp_sandbox: { kind: 'icp', live: false, description: 'Sandbox ICP adapter. No canister update is submitted.' }
};

function getRail(railId) {
  const rail = RAILS[railId];
  if (!rail) throw new Error(`unknown rail: ${railId}`);
  if (rail.live) throw new Error(`live rail disabled: ${railId}`);
  return rail;
}

function prepareRailPacket(proposal) {
  const rail = getRail(proposal.rail);
  const packet = {
    railId: proposal.rail,
    mode: 'SANDBOX_ONLY',
    liveSettlement: false,
    proposalId: proposal.proposalId,
    sourceWalletId: proposal.sourceWalletId,
    destination: proposal.destination,
    amountMinor: proposal.amountMinor,
    currency: proposal.currency,
    memo: proposal.memo || '',
    preparedAt: new Date().toISOString()
  };
  packet.packetHash = sha256(packet);
  return { rail, packet };
}

module.exports = { RAILS, getRail, prepareRailPacket };
