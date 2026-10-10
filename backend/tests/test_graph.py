import pytest
from graph import Node, Edge, build_and_validate_dag, calculate_expected_loss, get_fallback_graph

def test_dag_validation_success():
    nodes = [
        Node(id="A", name="A", label="A", financial_exposure=100, severity=1.0),
        Node(id="B", name="B", label="B", financial_exposure=200, severity=1.0),
    ]
    edges = [Edge(source_id="A", target_id="B", exposure_weight=0.5)]
    G = build_and_validate_dag(nodes, edges)
    # The edge should be B -> A (risk flows from B to A because A depends on B)
    assert G.has_edge("B", "A")
    assert G["B"]["A"]["weight"] == 0.5

def test_dag_validation_cyclic():
    nodes = [
        Node(id="A", name="A", label="A"),
        Node(id="B", name="B", label="B"),
    ]
    edges = [
        Edge(source_id="A", target_id="B"),
        Edge(source_id="B", target_id="A")
    ]
    with pytest.raises(ValueError, match="cyclic dependencies"):
        build_and_validate_dag(nodes, edges)

def test_dag_validation_invalid_weights():
    with pytest.raises(ValueError, match="Input should be less than or equal to 1"):
        Edge(source_id="A", target_id="B", exposure_weight=1.5)

def test_calculate_expected_loss_linear():
    """
    A depends on B, B depends on C
    Risk flows: C -> B -> A
    """
    nodes = [
        Node(id="A", name="A", label="A", financial_exposure=100, severity=1.0),
        Node(id="B", name="B", label="B", financial_exposure=200, severity=1.0),
        Node(id="C", name="C", label="C", financial_exposure=300, severity=1.0),
    ]
    edges = [
        Edge(source_id="A", target_id="B", exposure_weight=1.0),
        Edge(source_id="B", target_id="C", exposure_weight=0.5),
    ]
    # Compromised node is C
    # C's loss: 300 * 1.0 * 1.0 = 300
    # C -> B weight is 0.5. B's loss: 200 * 1.0 * 0.5 = 100
    # B -> A weight is 1.0. Path C->B->A weight is 0.5 * 1.0 = 0.5. A's loss: 100 * 1.0 * 0.5 = 50
    # Total expected loss = 300 + 100 + 50 = 450
    loss = calculate_expected_loss(nodes, edges, compromised_node_id="C")
    assert loss == 450.0

def test_calculate_expected_loss_multipath():
    """
    To avoid double-counting, we take the max path weight product.
    A depends on B (0.5), A depends on C (0.2).
    B depends on C (1.0).
    Risk flows: C -> A (path 1: weight 0.2)
                C -> B -> A (path 2: weight 1.0 * 0.5 = 0.5)
    Max path weight C -> A is 0.5.
    """
    nodes = [
        Node(id="A", name="A", label="A", financial_exposure=1000, severity=1.0),
        Node(id="B", name="B", label="B", financial_exposure=2000, severity=1.0),
        Node(id="C", name="C", label="C", financial_exposure=3000, severity=1.0),
    ]
    edges = [
        Edge(source_id="A", target_id="B", exposure_weight=0.5),
        Edge(source_id="A", target_id="C", exposure_weight=0.2), # direct dependency
        Edge(source_id="B", target_id="C", exposure_weight=1.0),
    ]
    
    # Compromised: C 
    # Loss for C: 3000 * 1 = 3000
    # Loss for B: C->B directly weight 1. 2000 * 1 = 2000
    # Loss for A: max(C->A (0.2), C->B->A (1*0.5)) = 0.5. 1000 * 0.5 = 500.
    # Total = 3000 + 2000 + 500 = 5500
    loss = calculate_expected_loss(nodes, edges, "C")
    assert loss == 5500.0

def test_fallback_graph():
    nodes, edges = get_fallback_graph()
    loss = calculate_expected_loss(nodes, edges, "L3") # ORACLE compromised
    # L3 exposure = 100k, sev=1.0 -> 100k
    # Risk flows L3 -> L4 (AMM, 200k, 0.7) weight=1 -> 140k
    # Risk flows L4 -> L5 (LENDING, 150k, 0.8) weight=1 -> 120k
    # Total = 360k
    assert loss == 360_000.0
