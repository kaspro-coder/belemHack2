"""
DeFi Risk Dependency Analyzer — Phase 2 Graph Risk Engine

Explicit DAG modeling with directional dependency propagation.
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator
import networkx as nx


class Node(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    label: str
    tvl: float = Field(default=0.0, ge=0.0)
    financial_exposure: float = Field(default=0.0, ge=0.0)
    severity: float = Field(default=1.0, ge=0.0, le=1.0)


class Edge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    target_id: str
    exposure_weight: float = Field(default=1.0, ge=0.0, le=1.0)


def build_and_validate_dag(nodes: list[Node], edges: list[Edge]) -> nx.DiGraph:
    """
    Build a NetworkX Directed Graph.
    Direction: source depends on target. Risk flows target -> source.
    So we add directed edges from target_id -> source_id indicating risk flow.
    Ensures the graph is acyclic.
    """
    G = nx.DiGraph()
    
    node_ids = {n.id for n in nodes}
    for n in nodes:
        G.add_node(n.id, **n.model_dump())

    for e in edges:
        if e.source_id not in node_ids or e.target_id not in node_ids:
            raise ValueError(f"Edge references invalid node IDs: {e.source_id} -> {e.target_id}")

        # Risk flows from the dependency (target) to the depender (source)
        # Add edge target -> source
        G.add_edge(e.target_id, e.source_id, weight=e.exposure_weight)

    if not nx.is_directed_acyclic_graph(G):
        raise ValueError("Invalid dependency graph: cyclic dependencies detected.")

    return G


def calculate_expected_loss(
    nodes: list[Node], 
    edges: list[Edge], 
    compromised_node_id: str
) -> float:
    """
    Simulate expected loss from a single compromised node.
    
    Expected Loss = Σ (Node.financial_exposure * Node.severity * effective_weight)
    
    Algorithm:
    1. Risk flows from target -> source.
    2. Path weight = product of edge exposure_weights.
    3. Effective weight for a node = max path weight from compromised node to that node.
    4. Each node's exposure is counted only once safely using max path weight.
    """
    G = build_and_validate_dag(nodes, edges)

    if compromised_node_id not in G:
        raise ValueError(f"Node '{compromised_node_id}' not found in graph.")

    # All simple paths from compromised node to every other node
    # Since it's a DAG, simple_paths is finite and safe.
    effective_weights = {compromised_node_id: 1.0}

    # Find all descendants reachable from the compromised node
    descendants = nx.descendants(G, compromised_node_id)
    
    for descendant in descendants:
        max_path_weight = 0.0
        # Check all possible paths to find the maximum product of weights
        paths = list(nx.all_simple_paths(G, source=compromised_node_id, target=descendant))
        for path in paths:
            path_weight = 1.0
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                edge_data = G.get_edge_data(u, v)
                path_weight *= edge_data['weight']
            if path_weight > max_path_weight:
                max_path_weight = path_weight
        
        effective_weights[descendant] = max_path_weight

    expected_loss = 0.0
    for node in nodes:
        if node.id in effective_weights:
            weight = effective_weights[node.id]
            expected_loss += node.financial_exposure * node.severity * weight

    return expected_loss

def get_fallback_graph() -> tuple[list[Node], list[Edge]]:
    """
    Returns the fallback 5-layer mock dependency graph.
    """
    nodes = [
        Node(id="L1", name="SETTLEMENT", label="LAYER 1 — SETTLEMENT", financial_exposure=500_000, severity=0.3),
        Node(id="L2", name="YIELD", label="LAYER 2 — YIELD", financial_exposure=300_000, severity=0.5),
        Node(id="L3", name="ORACLE", label="LAYER 3 — ORACLE", financial_exposure=100_000, severity=1.0),
        Node(id="L4", name="AMM", label="LAYER 4 — AMM", financial_exposure=200_000, severity=0.7),
        Node(id="L5", name="LENDING", label="LAYER 5 — LENDING", financial_exposure=150_000, severity=0.8),
    ]

    # Linear fallback: Yield depends on Settlement. Oracle depends on Yield. AMM depends on Oracle. Lending depends on AMM.
    edges = [
        Edge(source_id="L2", target_id="L1", exposure_weight=1.0),
        Edge(source_id="L3", target_id="L2", exposure_weight=1.0),
        Edge(source_id="L4", target_id="L3", exposure_weight=1.0),
        Edge(source_id="L5", target_id="L4", exposure_weight=1.0),
    ]

    return nodes, edges
