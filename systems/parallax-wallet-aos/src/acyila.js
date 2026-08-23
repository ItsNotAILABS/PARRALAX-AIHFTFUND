const ACYILA_INTERFACES = {
  wallet_api: {
    surface: 'http_json',
    description: 'Local HTTP JSON surface for wallets, balances, proposals, approvals, and sandbox settlement.'
  },
  agent_tooling: {
    surface: 'aos_command_bus',
    description: 'AOS command layer for agent-directed but policy-gated wallet operations.'
  },
  treasury_console: {
    surface: 'operator_ui_contract',
    description: 'Treasury operator contract for approvals, limits, receipts, and audit review.'
  },
  rail_gateway: {
    surface: 'adapter_contract',
    description: 'Sandbox rail adapter interface. Live rails are blocked until compliance activation.'
  },
  compliance_gate: {
    surface: 'policy_contract',
    description: 'KYC, AML, sanctions, fraud, transfer limits, and approval-state contract.'
  },
  receipt_stream: {
    surface: 'audit_contract',
    description: 'Hash-linked receipt and ledger event stream for proof-before-speed operation.'
  }
};

function listAcyilaInterfaces() {
  return Object.entries(ACYILA_INTERFACES).map(([id, value]) => ({ id, ...value }));
}

function getAcyilaInterface(id) {
  if (!ACYILA_INTERFACES[id]) throw new Error(`unknown ACYILA interface: ${id}`);
  return { id, ...ACYILA_INTERFACES[id] };
}

module.exports = { ACYILA_INTERFACES, listAcyilaInterfaces, getAcyilaInterface };
