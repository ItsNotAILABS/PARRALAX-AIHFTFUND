/** Objective post-trade cost measurement, not performance prediction. */
const positive=x=>typeof x==="number"&&Number.isFinite(x)&&x>0;
const nonnegative=x=>typeof x==="number"&&Number.isFinite(x)&&x>=0;
export function transactionCostReceipt(fill){
 const bad=reason=>({status:"INVALID",reason,verified:false});
 if(!fill||!["buy","sell"].includes(fill.side)||!positive(fill.arrivalMidUsd)||
  !positive(fill.fillPriceUsd)||!positive(fill.filledUnits)||
  !positive(fill.requestedUnits)||fill.filledUnits>fill.requestedUnits||
  !nonnegative(fill.venueFeeUsd)||!nonnegative(fill.networkFeeUsd)||
  !nonnegative(fill.fundingUsd)||!Number.isSafeInteger(fill.arrivalTimeMs)||
  !Number.isSafeInteger(fill.fillTimeMs)||fill.fillTimeMs<fill.arrivalTimeMs||
  typeof fill.venue!=="string"||fill.venue.length<2||
  typeof fill.receiptId!=="string"||fill.receiptId.length<2)
  return bad("INVALID_FILL_EVIDENCE");
 if(fill.confirmationVerified!==true||fill.ledgerReconciled!==true)
  return bad("CONFIRMATION_OR_LEDGER_NOT_VERIFIED");
 const direction=fill.side==="buy"?1:-1;
 const notionalUsd=fill.arrivalMidUsd*fill.filledUnits;
 const priceShortfallUsd=direction*(fill.fillPriceUsd-fill.arrivalMidUsd)*fill.filledUnits;
 const explicitCostsUsd=fill.venueFeeUsd+fill.networkFeeUsd+fill.fundingUsd;
 const totalCostUsd=priceShortfallUsd+explicitCostsUsd;
 return {status:"RECONCILED",verified:true,receiptId:fill.receiptId,venue:fill.venue,
  side:fill.side,fillRatio:fill.filledUnits/fill.requestedUnits,
  arrivalNotionalUsd:notionalUsd,priceShortfallUsd,explicitCostsUsd,
  implementationShortfallUsd:totalCostUsd,
  implementationShortfallBps:totalCostUsd/notionalUsd*10000,
  latencyMs:fill.fillTimeMs-fill.arrivalTimeMs,
  note:"Negative shortfall indicates price improvement; this is execution cost, not strategy alpha."};
}
export function summarizeExecutionQuality(receipts){
 if(!Array.isArray(receipts)||!receipts.length)return {status:"NO_RECONCILED_FILLED_TRADES",sampleCount:0};
 const accepted=receipts.filter(r=>r?.status==="RECONCILED"&&r.verified===true&&
  positive(r.arrivalNotionalUsd)&&Number.isFinite(r.implementationShortfallUsd)&&
  nonnegative(r.latencyMs));
 if(!accepted.length)return {status:"NO_RECONCILED_FILLED_TRADES",sampleCount:0};
 const usd=accepted.reduce((s,r)=>s+r.arrivalNotionalUsd,0);
 const cost=accepted.reduce((s,r)=>s+r.implementationShortfallUsd,0);
 const latency=[...accepted].map(r=>r.latencyMs).sort((a,b)=>a-b);
 return {status:"OBSERVED",sampleCount:accepted.length,arrivalNotionalUsd:usd,
  totalImplementationShortfallUsd:cost,weightedCostBps:cost/usd*10000,
  medianLatencyMs:latency[Math.floor((latency.length-1)/2)],
  note:"Selection-biased executed fills only; does not include rejected orders or opportunity cost."};
}
