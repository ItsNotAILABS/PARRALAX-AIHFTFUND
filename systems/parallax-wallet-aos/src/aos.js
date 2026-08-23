const { WalletOS } = require('./wallet');

class ParallaxAOS {
  constructor() {
    this.walletOS = new WalletOS();
    this.commands = new Map();
    this.registerCoreCommands();
  }

  register(name, handler, metadata = {}) {
    this.commands.set(name, { name, handler, metadata });
  }

  registerCoreCommands() {
    this.register('wallet.create', (input) => this.walletOS.createWallet(input), { risk: 'low' });
    this.register('wallet.creditSandbox', (input) => this.walletOS.creditSandbox(input), { risk: 'sandbox' });
    this.register('wallet.balance', (input) => this.walletOS.balance(input.walletId), { risk: 'read' });
    this.register('transfer.propose', (input) => this.walletOS.proposeTransfer(input), { risk: 'policy_gated' });
    this.register('transfer.approve', (input) => this.walletOS.approveTransfer(input), { risk: 'operator_approval' });
    this.register('transfer.settleSandbox', (input) => this.walletOS.settleTransfer(input), { risk: 'sandbox_settlement_only' });
    this.register('system.snapshot', () => this.walletOS.snapshot(), { risk: 'read' });
  }

  listCommands() {
    return Array.from(this.commands.values()).map(({ name, metadata }) => ({ name, metadata }));
  }

  execute(command, input = {}) {
    const item = this.commands.get(command);
    if (!item) throw new Error(`unknown AOS command: ${command}`);
    const result = item.handler(input);
    return { command, executedAt: new Date().toISOString(), result };
  }
}

module.exports = { ParallaxAOS };
