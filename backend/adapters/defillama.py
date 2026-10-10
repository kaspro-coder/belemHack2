import httpx
from typing import Optional

async def get_protocol_tvl(slug: str) -> Optional[float]:
    """
    Fetch the total TVL for a given protocol slug from DefiLlama.
    Used for metadata enrichment only, separate from modeled exposure.
    
    Args:
        slug: The defillama protocol slug (e.g. 'aave-v3')
    Returns:
        float TVL if successful, None if unknown slug or HTTP error.
    """
    if not slug:
        return None

    url = f"https://api.llama.fi/tvl/{slug}"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            # current-TVL endpoint returns a plain number
            tvl_str = response.text.strip()
            return float(tvl_str)
    except Exception:
        return None
