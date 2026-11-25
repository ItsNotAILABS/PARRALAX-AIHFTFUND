/**
 * End-to-end tests against a real local validator, run by `anchor test`
 * (which builds, starts solana-test-validator and deploys first).
 *
 * Clock-dependent behaviour (expiry, allowance refill) is covered by the Rust
 * program tests in programs/agent-treasury/tests/program.rs, which can warp time.
 * Every negative case asserts the exact Anchor error, not just "it threw".
 */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import anchor from "@coral-xyz/anchor";
import { Keypair, PublicKey, SystemProgram } from "@solana/web3.js";
import {
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
  createMint,
  getAssociatedTokenAddressSync,
  getOrCreateAssociatedTokenAccount,
  mintTo,
  getAccount,
} from "@solana/spl-token";

const { AnchorProvider, Program, BN, AnchorError } = anchor;

const provider = AnchorProvider.env();
anchor.setProvider(provider);
const connection = provider.connection;
const owner = provider.wallet;
const idl = JSON.parse(
  fs.readFileSync(new URL("../target/idl/parralax_agent_treasury.json", import.meta.url), "utf8"),
);
const program = new Program(idl, provider);

// Programs loaded at genesis or just deployed become invocable a slot later.
while ((await connection.getSlot("confirmed")) < 3) await new Promise((r) => setTimeout(r, 200));

const PER_TX = 1_000_000;
const DAILY = 2_000_000;
const LIFETIME = 4_000_000;

async function expectError(promise, code) {
  let err;
  try {
    await promise;
  } catch (e) {
    err = e;
  }
  assert.ok(err, `expected ${code} but the transaction succeeded`);
  const parsed = err instanceof AnchorError ? err : AnchorError.parse(err.logs ?? err.transactionLogs ?? []);
  assert.equal(parsed?.error?.errorCode?.code, code, `expected ${code}, got: ${err}`);
}

async function setup(seedId) {
  const agent = Keypair.generate();
  const beneficiary = Keypair.generate();
  const guardian = Keypair.generate();
  const mint = await createMint(connection, owner.payer, owner.publicKey, null, 6);
  const ownerToken = (await getOrCreateAssociatedTokenAccount(connection, owner.payer, mint, owner.publicKey)).address;
  const beneficiaryToken = (await getOrCreateAssociatedTokenAccount(connection, owner.payer, mint, beneficiary.publicKey)).address;
  await mintTo(connection, owner.payer, mint, ownerToken, owner.payer, 100_000_000n);
  const id = new BN(seedId);
  const [treasury] = PublicKey.findProgramAddressSync(
    [Buffer.from("treasury"), owner.publicKey.toBuffer(), mint.toBuffer(), id.toArrayLike(Buffer, "le", 8)],
    program.programId,
  );
  const vault = getAssociatedTokenAddressSync(mint, treasury, true);
  const now = Math.floor(Date.now() / 1000);
  await program.methods
    .initialize(
      id,
      { perTxCap: new BN(PER_TX), dailyCap: new BN(DAILY), lifetimeCap: new BN(LIFETIME), expiresAt: new BN(now + 3600) },
      guardian.publicKey,
    )
    .accountsStrict({
      owner: owner.publicKey,
      agent: agent.publicKey,
      beneficiary: beneficiary.publicKey,
      mint,
      treasury,
      vault,
      tokenProgram: TOKEN_PROGRAM_ID,
      associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
      systemProgram: SystemProgram.programId,
    })
    .rpc();
  await program.methods
    .deposit(new BN(LIFETIME))
    .accountsStrict({ owner: owner.publicKey, treasury, mint, ownerToken, vault, tokenProgram: TOKEN_PROGRAM_ID })
    .rpc();
  const spend = (amount, nonce, signer = agent, to = beneficiaryToken) =>
    program.methods
      .spend(new BN(amount), new BN(nonce))
      .accountsStrict({ agent: signer.publicKey, treasury, mint, vault, beneficiaryToken: to, tokenProgram: TOKEN_PROGRAM_ID })
      .signers([signer])
      .rpc();
  const ownerVault = { owner: owner.publicKey, treasury, mint, vault, ownerToken, tokenProgram: TOKEN_PROGRAM_ID };
  return { agent, beneficiary, guardian, mint, ownerToken, beneficiaryToken, treasury, vault, spend, ownerVault };
}

test("spend path: caps, replay, wrong signer, wrong recipient", async () => {
  const t = await setup(1);
  await t.spend(500_000, 0);
  assert.equal((await getAccount(connection, t.beneficiaryToken)).amount, 500_000n);
  assert.equal((await program.account.treasury.fetch(t.treasury)).nextNonce.toString(), "1");

  await expectError(t.spend(1, 0), "InvalidNonce");
  await expectError(t.spend(PER_TX + 1, 1), "PerTransactionLimit");
  await expectError(t.spend(1, 1, Keypair.generate()), "ConstraintHasOne");
  await expectError(t.spend(1, 1, t.agent, t.ownerToken), "ConstraintTokenOwner");

  await t.spend(PER_TX, 1);
  await expectError(t.spend(600_000, 2), "DailyLimit");
});

test("guardian revoke, then owner withdraws everything (C1 regression)", async () => {
  const t = await setup(2);
  await program.methods.revoke().accountsStrict({ authority: t.guardian.publicKey, treasury: t.treasury }).signers([t.guardian]).rpc();
  await expectError(t.spend(1, 0), "Revoked");

  const attacker = Keypair.generate();
  await expectError(
    program.methods.withdraw(new BN(1)).accountsStrict({ ...t.ownerVault, owner: attacker.publicKey }).signers([attacker]).rpc(),
    "ConstraintHasOne",
  );

  const remaining = (await getAccount(connection, t.vault)).amount;
  await program.methods.withdraw(new BN(remaining.toString())).accountsStrict(t.ownerVault).rpc();
  assert.equal((await getAccount(connection, t.vault)).amount, 0n);
});

test("close drains the vault and deletes both accounts", async () => {
  const t = await setup(3);
  await t.spend(PER_TX, 0);
  const before = (await getAccount(connection, t.ownerToken)).amount;
  await program.methods.close().accountsStrict(t.ownerVault).rpc();
  assert.equal((await getAccount(connection, t.ownerToken)).amount, before + BigInt(LIFETIME - PER_TX));
  assert.equal(await connection.getAccountInfo(t.treasury), null);
  assert.equal(await connection.getAccountInfo(t.vault), null);
});
