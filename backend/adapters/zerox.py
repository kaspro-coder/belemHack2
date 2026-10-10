import os
import httpx
from typing import Optional

async def get_0x_quote_slippage() -> Optional[float]:
    """
    Fetch a 0x Swap API v2 quote and extract estimated price impact.
    We separate price impact from slippage. For Phase 1 we return price impact 
    as the slippage metric if possible, otherwise None.
    
    Returns:
        float: price impact as a decimal (e.g. 0.01 for 1%) if available.
        None: if no reliable measurement is available or API fails.
    """
    api_key = os.getenv("ZEROX_API_KEY")
    sell_token = os.getenv("OXX_SELL_TOKEN")
    buy_token = os.getenv("OXX_BUY_TOKEN")
    trade_amount = os.getenv("OXX_TRADE_AMOUNT")
    chain_id = os.getenv("OXX_CHAIN_ID")
    taker_address = os.getenv("OXX_TAKER_ADDRESS", "0x0000000000000000000000000000000000000000")

    if not all([api_key, sell_token, buy_token, trade_amount, chain_id]):
        return None

    # Using the permitted v2 endpoint
    # Required params for v2 depending on endpoint, usually sellToken, buyToken, sellAmount, taker
    url = "https://api.0x.org/swap/permit2/quote"
    params = {
        "chainId": chain_id,
        "sellToken": sell_token,
        "buyToken": buy_token,
        "sellAmount": trade_amount,
        "taker": taker_address
    }
    
    headers = {
        "0x-api-key": api_key,
        "0x-version": "v2",
        "accept": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Extract estimated price impact if present
            # 0x docs: v2 may or may not return estimatedPriceImpact
            price_impact = data.get("estimatedPriceImpact")
            if price_impact is not None:
                return float(price_impact) / 100.0 if float(price_impact) > 1 else float(price_impact)
            
            return None
    except Exception:
        # Graceful degradation on API failure, timeout, auth issue
        return None
