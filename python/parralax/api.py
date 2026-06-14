"""PARRALAX-AIHFTFUND FastAPI Gateway — REST + WebSocket API."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

from .agents import SignalAgent, RiskAgent, ExecutionAgent
from .agents.base import AgentCapital
from .paper_trading import PaperTradingEngine
from .registry import ProtocolRegistry, AgentRegistry
from .public_api import public_api_app

# Main app for internal trading systems
app = FastAPI(
    title="PARRALAX-AIHFTFUND Internal API",
    description="Sovereign AI-Native Financial Execution Infrastructure (Internal)",
    version="0.1.0",
)

# Register public API as sub-application
# Third-party AI systems access /api/v1/* endpoints
app.mount("/api/v1", public_api_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core systems
protocol_registry = ProtocolRegistry()
protocol_registry.initialize_core_protocols()

agent_registry = AgentRegistry()
paper_engine = PaperTradingEngine(initial_capital=1_000_000.0)

# Register default agents
signal_agent = SignalAgent("alpha-signal-001")
risk_agent = RiskAgent("risk-governor-001")
execution_agent = ExecutionAgent("executor-001")

agent_registry.register(signal_agent)
agent_registry.register(risk_agent)
agent_registry.register(execution_agent)


class OrderRequest(BaseModel):
    symbol: str
    side: str
    quantity: float
    price: float
    order_type: str = "market"
    agent_id: str = ""


class PriceUpdate(BaseModel):
    prices: dict[str, float]


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "system": "PARRALAX-AIHFTFUND",
        "version": "0.1.0",
        "status": "operational",
        "identity": "Sovereign AI-Native Financial Execution Infrastructure",
    }


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "agents": agent_registry.get_registry_state(),
        "protocols": len(protocol_registry.list_all()),
        "paper_engine": {
            "capital": paper_engine.capital,
            "positions": len(paper_engine.positions),
            "trade_count": paper_engine.trade_count,
        },
    }


@app.get("/protocols")
async def list_protocols() -> list[dict[str, Any]]:
    return [p.to_dict() for p in protocol_registry.list_all()]


@app.get("/agents")
async def list_agents() -> dict[str, Any]:
    return agent_registry.get_registry_state()


@app.post("/orders")
async def submit_order(order: OrderRequest) -> dict[str, Any]:
    # Risk validation
    valid, reason = risk_agent.validate_order({
        "symbol": order.symbol,
        "side": order.side,
        "quantity": order.quantity,
        "notional": order.quantity * order.price,
        "asset_class": "crypto",
    })

    if not valid:
        raise HTTPException(status_code=400, detail=f"Risk rejected: {reason}")

    # Paper trade execution
    fill = paper_engine.submit_order(
        symbol=order.symbol,
        side=order.side,
        quantity=order.quantity,
        price=order.price,
        order_type=order.order_type,
        agent_id=order.agent_id,
    )

    if not fill:
        raise HTTPException(status_code=400, detail="Order failed — insufficient capital")

    return {
        "fill_id": str(fill.id),
        "symbol": fill.symbol,
        "side": fill.side,
        "price": fill.price,
        "quantity": fill.quantity,
        "fee": fill.fee,
        "timestamp": fill.timestamp.isoformat(),
    }


@app.get("/portfolio")
async def get_portfolio() -> dict[str, Any]:
    return paper_engine.get_portfolio_state()


@app.post("/prices")
async def update_prices(update: PriceUpdate) -> dict[str, str]:
    paper_engine.update_prices(update.prices)
    return {"status": "updated"}


@app.get("/risk")
async def get_risk_report() -> dict[str, Any]:
    return risk_agent.get_risk_report()


@app.post("/kill-switch")
async def engage_kill_switch() -> dict[str, str]:
    agent_registry.kill_all()
    return {"status": "ALL AGENTS HALTED — kill switch engaged"}
