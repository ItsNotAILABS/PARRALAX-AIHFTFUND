/**
 * Real local validator tests. Require:
 *  - solana-test-validator and Anchor 0.30.1 toolchain
 *  - anchor build / deploy, a non-placeholder declared program ID, and funded ANCHOR_WALLET
 * Run `anchor test --skip-local-validator` with a running validator.
 * No mocked RPC or simulated successful payments are accepted here.
 */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { AnchorProvider, Program, BN } from "@coral-xyz/anchor";
import { Keypair, PublicKey, SystemProgram, LAMPORTS_PER_SOL } from "@solana/web3.js";
import {
  TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID,
  createMint, getOrCreateAssociatedTokenAccount, mintTo, getAccount
} from "@solana/spl-token";

const sysId = new PublicKey("11111111111111111111111111111111");
const provider = AnchorProvider.local();
const connection = provider.connection;
const owner = provider.wallet;
const idl = JSON.parse(fs.readFileSync(new URL("../../../target/idl/parralax_agent_treasury.json", import.meta.url),"utf8"));
const program = new Program(idl, provider);
const programId = program.programId;
if (programId.equals(sysId)) throw new Error("Treasury program ID is still placeholder");
const agent = Keypair.generate();
const beneficiary = Keypair.generate();
const mint = await createMint(connection, owner.payer, owner.publicKey, null, 6);
const tokenSource = await getOrCreateAssociatedTokenAccount(connection, owner.payer, mint, owner.publicKey);
const beneficiaryToken = await getOrCreateAssociatedTokenAccount(connection, owner.payer, mint, beneficiary.publicKey);
await mintTo(connection, owner.payer, mint, tokenSource.address, owner.payer, 10_000_000n);
const [treasury,bump] = PublicKey.findProgramAddressSync([
 Buffer.from("treasury"), owner.publicKey.toBuffer(),agent.publicKey.toBuffer(),
 beneficiary.publicKey.toBuffer(),mint.toBuffer()
],programId);
const [vault] = PublicKey.findProgramAddressSync([
 treasury.toBuffer(),TOKEN_PROGRAM_ID.toBuffer(),mint.toBuffer()
],ASSOCIATED_TOKEN_PROGRAM_ID);
const accounts = { treasury, vault, owner:owner.publicKey,agent:agent.publicKey,
 beneficiary:beneficiary.publicKey,mint,tokenProgram:TOKEN_PROGRAM_ID,
 associatedTokenProgram:ASSOCIATED_TOKEN_PROGRAM_ID,systemProgram:SystemProgram.programId };
const now = Math.floor(Date.now()/1000);
const signAgent = (amount,nonce) => program.methods.spend(new BN(amount), new BN(nonce))
 .accounts({agent:agent.publicKey,treasury,mint,vault,beneficiaryToken:beneficiaryToken.address,tokenProgram:TOKEN_PROGRAM_ID})
 .signers([agent]).rpc();
async function mustReject(f,reason){
 let rejected=false;try{await f()}catch(e){rejected=true}
 assert.ok(rejected,reason);
}
test("initialize, deposit, spend, replay, cap, revoke, owner withdrawal",async t=>{
 await t.test("initialize exact PDA and fixed limits",async()=>{
  await program.methods.initialize(new BN(1_000_000),new BN(2_000_000),new BN(4_000_000),new BN(now+3600))
   .accounts(accounts).rpc();
  const state=await program.account.treasury.fetch(treasury);
  assert.equal(state.owner.toBase58(),owner.publicKey.toBase58());
  assert.equal(state.agent.toBase58(),agent.publicKey.toBase58());
  assert.equal(state.beneficiary.toBase58(),beneficiary.publicKey.toBase58());
  assert.equal(state.bump,bump);
 });
 await t.test("owner deposits checked SPL amount into PDA vault",async()=>{
  await program.methods.deposit(new BN(4_000_000)).accounts({
   owner:owner.publicKey,treasury,mint,ownerToken:tokenSource.address,vault,tokenProgram:TOKEN_PROGRAM_ID
  }).rpc();
  assert.equal((await getAccount(connection,vault)).amount,4_000_000n);
 });
 await t.test("agent signs exact recipient transfer",async()=>{
  await signAgent(500_000,0);
  assert.equal((await getAccount(connection,beneficiaryToken.address)).amount,500_000n);
  assert.equal((await program.account.treasury.fetch(treasury)).nextNonce.toString(),"1");
 });
 await t.test("replayed nonce denied",async()=>mustReject(()=>signAgent(100_000,0),"replayed nonce accepted"));
 await t.test("per transaction cap denied",async()=>mustReject(()=>signAgent(1_000_001,1),"over-cap spend accepted"));
 await t.test("wrong agent cannot spend",async()=>{
  const attacker=Keypair.generate();
  await mustReject(()=>program.methods.spend(new BN(1),new BN(1))
   .accounts({agent:attacker.publicKey,treasury,mint,vault,beneficiaryToken:beneficiaryToken.address,tokenProgram:TOKEN_PROGRAM_ID})
   .signers([attacker]).rpc(),"wrong agent signed spend");
 });
 await t.test("wrong beneficiary token account cannot receive funds",async()=>{
  await mustReject(()=>program.methods.spend(new BN(1),new BN(1))
   .accounts({agent:agent.publicKey,treasury,mint,vault,beneficiaryToken:tokenSource.address,tokenProgram:TOKEN_PROGRAM_ID})
   .signers([agent]).rpc(),"token went to wrong beneficiary");
 });
 await t.test("daily spending cumulative cap denied",async()=>{
  await signAgent(1_000_000,1);
  await mustReject(()=>signAgent(600_000,2),"daily cap bypassed");
 });
 await t.test("only owner may revoke",async()=>{
  await program.methods.revoke().accounts({owner:owner.publicKey,treasury}).rpc();
  assert.equal((await program.account.treasury.fetch(treasury)).revoked,true);
  await mustReject(()=>signAgent(1,2),"revoked agent spent");
 });
 await t.test("unauthorized wallet cannot withdraw",async()=>{
  const attacker=Keypair.generate();
  await mustReject(()=>program.methods.withdraw(new BN(1)).accounts({
   owner:attacker.publicKey,treasury,mint,vault,ownerToken:tokenSource.address,tokenProgram:TOKEN_PROGRAM_ID
  }).signers([attacker]).rpc(),"non-owner withdrew funds");
 });
 await t.test("owner can withdraw remaining vault balance",async()=>{
  const remaining=(await getAccount(connection,vault)).amount;
  await program.methods.withdraw(new BN(remaining.toString())).accounts({
   owner:owner.publicKey,treasury,mint,vault,ownerToken:tokenSource.address,tokenProgram:TOKEN_PROGRAM_ID
  }).rpc();
  assert.equal((await getAccount(connection,vault)).amount,0n);
 });
});
