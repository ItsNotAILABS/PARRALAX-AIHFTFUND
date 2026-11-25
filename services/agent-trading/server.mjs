/**
 * Private PARRALAX agent pretrade HTTP service.
 * Only trusted backend policy/evidence resolvers can satisfy the risk engine.
 * No market data or approval facts are accepted from agent-supplied request JSON.
 */
import http from "node:http";
import {createHash,timingSafeEqual} from "node:crypto";
import {evaluatePretrade} from "./pretrade.mjs";
function constantTimeToken(header,secret){
 if(typeof secret!=="string"||secret.length<32||typeof header!=="string"||!header.startsWith("Bearer "))return false;
 return timingSafeEqual(createHash("sha256").update(header.slice(7)).digest(),
                       createHash("sha256").update(secret).digest());
}
function response(res,status,body){
 res.writeHead(status,{"content-type":"application/json; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff"});
 res.end(JSON.stringify(body));
}
export function createPretradeServer({serviceToken,loadTrustedContext,audit=()=>{},now=Date.now}={}){
 if(typeof serviceToken!=="string"||serviceToken.length<32)throw Error("Strong service token required");
 if(typeof loadTrustedContext!=="function")throw Error("Trusted context resolver is required");
 return http.createServer(async(req,res)=>{
  if(!constantTimeToken(req.headers.authorization,serviceToken))
   return response(res,401,{schema:"parralax.pretrade.response.v1",decision:"DENY",reason:"UNAUTHORIZED"});
  if(req.url==="/healthz"&&req.method==="GET")
   return response(res,200,{service:"parralax-agent-pretrade",state:"running",executionEnabled:false});
  if(req.url!=="/v1/agents/pretrade"||req.method!=="POST")
   return response(res,404,{reason:"NOT_FOUND"});
  let raw="";
  try{
   for await(const chunk of req){
    raw+=chunk;
    if(raw.length>32000)return response(res,413,{decision:"DENY",reason:"REQUEST_TOO_LARGE"});
   }
   const data=JSON.parse(raw);
   const order=data?.order;
   if(data?.schema!=="senda.pretrade.request.v1"||!order||typeof order!=="object"||Array.isArray(order))
    return response(res,400,{decision:"DENY",reason:"INVALID_REQUEST"});
   // The resolver must read durable tenant policy, P&L and quote/oracle evidence.
   // Caller-supplied limits, market and portfolio are discarded.
   const context=await loadTrustedContext({
    tenantId:order.tenantId,agentId:order.agentId,requestId:order.requestId,
    venue:order.venue,mint:order.mint,quoteId:data.quoteId,principal:req.headers["x-service-principal"]
   });
   const result=evaluatePretrade({order,portfolio:context.portfolio,market:context.market,
    limits:context.limits,evidence:context.evidence},now());
   await audit({at:now(),requestId:order.requestId,tenantId:order.tenantId,
    agentId:order.agentId,decision:result.decision,reason:result.reason??result.policyVersion,
    executionAuthorized:false});
   return response(res,200,{schema:"parralax.pretrade.response.v1",requestId:order.requestId,...result});
  }catch{
   return response(res,503,{schema:"parralax.pretrade.response.v1",decision:"DENY",reason:"TRUSTED_EVIDENCE_UNAVAILABLE",executionAuthorized:false});
  }
 });
}
