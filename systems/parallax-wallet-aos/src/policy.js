const DEFAULT_POLICY = {
  jurisdiction: 'US_REVIEW_REQUIRED',
  maxSingleTransferMinor: 250000,
  maxDailyTransferMinor: 1000000,
  requireKycForExternalRails: true,
  requireManualApprovalOverMinor: 50000,
  blockedRails: ['live_bank_wire', 'live_ach', 'live_card', 'live_crypto'],
  allowedRails: ['internal_ledger_sandbox', 'bank_wire_sandbox', 'ach_sandbox', 'card_sandbox', 'crypto_sandbox', 'icp_sandbox']
};

function policyCheck({ wallet, proposal, policy = DEFAULT_POLICY }) {
  const errors = [];
  const warnings = [];
  if (!proposal) errors.push('proposal_required');
  if (proposal && !Number.isInteger(proposal.amountMinor)) errors.push('amount_minor_integer_required');
  if (proposal && proposal.amountMinor > policy.maxSingleTransferMinor) errors.push('single_transfer_limit_exceeded');
  if (proposal && !policy.allowedRails.includes(proposal.rail)) errors.push('rail_not_allowed_or_live_rail_blocked');
  if (proposal && policy.requireKycForExternalRails && proposal.rail !== 'internal_ledger_sandbox') {
    if (!wallet || wallet.kycStatus !== 'verified') errors.push('kyc_required_for_external_rail');
  }
  if (proposal && proposal.amountMinor >= policy.requireManualApprovalOverMinor) warnings.push('manual_approval_required');
  return { ok: errors.length === 0, errors, warnings, policyVersion: 'parallax-wallet-policy-v0.1' };
}

module.exports = { DEFAULT_POLICY, policyCheck };
