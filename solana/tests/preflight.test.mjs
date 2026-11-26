// Fast source-level gates that need no toolchain. Behaviour is tested in
// programs/agent-treasury/tests/program.rs and treasury.localnet.test.mjs.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const root = new URL("../", import.meta.url);
const read = (p) => fs.readFileSync(new URL(p, root), "utf8");
const lib = read("programs/agent-treasury/src/lib.rs");
const anchorToml = read("Anchor.toml");

const declared = lib.match(/declare_id!\("([1-9A-HJ-NP-Za-km-z]{32,44})"\)/)?.[1];

test("program ID is not the System Program placeholder", () => {
  assert.ok(declared, "declare_id! present");
  assert.notEqual(declared, "11111111111111111111111111111111");
});

test("Anchor.toml localnet ID matches declare_id!", () => {
  assert.ok(anchorToml.includes(`parralax_agent_treasury = "${declared}"`));
});

test("no mainnet or devnet deployment is configured in this source", () => {
  assert.ok(!/\[programs\.(mainnet|devnet)\]/.test(anchorToml));
});

test("release profile keeps overflow checks", () => {
  assert.match(read("Cargo.toml"), /overflow-checks\s*=\s*true/);
});

test("toolchain and dependencies are pinned", () => {
  assert.match(read("rust-toolchain.toml"), /channel = "1\.79\.0"/);
  const cargo = read("programs/agent-treasury/Cargo.toml");
  assert.match(cargo, /anchor-lang = "=0\.30\.1"/);
  assert.match(cargo, /version = "=0\.30\.1"/);
  assert.ok(fs.existsSync(new URL("Cargo.lock", root)), "Cargo.lock committed");
});
