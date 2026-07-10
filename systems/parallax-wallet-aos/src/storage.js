const fs = require('fs');
const path = require('path');
const { sha256 } = require('./ledger');

class JsonVault {
  constructor(rootDir) {
    this.rootDir = rootDir || path.join(process.cwd(), '.parallax-wallet-aos');
    this.stateFile = path.join(this.rootDir, 'state.json');
    this.receiptFile = path.join(this.rootDir, 'storage_receipts.jsonl');
  }

  ensure() {
    fs.mkdirSync(this.rootDir, { recursive: true });
  }

  save(snapshot) {
    this.ensure();
    const envelope = {
      schema: 'parallax-wallet-aos-state-v0.2',
      savedAt: new Date().toISOString(),
      snapshot,
      snapshotHash: sha256(snapshot)
    };
    const tempFile = `${this.stateFile}.tmp`;
    fs.writeFileSync(tempFile, JSON.stringify(envelope, null, 2));
    fs.renameSync(tempFile, this.stateFile);
    const receipt = this.receipt('state_saved', { snapshotHash: envelope.snapshotHash, stateFile: this.stateFile });
    fs.appendFileSync(this.receiptFile, JSON.stringify(receipt) + '\n');
    return { envelope, receipt };
  }

  load() {
    this.ensure();
    if (!fs.existsSync(this.stateFile)) return null;
    const envelope = JSON.parse(fs.readFileSync(this.stateFile, 'utf8'));
    const actualHash = sha256(envelope.snapshot);
    if (actualHash !== envelope.snapshotHash) {
      throw new Error('state snapshot hash mismatch');
    }
    return envelope;
  }

  receipt(type, payload) {
    const receipt = { type, timestamp: new Date().toISOString(), payload };
    receipt.hash = sha256(receipt);
    return receipt;
  }

  listReceipts() {
    this.ensure();
    if (!fs.existsSync(this.receiptFile)) return [];
    return fs.readFileSync(this.receiptFile, 'utf8').trim().split('\n').filter(Boolean).map(line => JSON.parse(line));
  }
}

module.exports = { JsonVault };
