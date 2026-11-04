import { createHash } from "node:crypto";
export const VENUES = Object.freeze({
  jupiter: { chain: "solana", kind: "perpetual", execution: "wallet-signed-senda-adapter", assets: ["SOL","ETH","BTC"] },
  drift: { chain: "solana", kind: "perpetual", execution: "candidate-adapter", assets: [] },
  hyperliquid: { chain: "hyperliquid", kind: "perpetual", execution: "separate-existing-senda-adapter", assets: [] },
  ostium: { chain: "arbitrum", kind: "perpetual", execution: "separate-existing-senda-adapter", assets: [] },
  monad: { chain: "monad", kind: "perpetual", execution: "separate-existing-senda-adapter", assets: [] },
  dYdX: { chain: "dydx", kind: "perpetual", execution: "candidate-adapter", assets: [] },
  gmx: { chain: "arbitrum", kind: "perpetual", execution: "candidate-adapter", assets: [] }
});
export const finitePositive = x => typeof x === "number" && Number.isFinite(x) && x > 0;
const validSymbol = x => typeof x === "string" && /^[A-Z0-9._:-]{2,32}$/.test(x);
const validId = x => typeof x === "string" && /^[a-zA-Z0-9._:-]{1,128}$/.test(x);
export function evaluateRisk(p) {
  if (!p || !validSymbol(p.instrument) || !["long","short","spot-buy","spot-sell"].includes(p.side) ||
      !finitePositive(p.notionalUsd) || !finitePositive(p.maxNotionalUsd) ||
      !finitePositive(p.leverage) || !finitePositive(p.maxLeverage) ||
      !Number.isFinite(p.quoteAgeMs) || p.quoteAgeMs < 0 ||
      !Number.isFinite(p.maxQuoteAgeMs) || p.maxQuoteAgeMs < 0 ||
      !Number.isFinite(p.priceImpactBps) || p.priceImpactBps < 0 ||
      !Number.isFinite(p.maxImpactBps) || p.maxImpactBps < 0) {
    return { decision: "DENY", reasons: ["INVALID_OR_MISSING_RISK_INPUT"], executionAuthorized: false };
  }
  const reasons = [];
  if (p.notionalUsd > p.maxNotionalUsd) reasons.push("NOTIONAL_LIMIT");
  if (p.leverage > p.maxLeverage) reasons.push("LEVERAGE_LIMIT");
  if (p.quoteAgeMs > p.maxQuoteAgeMs) reasons.push("STALE_QUOTE");
  if (p.priceImpactBps > p.maxImpactBps) reasons.push("EXCESSIVE_PRICE_IMPACT");
  if (p.marketHalted === true) reasons.push("MARKET_HALTED");
  if (p.oracleHealthy !== true) reasons.push("ORACLE_NOT_VERIFIED");
  if (p.venueEligible !== true) reasons.push("VENUE_ELIGIBILITY_UNVERIFIED");
  if (p.walletAuthorized !== true) reasons.push("WALLET_APPROVAL_REQUIRED");
  return { decision: reasons.length ? "DENY" : "PASS_TO_WALLET_REVIEW", reasons, executionAuthorized: false };
}
/** Evidence-only route comparison. Never creates a fill or swaps a token. */
export function planExit(input, now = Date.now()) {
  if (!input || !validId(input.requestId) || !validSymbol(input.instrument) ||
      !["long","short","spot"].includes(input.positionSide) || !finitePositive(input.size) ||
      !Number.isFinite(input.maxAgeMs) || input.maxAgeMs < 0 ||
      !Number.isFinite(input.maxImpactBps) || input.maxImpactBps < 0 ||
      !Array.isArray(input.observations)) {
    return { decision: "DENY", reasons: ["INVALID_EXIT_REQUEST"], routes: [], executionAuthorized: false };
  }
  const rejected = []; const routes = [];
  for (const x of input.observations.slice(0, 64)) {
    const valid = x && typeof x.venue === "string" && Object.hasOwn(VENUES, x.venue) &&
      x.instrument === input.instrument && x.positionSide === input.positionSide &&
      finitePositive(x.executableSize) && finitePositive(x.expectedOutputUsd) &&
      Number.isFinite(x.priceImpactBps) && x.priceImpactBps >= 0 &&
      Number.isFinite(x.observedAt) && x.observedAt <= now &&
      typeof x.source === "string" && x.source.length > 4 &&
      x.walletOrAccountEligible === true && x.verified === true &&
      VENUES[x.venue].execution !== "candidate-adapter";
    if (!valid) { rejected.push({ venue: String(x?.venue ?? "unknown"), reason: "INVALID_OR_UNVERIFIED_OBSERVATION" }); continue; }
    if (now - x.observedAt > input.maxAgeMs) { rejected.push({ venue: x.venue, reason: "STALE_OBSERVATION" }); continue; }
    if (x.priceImpactBps > input.maxImpactBps) { rejected.push({ venue: x.venue, reason: "IMPACT_LIMIT" }); continue; }
    if (x.executableSize < input.size) { rejected.push({ venue: x.venue, reason: "INSUFFICIENT_QUOTED_SIZE" }); continue; }
    routes.push({ venue: x.venue, instrument: x.instrument, source: x.source,
      expectedOutputUsd: x.expectedOutputUsd, priceImpactBps: x.priceImpactBps,
      observedAt: x.observedAt, executableSize: x.executableSize, quoteId: x.quoteId ?? null });
  }
  routes.sort((a,b)=>b.expectedOutputUsd-a.expectedOutputUsd || a.priceImpactBps-b.priceImpactBps);
  const evidenceHash = createHash("sha256").update(JSON.stringify({ requestId: input.requestId, routes, rejected })).digest("hex");
  return { decision: routes.length ? "REVIEW_REQUIRED" : "NO_VERIFIED_EXIT_ROUTE",
    reasons: routes.length ? ["WALLET_SIGNATURE_AND_FRESH_REQUOTE_REQUIRED"] : ["NO_ELIGIBLE_FRESH_ROUTE"],
    routes, rejected, evidenceHash, executionAuthorized: false, requiresFreshQuote: true };
}
export function research(payload) {
  return { state: "registry-only", venues: VENUES, instrument: payload?.instrument ?? null,
    warning: "Venue presence does not establish live connection, pricing, eligibility or executable orders." };
}
export function planOrder(payload) {
  const risk = evaluateRisk(payload);
  return { ...risk, planOnly: true, requiresFreshQuote: true, walletSignatureRequired: true };
}
