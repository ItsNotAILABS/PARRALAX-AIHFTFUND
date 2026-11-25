/** Non-signing deterministic pretrade policy. Caller inputs require trusted server authentication. */
const fail=(reason,blocks=[])=>({decision:"DENY",reason,blocks,executionAuthorized:false});
const n=x=>typeof x==="number"&&Number.isFinite(x)&&x>=0;
const p=x=>n(x)&&x>0;
const id=x=>typeof x==="string"&&/^[a-zA-Z0-9._:-]{1,128}$/.test(x);
const mint=x=>typeof x==="string"&&/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(x);
export const POLICY_VERSION="parralax.pretrade.v1";
export const AGENT_ROLES=Object.freeze([
 {id:"market-data-qa",capabilities:["observe","quarantine-feed"]},
 {id:"liquidity-scout",capabilities:["observe","compare-venues"]},
 {id:"volatility-regime",capabilities:["observe","propose-strategy"]},
 {id:"execution-cost-analyst",capabilities:["observe","estimate-cost"]},
 {id:"portfolio-risk",capabilities:["observe","deny-proposal"]},
 {id:"funding-basis",capabilities:["observe","track-funding"]},
 {id:"treasury-governor",capabilities:["observe","deny-proposal"]},
 {id:"order-proposer",capabilities:["observe","propose-order"]}
]);
export function evaluatePretrade({order:o,portfolio:v,market:m,limits:l,evidence:e},now=Date.now()){
 if(!o||!v||!m||!l||!e||!Number.isSafeInteger(now))return fail("MISSING_EVIDENCE");
 if(!id(o.requestId)||!id(o.tenantId)||!id(o.agentId)||!id(o.venue)||!mint(o.mint)||
 !["buy","sell","long","short","close","reduce"].includes(o.side)||!p(o.notionalUsd)||
 !p(o.leverage)||!n(o.priceImpactBps)||!n(o.slippageBps)||
 !p(v.equityUsd)||!p(v.dayStartEquityUsd)||!p(v.peakEquityUsd)||
 !n(v.exposureUsd)||!n(v.dailyTurnoverUsd)||!n(v.reservedUsd)||!n(v.openOrders)||
 !n(m.spreadBps)||!n(m.liquidityUsd)||!n(m.oracleObservedAtMs)||
 !id(e.quoteId)||!id(e.issuerId)||!n(e.observedAtMs)||
 !p(l.maxOrderUsd)||!p(l.maxGrossUsd)||!p(l.maxTurnoverUsd)||
 !n(l.maxDailyLossPct)||!n(l.maxDrawdownPct)||!p(l.maxLeverage)||
 !n(l.maxImpactBps)||!n(l.maxSpreadBps)||!p(l.maxQuoteAgeMs)||
 !p(l.maxOracleAgeMs)||!n(l.maxOpenOrders)||!p(l.minLiquidityUsd)||
 !Array.isArray(l.allowedVenues)||!Array.isArray(l.allowedMints)||!Array.isArray(l.allowedSides))
 return fail("INVALID_EVIDENCE");
 const blocked=[],check=(condition,reason)=>{if(condition)blocked.push(reason)};
 check(!l.allowedVenues.includes(o.venue),"VENUE");
 check(!l.allowedMints.includes(o.mint),"MINT");
 check(!l.allowedSides.includes(o.side),"SIDE");
 check(o.notionalUsd>l.maxOrderUsd,"ORDER_LIMIT");
 check(o.leverage>l.maxLeverage,"LEVERAGE_LIMIT");
 check(o.priceImpactBps>l.maxImpactBps||o.slippageBps>l.maxImpactBps,"IMPACT_SLIPPAGE");
 check(m.spreadBps>l.maxSpreadBps,"SPREAD");
 check(m.liquidityUsd<l.minLiquidityUsd,"ILLIQUID");
 check(e.observedAtMs>now||now-e.observedAtMs>l.maxQuoteAgeMs,"QUOTE_STALE");
 check(m.oracleObservedAtMs>now||now-m.oracleObservedAtMs>l.maxOracleAgeMs,"ORACLE_STALE");
 check(e.issuerPolicyVersion!==POLICY_VERSION||e.trustedIngestion!==true||
       e.principalEligible!==true,"UNVERIFIED_EVIDENCE");
 check(m.oracleHealthy!==true||m.halted===true,"HALT_OR_ORACLE");
 const dailyLoss=Math.max(0,(v.dayStartEquityUsd-v.equityUsd)/v.dayStartEquityUsd);
 const drawdown=Math.max(0,(v.peakEquityUsd-v.equityUsd)/v.peakEquityUsd);
 check(v.equityUsd>v.peakEquityUsd*1.01,"INCONSISTENT_PEAK");
 check(dailyLoss>l.maxDailyLossPct,"DAILY_STOP");
 check(drawdown>l.maxDrawdownPct,"DRAWDOWN_STOP");
 if(["buy","long","short"].includes(o.side)){
  check(v.exposureUsd+v.reservedUsd+o.notionalUsd>l.maxGrossUsd,"EXPOSURE");
  check(v.openOrders>=l.maxOpenOrders,"OPEN_ORDERS");
 }
 check(v.dailyTurnoverUsd+o.notionalUsd>l.maxTurnoverUsd,"TURNOVER");
 if(blocked.length)return fail("RISK_GATES_FAILED",blocked);
 return {decision:"APPROVAL_REQUIRED",policyVersion:POLICY_VERSION,requestId:o.requestId,
  tenantId:o.tenantId,agentId:o.agentId,venue:o.venue,quoteId:e.quoteId,
  dailyLossPct:dailyLoss,drawdownPct:drawdown,executionAuthorized:false,
  requiresFreshRequote:true,requiresAtomicBudgetReservation:true,
  requiresIndependentSimulation:true,requiresWalletOrProgramSignature:true,
  warning:"No profitable execution or guaranteed exit implied."};
}
