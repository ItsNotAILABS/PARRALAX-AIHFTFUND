import test from "node:test";
import assert from "node:assert/strict";
import {evaluatePretrade,AGENT_ROLES,POLICY_VERSION} from "./pretrade.mjs";
const now=1800000000000,mint="So11111111111111111111111111111111111111112";
const order={requestId:"req1",tenantId:"t1",agentId:"a1",venue:"jupiter",mint,side:"buy",notionalUsd:10,leverage:1,priceImpactBps:5,slippageBps:8};
const portfolio={equityUsd:1000,dayStartEquityUsd:1000,peakEquityUsd:1000,exposureUsd:100,dailyTurnoverUsd:150,reservedUsd:0,openOrders:0};
const market={spreadBps:7,liquidityUsd:1000000,oracleObservedAtMs:now-1000,oracleHealthy:true,halted:false};
const limits={allowedVenues:["jupiter"],allowedMints:[mint],allowedSides:["buy","sell","close"],maxOrderUsd:25,
 maxGrossUsd:250,maxTurnoverUsd:500,maxDailyLossPct:0.03,maxDrawdownPct:0.06,
 maxLeverage:1,maxImpactBps:40,maxSpreadBps:45,maxQuoteAgeMs:2500,maxOracleAgeMs:3000,
 maxOpenOrders:2,minLiquidityUsd:250000};
const evidence={quoteId:"q1",issuerId:"provider1",observedAtMs:now-500,issuerPolicyVersion:POLICY_VERSION,trustedIngestion:true,principalEligible:true};
function check(patch={}){return evaluatePretrade({order:{...order,...patch.order},portfolio:{...portfolio,...patch.portfolio},
 market:{...market,...patch.market},limits:{...limits,...patch.limits},evidence:{...evidence,...patch.evidence}},now)}
test("agent roles cannot sign or spend",()=>assert.ok(AGENT_ROLES.every(r=>r.capabilities.every(c=>!/sign|submit|withdraw|transfer/.test(c)))));
test("passing checks never authorize execution",()=>{let r=check();assert.equal(r.decision,"APPROVAL_REQUIRED");assert.equal(r.executionAuthorized,false)});
test("fail closed across risk and data scenarios",()=>{
 const patches=[
 {order:{venue:"fake"}},{order:{mint:"fake"}},{order:{side:"short"}},{order:{notionalUsd:26}},
 {order:{notionalUsd:NaN}},{order:{notionalUsd:0}},{order:{leverage:2}},
 {order:{priceImpactBps:45}},{order:{slippageBps:45}},{market:{spreadBps:50}},
 {market:{liquidityUsd:1}},{market:{oracleObservedAtMs:now-9999}},
 {market:{oracleHealthy:false}},{market:{halted:true}},
 {evidence:{observedAtMs:now-3000}},{evidence:{observedAtMs:now+1000}},
 {evidence:{trustedIngestion:false}},{evidence:{principalEligible:false}},
 {evidence:{issuerPolicyVersion:"old"}},{portfolio:{equityUsd:960}},
 {portfolio:{peakEquityUsd:1500}},{portfolio:{exposureUsd:245}},
 {portfolio:{openOrders:2}},{portfolio:{dailyTurnoverUsd:495}},
 {limits:{maxOrderUsd:0}},{limits:{allowedMints:[]}}
 ];
 for(const [i,x] of patches.entries())assert.equal(check(x).decision,"DENY","case "+i);
});
test("close proposals bypass exposure cap but still require signature",()=>{
 let r=check({order:{side:"close"},portfolio:{exposureUsd:9999,openOrders:5}});
 assert.equal(r.decision,"APPROVAL_REQUIRED");assert.equal(r.executionAuthorized,false);
});
