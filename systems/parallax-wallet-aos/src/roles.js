const TREASURY_ROLES = {
  viewer: { canRead: true, canPropose: false, canApprove: false, canSettle: false, canAdmin: false },
  proposer: { canRead: true, canPropose: true, canApprove: false, canSettle: false, canAdmin: false },
  approver: { canRead: true, canPropose: false, canApprove: true, canSettle: false, canAdmin: false },
  settler: { canRead: true, canPropose: false, canApprove: false, canSettle: true, canAdmin: false },
  admin: { canRead: true, canPropose: true, canApprove: true, canSettle: true, canAdmin: true }
};

class TreasuryRoles {
  constructor() {
    this.assignments = new Map();
    this.quorum = { approvalsRequired: 1, distinctApprovers: true };
  }

  assign(operatorId, role) {
    if (!TREASURY_ROLES[role]) throw new Error(`unknown treasury role: ${role}`);
    if (!this.assignments.has(operatorId)) this.assignments.set(operatorId, new Set());
    this.assignments.get(operatorId).add(role);
    return this.operator(operatorId);
  }

  operator(operatorId) {
    const roles = Array.from(this.assignments.get(operatorId) || []);
    const effective = roles.reduce((acc, role) => {
      const grants = TREASURY_ROLES[role];
      for (const [key, value] of Object.entries(grants)) acc[key] = Boolean(acc[key] || value);
      return acc;
    }, { canRead: false, canPropose: false, canApprove: false, canSettle: false, canAdmin: false });
    return { operatorId, roles, effective };
  }

  require(operatorId, permission) {
    const op = this.operator(operatorId);
    if (!op.effective[permission]) throw new Error(`operator ${operatorId} lacks ${permission}`);
    return op;
  }

  setQuorum({ approvalsRequired = 1, distinctApprovers = true } = {}) {
    if (!Number.isInteger(approvalsRequired) || approvalsRequired < 1) throw new Error('approvalsRequired must be positive integer');
    this.quorum = { approvalsRequired, distinctApprovers };
    return this.quorum;
  }

  quorumMet(approvals) {
    const operatorIds = approvals.map(a => a.operatorId);
    const count = this.quorum.distinctApprovers ? new Set(operatorIds).size : operatorIds.length;
    return count >= this.quorum.approvalsRequired;
  }

  snapshot() {
    return { quorum: this.quorum, operators: Array.from(this.assignments.keys()).map(id => this.operator(id)) };
  }
}

module.exports = { TREASURY_ROLES, TreasuryRoles };
