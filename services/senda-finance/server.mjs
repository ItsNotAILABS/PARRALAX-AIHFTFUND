import http from "node:http";
import { timingSafeEqual, createHash } from "node:crypto";
import { evaluateRisk, planExit, planOrder, research } from "./core.mjs";
import { evaluateAgentBudget } from "./budgets.mjs";
function authorized(raw, token) {
  if (!token || token.length < 32 || !raw?.startsWith("Bearer ")) return false;
  return timingSafeEqual(createHash("sha256").update(raw.slice(7)).digest(),createHash("sha256").update(token).digest());
}
export function createFinanceServer({ token, now = Date.now, audit = () => {} }) {
  if (!token || token.length < 32) throw Error("Use a strong service credential");
  const handlers = {
    "/v1/market/research": research,
    "/v1/risk/evaluate": evaluateRisk,
    "/v1/execution/plan": planOrder,
    "/v1/execution/exit-plan": (p) => planExit(p, now()),
    "/v1/agents/budget-evaluate": (p) => evaluateAgentBudget(p,now())
  };
  return http.createServer(async (req,res)=>{
    const answer = (status,body)=>{res.writeHead(status,{"content-type":"application/json","cache-control":"no-store"});res.end(JSON.stringify(body));};
    if(req.method==="GET" && req.url==="/healthz") return answer(200,{ service:"parralax-senda-finance", state:"up", tradingEnabled:false });
    if (!authorized(req.headers.authorization,token)) return answer(401,{error:"UNAUTHORIZED"});
    if (req.method!=="POST" || !Object.hasOwn(handlers,req.url)) return answer(404,{error:"UNIMPLEMENTED_ROUTE"});
    let raw="";for await(const c of req){raw+=c;if(raw.length>70000)return answer(413,{error:"TOO_LARGE"});}
    let input;try{input=JSON.parse(raw)}catch{return answer(400,{error:"INVALID_JSON"})}
    if(input?.schema!=="senda.parralax.request.v1"||typeof input.requestId!=="string"||input.requestId.length>128||!input.requestId||
      !input.payload||typeof input.payload!=="object"||Array.isArray(input.payload))
      return answer(400,{error:"INVALID_CONTRACT"});
    const result=handlers[req.url](input.payload);
    audit({requestId:input.requestId,path:req.url,decision:result.decision??result.state,at:now()});
    return answer(200,{schema:"parralax.response.v1",requestId:input.requestId,kind:"non-executing-analysis", result});
  });
}
if(process.argv[1] && import.meta.url===new URL("file://"+process.argv[1]).href){
  const server=createFinanceServer({token:process.env.PARRALAX_SENDA_SERVICE_TOKEN,
    audit: event=>process.stdout.write(JSON.stringify({type:"parralax-finance-audit",...event})+"\n")});
  server.listen(Number(process.env.PORT||8790),process.env.HOST||"127.0.0.1");
}
