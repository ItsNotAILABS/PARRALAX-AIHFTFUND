import test from "node:test";
import assert from "node:assert/strict";
import { evaluateRisk,planExit,VENUES,planOrder } from "./core.mjs";
const risk={instrument:"SOL",side:"long",notionalUsd:100,maxNotionalUsd:200,leverage:2,maxLeverage:3,quoteAgeMs:10,maxQuoteAgeMs:1000,priceImpactBps:8,maxImpactBps:50,oracleHealthy:true,venueEligible:true,walletAuthorized:true};
test("bounded risk is review only, never execution authority",()=>{assert.equal(evaluateRisk(risk).decision,"PASS_TO_WALLET_REVIEW");assert.equal(evaluateRisk(risk).executionAuthorized,false)});
test("risk denies missing evidence or exceeded limits",()=>{
  const cases=[{quoteAgeMs:1001},{priceImpactBps:51},{leverage:4},{notionalUsd:201},{oracleHealthy:false},{venueEligible:false},{walletAuthorized:false},{marketHalted:true}];
  for(const patch of cases)assert.equal(evaluateRisk({...risk,...patch}).decision,"DENY");
});
test("risk denies NaN and invalid strings",()=>{for(const n of [NaN,Infinity,-1,0])assert.equal(evaluateRisk({...risk,notionalUsd:n}).decision,"DENY")});
const t=Date.now(), base={requestId:"r1",instrument:"SOL",positionSide:"long",size:100,maxAgeMs:2000,maxImpactBps:80,observations:[]};
const obs={venue:"jupiter",instrument:"SOL",positionSide:"long",executableSize:100,expectedOutputUsd:99,priceImpactBps:12,observedAt:t,source:"jupiter-route-quote",verified:true,walletOrAccountEligible:true};
test("exit planning ranks fresh eligible observations without executing",()=>{
 const res=planExit({...base,observations:[{...obs,venue:"hyperliquid",expectedOutputUsd:101},obs]},t);
 assert.equal(res.decision,"REVIEW_REQUIRED");assert.equal(res.routes[0].venue,"hyperliquid");assert.equal(res.executionAuthorized,false);
});
test("exit denies stale, insufficient, bad, candidate and ineligible routes",()=>{
 const cases=[{observedAt:t-3000},{executableSize:99},{verified:false},{walletOrAccountEligible:false},{venue:"drift"},{priceImpactBps:81},{instrument:"ETH"}];
 for(const patch of cases)assert.equal(planExit({...base,observations:[{...obs,...patch}]},t).routes.length,0);
});
test("unknown venue and empty list fail closed",()=>{assert.equal(planExit({...base,observations:[{...obs,venue:"unknown"}]},t).decision,"NO_VERIFIED_EXIT_ROUTE");assert.equal(planExit(base,t).decision,"NO_VERIFIED_EXIT_ROUTE")});
test("registry never asserts candidate execution",()=>{assert.equal(VENUES.drift.execution,"candidate-adapter");assert.equal(VENUES.gmx.execution,"candidate-adapter")});
test("orders are only plans",()=>assert.equal(planOrder(risk).planOnly,true));
