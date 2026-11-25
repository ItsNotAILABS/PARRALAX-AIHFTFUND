/** Bounded market research worker coordinator. No wallet or transaction execution. */
import {createHash} from "node:crypto";
import {AGENT_ROLES} from "./pretrade.mjs";
const roles=new Set(AGENT_ROLES.map(r=>r.id));
const required=["market-data-qa","liquidity-scout","portfolio-risk"];
export async function runResearchSwarm({requestId,tenantId,symbol,workers,context,timeoutMs=5000}={}){
 if(typeof requestId!=="string"||!/^[A-Za-z0-9._:-]{1,128}$/.test(requestId)||
  typeof tenantId!=="string"||!/^[A-Za-z0-9._:-]{1,128}$/.test(tenantId)||
  typeof symbol!=="string"||!/^[A-Za-z0-9._:-]{2,40}$/.test(symbol)||
  !workers||typeof workers!=="object"||!context||typeof context!=="object"||
  !Number.isSafeInteger(timeoutMs)||timeoutMs<100||timeoutMs>30000)
  return {status:"DENY",reason:"INVALID_RESEARCH_CONTEXT",executionAuthorized:false};
 const entries=Object.entries(workers).filter(([role,run])=>roles.has(role)&&typeof run==="function");
 if(entries.length===0||entries.length>AGENT_ROLES.length||
  required.some(role=>!entries.some(([name])=>name===role)))
  return {status:"DENY",reason:"REQUIRED_WORKERS_MISSING",executionAuthorized:false};
 const snapshots=Object.freeze({requestId,tenantId,symbol,context:Object.freeze({...context})});
 const receipts=await Promise.all(entries.map(async([role,run])=>{
  try{
   const output=await run(snapshots,{signal:AbortSignal.timeout(timeoutMs)});
   if(!output||typeof output!=="object"||!["PASS","VETO","UNKNOWN"].includes(output.state))
    throw Error("INVALID_WORKER_OUTPUT");
   if(output.canSign===true||output.executionAuthorized===true||output.transaction!=null)
    throw Error("WORKER_ATTEMPTED_ESCALATION");
   return {role,state:output.state,summary:String(output.summary||"").slice(0,400),
    sourceId:String(output.sourceId||"").slice(0,128)};
  }catch{return {role,state:"UNKNOWN",summary:"Worker failed or returned unauthorized output",sourceId:""};}
 }));
 const missing=required.filter(role=>!receipts.some(r=>r.role===role&&r.state==="PASS"));
 const veto=receipts.filter(r=>r.state==="VETO").map(r=>r.role);
 const status=missing.length||veto.length?"HOLD":"REVIEW";
 const digest=createHash("sha256").update(JSON.stringify({requestId,tenantId,symbol,receipts})).digest("hex");
 return Object.freeze({schema:"parralax.research-swarm.v1",status,requestId,tenantId,symbol,
  receipts,missing,veto,evidenceSha256:digest,executionAuthorized:false,
  note:"Research-only receipt; sourceId values must be independently verified by the trading backend."});
}
