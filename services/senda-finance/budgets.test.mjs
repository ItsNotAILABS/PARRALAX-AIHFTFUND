import test from "node:test";
import assert from "node:assert/strict";
import {evaluateAgentBudget} from "./budgets.mjs";
const now=1730000000000;
const base={tenantId:"tenant1",organismId:"org1",policyId:"policy1",requestId:"req1",
 beneficiaryId:"payee1",asset:"USDC",amountMinor:1000,maxPerTransactionMinor:5000,
 totalBudgetMinor:10000,usedBudgetMinor:4000,reservedBudgetMinor:3000,expiresAt:now+10000,
 allowedBeneficiaries:["payee1"],allowedAssets:["USDC"],requestNonce:"nonce1",
 nonceUnused:true,policyVerified:true,ledgerVerified:true,revoked:false};
test("budget allows review but never authorizes signing",()=>{
 const r=evaluateAgentBudget(base,now);assert.equal(r.decision,"REVIEW_REQUIRED");
 assert.equal(r.executionAuthorized,false);assert.equal(r.budgetReservationCreated,false);
});
test("fail-closed budget inputs",()=>{
 const patches=[{revoked:true},{expiresAt:now},{beneficiaryId:"payee2"},
 {asset:"SOL"},{amountMinor:6000},{amountMinor:4000},{nonceUnused:false},
 {policyVerified:false},{ledgerVerified:false},{tenantId:""},{amountMinor:NaN},
 {usedBudgetMinor:-1},{requestNonce:"not allowed!"}];
 for(const p of patches)assert.equal(evaluateAgentBudget({...base,...p},now).decision,"DENY");
});
