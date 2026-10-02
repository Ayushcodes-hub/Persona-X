from typing import Iterable, Optional

from engine.evidence.graph_schemas import (
    EvidenceGraph,
    GraphBuildResult,
    GraphEdge,
    GraphEdgeType,
    GraphNode,
)


class EvidenceGraphBuilder:
    """
    Builds a normalized evidence graph.

    The builder is deliberately independent of SQLAlchemy so that:
    - analysis engines remain reusable
    - graph construction can be tested independently
    - future persistence layers can consume the same graph
    """

    def __init__(self) -> None:
        self.graph = EvidenceGraph()

    def add_node(self, node: GraphNode) -> bool:
        existing = self.graph.nodes.get(node.node_id)

        if existing is not None:
            return False

        self.graph.nodes[node.node_id] = node
        return True

    def add_nodes(self, nodes: Iterable[GraphNode]) -> int:
        added = 0

        for node in nodes:
            if self.add_node(node):
                added += 1

        return added

    def add_edge(self, edge: GraphEdge) -> bool:
        if edge.source_id not in self.graph.nodes:
            return False

        if edge.target_id not in self.graph.nodes:
            return False

        if edge.edge_id in self.graph.edges:
            return False

        self.graph.edges[edge.edge_id] = edge
        return True

    def add_edges(self, edges: Iterable[GraphEdge]) -> tuple[int, int]:
        added = 0
        skipped = 0

        for edge in edges:
            if self.add_edge(edge):
                added += 1
            else:
                skipped += 1

        return added, skipped

    def connect(
        self,
        source_id: str,
        target_id: str,
        relationship: GraphEdgeType,
        edge_id: Optional[str] = None,
        explanation: Optional[str] = None,
        confidence: Optional[float] = None,
        evidence_id: Optional[int] = None,
    ) -> bool:
        if source_id not in self.graph.nodes:
            return False

        if target_id not in self.graph.nodes:
            return False

        generated_id = edge_id or self._edge_id(
            source_id,
            target_id,
            relationship,
        )

        edge = GraphEdge(
            edge_id=generated_id,
            source_id=source_id,
            target_id=target_id,
            relationship=relationship,
            explanation=explanation,
            confidence=confidence,
            evidence_id=evidence_id,
        )

        return self.add_edge(edge)

    def build(
        self,
        nodes: Iterable[GraphNode],
        edges: Iterable[GraphEdge],
    ) -> GraphBuildResult:
        added_nodes = self.add_nodes(nodes)
        added_edges, skipped_edges = self.add_edges(edges)

        warnings = []

        if skipped_edges:
            warnings.append(
                f"{skipped_edges} graph edge(s) were skipped because "
                "their endpoints were missing or already existed."
            )

        return GraphBuildResult(
            graph=self.graph,
            added_nodes=added_nodes,
            added_edges=added_edges,
            skipped_edges=skipped_edges,
            warnings=warnings,
        )

    @staticmethod
    def _edge_id(
        source_id: str,
        target_id: str,
        relationship: GraphEdgeType,
    ) -> str:
        return f"{source_id}|{relationship.value}|{target_id}"