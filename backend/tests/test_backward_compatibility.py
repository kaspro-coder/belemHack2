from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_analyze_backward_compatibility():
    # Phase 1 expected token_address in request, and return status, token_address, slippage, expected_loss, action
    response = client.post("/api/analyze", json={"token_address": "0x1234567890abcdef"})
    assert response.status_code == 200
    data = response.json()
    
    # Check old fields
    assert "status" in data
    assert "token_address" in data
    assert "expected_loss" in data
    assert "action" in data
    
    # By default in testing without env vars, zerox returns None
    assert data["slippage"] is None
    
    # Check new fields
    assert "nodes" in data
    assert "edges" in data
    assert "warnings" in data
    assert "data_provenance" in data
