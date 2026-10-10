import sys
import json
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

def run_scenario(scenario):
    manifest_path = os.getenv("DEPLOYMENT_MANIFEST", "local-chain/deployments/anvil.json")
    rpc_url = os.getenv("WEB3_RPC_URL", "http://127.0.0.1:8545")

    with open(manifest_path, "r") as f:
        data = json.load(f)
    contracts = data["contracts"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print("Error: Could not connect to local Anvil RPC.", file=sys.stderr)
        sys.exit(1)

    controller_addr = w3.to_checksum_address(contracts["demoScenarioController"])
    
    # Minimal ABI
    abi = [{
        "inputs": [],
        "name": fn,
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    } for fn in ["resetToBaseline", "triggerInflation", "triggerPoolDrain", "triggerOracleFailure"]]
    
    controller = w3.eth.contract(address=controller_addr, abi=abi)
    
    # We use Anvil's first default account
    acct = w3.eth.accounts[0]
    
    print(f"Triggering Scenario: {scenario}...")
    try:
        if scenario == "baseline":
            tx_hash = controller.functions.resetToBaseline().transact({'from': acct})
        elif scenario == "inflation":
            tx_hash = controller.functions.triggerInflation().transact({'from': acct})
        elif scenario == "pool-drain":
            tx_hash = controller.functions.triggerPoolDrain().transact({'from': acct})
        elif scenario == "oracle-failure":
            tx_hash = controller.functions.triggerOracleFailure().transact({'from': acct})
        else:
            print(f"Unknown scenario: {scenario}")
            sys.exit(1)
            
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Success! Block: {receipt['blockNumber']}, Hash: {tx_hash.hex()}")
    except Exception as e:
        print(f"Transaction failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scenario_simulator.py [baseline|inflation|pool-drain|oracle-failure]")
        sys.exit(1)
    
    run_scenario(sys.argv[1])
