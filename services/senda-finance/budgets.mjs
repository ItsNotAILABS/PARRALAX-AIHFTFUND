/**
 * Deterministic budget decision; no on-chain enforcement or balance reservation.
 * All input facts MUST be sourced by a trusted caller from durable ledger/policy storage.
 */
const goodNumber=x=>typeof x==="number"&&Number.isSafeInteger(x)&&x>=0;
const goodId=x=>typeof x==="string"&&/^[a-zA-Z0-9._:-]{1,128}$/.test(x);
export function evaluateAgentBudget(input, now=Date.now()){
 const deny=(reason)=>({decision:"DENY",reason,executionAuthorized:false,requiresUserSignature:true});
 if(!input||!goodId(input.tenantId)||!goodId(input.organismId)||!goodId(input.policyId)||
   !goodId(input.requestId)||!goodId(input.beneficiaryId)||!goodId(input.asset)||
   !goodNumber(input.amountMinor)||input.amountMinor===0||
   !goodNumber(input.maxPerTransactionMinor)||!goodNumber(input.totalBudgetMinor)||
   !goodNumber(input.usedBudgetMinor)||!goodNumber(input.reservedBudgetMinor)||
   !Number.isSafeInteger(input.expiresAt)||!Number.isSafeInteger(now)||
   !Array.isArray(input.allowedBeneficiaries)||!Array.isArray(input.allowedAssets)||
   !goodId(input.requestNonce))
   return deny("INVALID_BUDGET_EVIDENCE");
 if(input.revoked===true)return deny("REVOKED");
 if(now>=input.expiresAt)return deny("EXPIRED");
 if(!input.allowedBeneficiaries.includes(input.beneficiaryId))return deny("BENEFICIARY_DENIED");
 if(!input.allowedAssets.includes(input.asset))return deny("ASSET_DENIED");
 if(input.amountMinor>input.maxPerTransactionMinor)return deny("PER_TRANSACTION_CAP");
 if(input.usedBudgetMinor+input.reservedBudgetMinor+input.amountMinor>input.totalBudgetMinor)return deny("CUMULATIVE_CAP");
 if(input.nonceUnused!==true)return deny("REPLAY_OR_NONCE_NOT_VERIFIED");
 if(input.policyVerified!==true||input.ledgerVerified!==true)return deny("UNVERIFIED_POLICY_OR_LEDGER");
 return {decision:"REVIEW_REQUIRED",reason:"BUDGET_WITHIN_POLICY",executionAuthorized:false,
  requiresUserSignature:true,requestId:input.requestId,policyId:input.policyId,
  budgetReservationCreated:false};
}
