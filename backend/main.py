"""
DeFi Risk Dependency Analyzer — Phase 1 Backend
FastAPI server with mock analysis endpoint.

All returned values are illustrative mock data.
They do not represent actual DeFi risk estimates.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

app = FastAPI(title="DeFi Risk Dependency Analyzer", version="0.1.0")

# ---------------------------------------------------------------------------
# CORS — allow the Next.js dev server
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Illustrative action threshold (USD).
# If expected_loss > ACTION_THRESHOLD the recommended action is EXIT.
# ---------------------------------------------------------------------------
ACTION_THRESHOLD = 30_000

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

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
    slippage: float
    expected_loss: float
    action: str

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Simple liveness probe."""
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_token(request: AnalyzeRequest):
    """
    Accept a token address and return mock risk metrics.
    Real blockchain analysis will replace this in a later phase.
    """
    # --- Mock analysis logic (deterministic) ---
    slippage = 0.11
    expected_loss = 50_000.0
    action = "EXIT" if expected_loss > ACTION_THRESHOLD else "STAY"

    return AnalyzeResponse(
        status="success",
        token_address=request.token_address,
        slippage=slippage,
        expected_loss=expected_loss,
        action=action,
    )
