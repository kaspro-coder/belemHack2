import os
from web3 import AsyncWeb3
import json
from graph import Node, Edge

async def check_onchain_dependency(target_address: str) -> bool:
    """
    Attempt to connect to Web3 RPC and check if it's a contract.
    Returns True if we supposedly discovered on-chain data,
    False if we must use the fallback model.
    """
    rpc_url = os.getenv("WEB3_RPC_URL")
    if not rpc_url:
        return False
        
    try:
        w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))
        # Simple latency check and connection check
        is_connected = await w3.is_connected()
        if not is_connected:
            return False
            
        # In a real phase we would fetch the bytecode / call standard interfaces.
        # But for this checkpoint we do a basic bytecode check.
        code = await w3.eth.get_code(w3.to_checksum_address(target_address))
        if len(code) > 2:
            return True # It exists on chain
        return False
    except Exception:
        # Fallback gracefully on timeout or bad config
        return False

async def get_demo_graph() -> tuple[list[Node], list[Edge]]:
    """Reads anvil.json and queries Anvil for real dummy values to construct the graph."""
    manifest_path = os.getenv("DEPLOYMENT_MANIFEST", "../local-chain/deployments/anvil.json")
    rpc_url = os.getenv("WEB3_RPC_URL", "http://127.0.0.1:8545")
    
    with open(manifest_path, "r") as f:
        data = json.load(f)
    contracts = data["contracts"]
    
    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))
    if not await w3.is_connected():
        raise ConnectionError("Anvil is unavailable. Fail loudly in DEMO_MODE!")
        
    amm_abi = [{
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }]
    oracle_abi = [{
        "constant": True,
        "inputs": [],
        "name": "getPrice",
        "outputs": [{"name": "price", "type": "int256"}, {"name": "isValid", "type": "bool"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }]
    
    amm_contract = w3.eth.contract(address=w3.to_checksum_address(contracts["demoAMM"]), abi=amm_abi)
    oracle_contract = w3.eth.contract(address=w3.to_checksum_address(contracts["demoOracle"]), abi=oracle_abi)
    
    reserves = await amm_contract.functions.getReserves().call()
    price, is_valid = await oracle_contract.functions.getPrice().call()
    
    # Exposing on-chain differences natively
    amm_exposure = float(w3.from_wei(reserves, 'ether')) * 0.2
    oracle_severity = 0.5 if is_valid else 1.0 # higher risk if oracle invalid
    if price == 0:
        oracle_severity = 1.0
    
    nodes = [
        Node(id="L1", name="SETTLEMENT", label="LAYER 1 — SETTLEMENT", financial_exposure=500_000, severity=0.3),
        Node(id="L2", name="YIELD", label="LAYER 2 — YIELD", financial_exposure=300_000, severity=0.5),
        Node(id="L3", name="ORACLE", label="LAYER 3 — ORACLE", financial_exposure=100_000, severity=oracle_severity),
        Node(id="L4", name="AMM", label="LAYER 4 — AMM", financial_exposure=amm_exposure, severity=0.7),
        Node(id="L5", name="LENDING", label="LAYER 5 — LENDING", financial_exposure=150_000, severity=0.8),
    ]

    edges = [
        Edge(source_id="L2", target_id="L1", exposure_weight=1.0),
        Edge(source_id="L3", target_id="L2", exposure_weight=1.0),
        Edge(source_id="L4", target_id="L3", exposure_weight=1.0),
        Edge(source_id="L5", target_id="L4", exposure_weight=1.0),
    ]

    return nodes, edges
