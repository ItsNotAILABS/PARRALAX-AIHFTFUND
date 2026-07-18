import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const required = [
  'docs/release-harness/README.md',
  'docs/release-harness/model-cards/parallax-aihft-research.md',
  'docs/release-harness/release-packages/v1.0.0/RELEASE.md',
  'docs/release-harness/release-packages/v1.0.0/release-manifest.json',
  'schemas/ecosystem-feeder.schema.json',
  'schemas/research-backtest-release.schema.json'
];
for (const file of required) assert.ok(fs.existsSync(path.join(root, file)), `missing ${file}`);
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'docs/release-harness/release-packages/v1.0.0/release-manifest.json'), 'utf8'));
assert.equal(manifest.schema, 'nova-ecosystem-feeder-release-v1');
assert.equal(manifest.repo, 'ItsNotAILABS/PARRALAX-AIHFTFUND');
assert.ok(Array.isArray(manifest.evidence) && manifest.evidence.length >= 5);
assert.ok(Array.isArray(manifest.boundaries) && manifest.boundaries.includes('research backtest only'));
assert.equal(manifest.approvals.operator, false);
const banned = [/guaranteed profit/i, /risk-free/i, /live trading enabled/i, /investment advice/i, /capital deployed/i];
for (const file of required) {
  const text = fs.readFileSync(path.join(root, file), 'utf8');
  for (const pattern of banned) assert.equal(pattern.test(text), false, `${file} contains banned phrase ${pattern}`);
}
console.log(JSON.stringify({ ok: true, checked: required.length, release: manifest.release }, null, 2));
