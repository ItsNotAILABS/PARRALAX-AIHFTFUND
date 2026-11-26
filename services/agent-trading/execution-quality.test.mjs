import test from "node:test";
import assert from "node:assert/strict";
import {transactionCostReceipt,summarizeExecutionQuality} from "./execution-quality.mjs";
const base={receiptId:"tx1",venue:"jupiter",side:"buy",arrivalMidUsd:100,fillPriceUsd:100.25,
 filledUnits:5,requestedUnits:10,venueFeeUsd:0.2,networkFeeUsd:0.01,fundingUsd:0,
 arrivalTimeMs:1800000000000,fillTimeMs:1800000001250,confirmationVerified:true,ledgerReconciled:true};
test("reconciled partial fill uses observed executed units",()=>{
 const r=transactionCostReceipt(base);
 assert.equal(r.status,"RECONCILED");assert.equal(r.fillRatio,0.5);
 assert.equal(r.arrivalNotionalUsd,500);assert.equal(r.latencyMs,1250);
 assert.ok(r.implementationShortfallUsd>1.4&&r.implementationShortfallUsd<1.5);
});
test("negative shortfall is price improvement, not return",()=>{
 const r=transactionCostReceipt({...base,fillPriceUsd:99,venueFeeUsd:0,networkFeeUsd:0});
 assert.ok(r.implementationShortfallUsd<0);
});
test("sell direction is handled separately",()=>{
 const r=transactionCostReceipt({...base,side:"sell",fillPriceUsd:99.5});
 assert.ok(r.priceShortfallUsd>0);
});
test("not reconciled means unverified",()=>{
 for(const patch of [{confirmationVerified:false},{ledgerReconciled:false},{filledUnits:11},
 {filledUnits:0},{arrivalMidUsd:0},{venueFeeUsd:-1},{fillTimeMs:0}]){
  assert.equal(transactionCostReceipt({...base,...patch}).verified,false);
 }
});
test("weighted aggregate excludes bad receipts",()=>{
 const valid=transactionCostReceipt(base);
 const summary=summarizeExecutionQuality([valid,{status:"INVALID",verified:false}]);
 assert.equal(summary.status,"OBSERVED");assert.equal(summary.sampleCount,1);
 assert.equal(summary.weightedCostBps,valid.implementationShortfallBps);
 assert.equal(summarizeExecutionQuality([]).status,"NO_RECONCILED_FILLED_TRADES");
});
