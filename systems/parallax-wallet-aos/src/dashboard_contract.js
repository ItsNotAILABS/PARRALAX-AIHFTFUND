function dashboardContract() {
  return {
    schema: 'parallax-wallet-dashboard-contract-v0.2',
    title: 'PARALLAX Wallet AOS Operator Dashboard',
    surfaces: [
      { id: 'overview', widgets: ['health', 'ledger_verification', 'total_balances', 'open_proposals', 'policy_exceptions'] },
      { id: 'wallets', widgets: ['wallet_table', 'balance_cards', 'statement_export'] },
      { id: 'transfers', widgets: ['proposal_create', 'approval_queue', 'settlement_queue', 'reversal_queue'] },
      { id: 'reconciliation', widgets: ['ledger_totals', 'external_balance_import', 'exception_table', 'report_export'] },
      { id: 'audit', widgets: ['receipt_stream', 'hash_chain_status', 'storage_receipts', 'download_exports'] },
      { id: 'controls', widgets: ['treasury_roles', 'approval_quorum', 'rail_activation_status', 'live_mode_blockers'] }
    ],
    api: {
      read: ['GET /health', 'GET /interfaces', 'GET /commands', 'GET /snapshot'],
      command: ['POST /execute'],
      future: ['POST /statement', 'POST /reconcile', 'POST /export']
    },
    liveModeDefault: false,
    requiredHumanActions: ['approve_transfer', 'activate_live_rail', 'change_quorum', 'export_audit_package']
  };
}

module.exports = { dashboardContract };
