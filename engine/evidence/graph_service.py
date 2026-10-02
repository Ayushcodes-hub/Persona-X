from collections import deque
from typing import Iterable, Optional, Set

from engine.evidence.graph_schemas import (
    EvidenceGraph,
    EvidenceTrace,
    EvidenceTraceStep,
    GraphEdge,
    GraphEdgeType,
    GraphNode,
)


class EvidenceGraphService:
    """
    Query and trace an evidence graph.

    Traversal is intentionally bounded to prevent runaway graph exploration.
    """

    def __init__(self, graph: EvidenceGraph) -> None:
        self.graph = graph

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.graph.nodes.get(node_id)

    def get_edges(
        self,
        node_id: str,
        relationships: Optional[Iterable[GraphEdgeType]] = None,
    ) -> list[GraphEdge]:
        allowed: Optional[Set[GraphEdgeType]] = (
            set(relationships)
            if relationships is not None
            else None
        )

        return [
            edge
            for edge in self.graph.outgoing(node_id)
            if allowed is None or edge.relationship in allowed
        ]

    def trace(
        self,
        start_node_id: str,
        target_node_id: str,
        max_depth: int = 10,
    ) -> EvidenceTrace:
        if start_node_id not in self.graph.nodes:
            return EvidenceTrace(
                start_node_id=start_node_id,
                target_node_id=target_node_id,
                found=False,
                reason="Start node does not exist.",
            )

        if target_node_id not in self.graph.nodes:
            return EvidenceTrace(
                start_node_id=start_node_id,
                target_node_id=target_node_id,
                found=False,
                reason="Target node does not exist.",
            )

        if start_node_id == target_node_id:
            return EvidenceTrace(
                start_node_id=start_node_id,
                target_node_id=target_node_id,
                found=True,
                steps=[
                    EvidenceTraceStep(
                        node=self.graph.nodes[start_node_id]
                    )
                ],
                confidence=1.0,
                reason="Start and target are the same node.",
            )

        queue = deque([(start_node_id, 0)])

        parents: dict[str, tuple[str, GraphEdge]] = {}

        visited = {start_node_id}

        while queue:
            current_id, depth = queue.popleft()

            if depth >= max_depth:
                continue

            for edge in self.graph.outgoing(current_id):
                next_id = edge.target_id

                if next_id in visited:
                    continue

                visited.add(next_id)
                parents[next_id] = (current_id, edge)

                if next_id == target_node_id:
                    return self._build_trace(
                        start_node_id=start_node_id,
                        target_node_id=target_node_id,
                        parents=parents,
                    )

                queue.append((next_id, depth + 1))

        return EvidenceTrace(
            start_node_id=start_node_id,
            target_node_id=target_node_id,
            found=False,
            reason=f"No path found within depth {max_depth}.",
        )

    def trace_to_sources(
        self,
        start_node_id: str,
        max_depth: int = 10,
    ) -> list[EvidenceTrace]:
        if start_node_id not in self.graph.nodes:
            return []

        source_ids = [
            node.node_id
            for node in self.graph.nodes.values()
            if node.node_type.value == "source"
        ]

        traces = []

        for source_id in source_ids:
            trace = self.trace(
                start_node_id=start_node_id,
                target_node_id=source_id,
                max_depth=max_depth,
            )

            if trace.found:
                traces.append(trace)

        return traces

    def neighbors(
        self,
        node_id: str,
        relationships: Optional[Iterable[GraphEdgeType]] = None,
    ) -> list[GraphNode]:
        edges = self.get_edges(
            node_id=node_id,
            relationships=relationships,
        )

        return [
            self.graph.nodes[edge.target_id]
            for edge in edges
            if edge.target_id in self.graph.nodes
        ]

    def _build_trace(
        self,
        start_node_id: str,
        target_node_id: str,
        parents: dict[str, tuple[str, GraphEdge]],
    ) -> EvidenceTrace:
        chain: list[tuple[str, GraphEdge]] = []

        current_id = target_node_id
        confidence_values = []

        while current_id != start_node_id:
            parent_id, edge = parents[current_id]

            chain.append((current_id, edge))

            if edge.confidence is not None:
                confidence_values.append(edge.confidence)

            current_id = parent_id

        chain.reverse()

        steps = [
            EvidenceTraceStep(
                node=self.graph.nodes[start_node_id],
                via_edge=None,
            )
        ]

        for node_id, edge in chain:
            steps.append(
                EvidenceTraceStep(
                    node=self.graph.nodes[node_id],
                    via_edge=edge,
                )
            )

        confidence = (
            min(confidence_values)
            if confidence_values
            else None
        )

        return EvidenceTrace(
            start_node_id=start_node_id,
            target_node_id=target_node_id,
            found=True,
            steps=steps,
            confidence=confidence,
            reason="Evidence path successfully traced.",
        )