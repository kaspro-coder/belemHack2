import pytest
import respx
import httpx
from adapters.zerox import get_0x_quote_slippage
from adapters.defillama import get_protocol_tvl
import os

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("ZEROX_API_KEY", "test_key")
    monkeypatch.setenv("OXX_SELL_TOKEN", "0xSell")
    monkeypatch.setenv("OXX_BUY_TOKEN", "0xBuy")
    monkeypatch.setenv("OXX_TRADE_AMOUNT", "1000")
    monkeypatch.setenv("OXX_CHAIN_ID", "1")
    monkeypatch.setenv("OXX_TAKER_ADDRESS", "0xTaker")

@pytest.mark.asyncio
@respx.mock
async def test_get_0x_quote_success():
    respx.get("https://api.0x.org/swap/permit2/quote").mock(
        return_value=httpx.Response(200, json={"estimatedPriceImpact": "1.5"})
    )
    slippage = await get_0x_quote_slippage()
    # 1.5 -> 0.015
    assert slippage == 0.015

@pytest.mark.asyncio
@respx.mock
async def test_get_0x_quote_no_impact_returned():
    respx.get("https://api.0x.org/swap/permit2/quote").mock(
        return_value=httpx.Response(200, json={"liquidity": "lots"}) # Missing estimatedPriceImpact
    )
    slippage = await get_0x_quote_slippage()
    assert slippage is None

@pytest.mark.asyncio
@respx.mock
async def test_get_0x_quote_api_failure():
    respx.get("https://api.0x.org/swap/permit2/quote").mock(
        return_value=httpx.Response(400, json={"error": "bad request"})
    )
    slippage = await get_0x_quote_slippage()
    assert slippage is None

@pytest.mark.asyncio
@respx.mock
async def test_get_defillama_tvl_success():
    respx.get("https://api.llama.fi/tvl/aave-v3").mock(
        return_value=httpx.Response(200, text="1234567.89")
    )
    tvl = await get_protocol_tvl("aave-v3")
    assert tvl == 1234567.89

@pytest.mark.asyncio
@respx.mock
async def test_get_defillama_tvl_failure():
    respx.get("https://api.llama.fi/tvl/unknown-slug").mock(
        return_value=httpx.Response(404, text="Not found")
    )
    tvl = await get_protocol_tvl("unknown-slug")
    assert tvl is None
