"""
DeFi Risk Dependency Analyzer — Phase 2 Backend

Includes explicit response updates for Phase 2:
- nodes, edges
- warnings, data_provenance
- null slippage handling
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional, List
from dotenv import load_dotenv

# Adapters
from adapters.zerox import get_0x_quote_slippage
from adapters.defillama import get_protocol_tvl
from adapters.web3_onchain import check_onchain_dependency
from graph import Node, Edge, get_fallback_graph, calculate_expected_loss

load_dotenv()

app = FastAPI(title="DeFi Risk Dependency Analyzer", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ACTION_THRESHOLD = 30_000

# -----------------
# Models
# -----------------

class AnalyzeRequest(BaseModel):
    token_address: str

    @field_validator("token_address")
    @classmethod
    def address_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("token_address must not be empty or whitespace-only")
        return stripped

class AnalyzeResponse(BaseModel):
    status: str
    token_address: str
    slippage: Optional[float]
    expected_loss: float
    action: str
    warnings: List[str]
    data_provenance: str
    nodes: List[dict]
    edges: List[dict]


# -----------------
# Routes
# -----------------

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_token(request: AnalyzeRequest):
    warnings = []

    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    
    if demo_mode:
        slippage = None
        warnings.append("DEMO MODE ON: Fetching state from Local Anvil Blockchain.")
        data_provenance = "LOCAL_EVM_RPC"
        try:
            from adapters.web3_onchain import get_demo_graph
            nodes, edges = await get_demo_graph()
        except Exception as e:
            warnings.append(f"Anvil node failed: {e}")
            raise # Fail loudly
    else:
        # 1. 0x API Slippage Request
        slippage = await get_0x_quote_slippage()
        if slippage is None:
            warnings.append("0x API Quote failed or estimatedPriceImpact unavailable. Slippage is N/A.")

        # 2. Check On-Chain
        on_chain_found = await check_onchain_dependency(request.token_address)
        
        if on_chain_found:
            data_provenance = "ON_CHAIN_DISCOVERY"
            # In a real system, we'd build graph from bytecode discovery here.
            # For checkpoint, we'll mark a warning that we only found it, but no deep discovery logic yet.
            warnings.append("On-chain contract found, but deep discovery is mock for now.")
            nodes, edges = get_fallback_graph()
        else:
            data_provenance = "FALLBACK_SIMULATION"
            nodes, edges = get_fallback_graph()
            warnings.append("On-chain discovery failed. Using local fallback 5-layer dependency graph.")

        # 3. DefiLlama enrichment (optional for nodes)
        tvl = await get_protocol_tvl("aave-v3")
        if tvl is not None:
            for n in nodes:
                if n.id == "L2":
                    n.tvl = tvl
        else:
            warnings.append("DefiLlama API failed. Some metadata TVL values may be 0.")

    # 4. Expected Loss calculation
    # Simulate compromise on L3
    expected_loss = calculate_expected_loss(nodes, edges, compromised_node_id="L3")

    action = "EXIT" if expected_loss > ACTION_THRESHOLD else "STAY"

    return AnalyzeResponse(
        status="success",
        token_address=request.token_address,
        slippage=slippage,
        expected_loss=expected_loss,
        action=action,
        warnings=warnings,
        data_provenance=data_provenance,
        nodes=[n.model_dump() for n in nodes],
        edges=[e.model_dump() for e in edges],
    )
