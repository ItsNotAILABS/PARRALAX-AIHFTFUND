import test from "node:test";
import assert from "node:assert/strict";
import {runResearchSwarm} from "./research-swarm.mjs";
const yes=async()=>({state:"PASS",summary:"Independent observation",sourceId:"proof-1"});
const workers={"market-data-qa":yes,"liquidity-scout":yes,"portfolio-risk":yes};
const request={requestId:"run1",tenantId:"tenant1",symbol:"SOL",context:{instrument:"SOL"},workers,timeoutMs:1000};
test("research roles review without signing or executing",async()=>{
 const r=await runResearchSwarm(request);
 assert.equal(r.status,"REVIEW");assert.equal(r.executionAuthorized,false);
 assert.equal(r.receipts.length,3);assert.equal(r.evidenceSha256.length,64);
});
test("portfolio risk veto is binding",async()=>{
 const r=await runResearchSwarm({...request,workers:{...workers,"portfolio-risk":async()=>({state:"VETO",summary:"Daily stop"})}});
 assert.equal(r.status,"HOLD");assert.deepEqual(r.veto,["portfolio-risk"]);
});
test("missing source and fake authority fail closed",async()=>{
 assert.equal((await runResearchSwarm({...request,workers:{"market-data-qa":yes}})).status,"DENY");
 const r=await runResearchSwarm({...request,workers:{...workers,"portfolio-risk":async()=>({state:"PASS",canSign:true,transaction:"junk"})}});
 assert.equal(r.status,"HOLD");
});
test("worker failures and timeouts become hold receipts",async()=>{
 const r=await runResearchSwarm({...request,timeoutMs:100,workers:{
  ...workers,"liquidity-scout":async()=>new Promise(()=>{})
 }});
 assert.equal(r.status,"HOLD");
 assert.equal(r.receipts.find(x=>x.role==="liquidity-scout").state,"UNKNOWN");
});
