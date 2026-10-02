from engine.evidence.graph_builder import EvidenceGraphBuilder
from engine.evidence.graph_schemas import (
    GraphEdge,
    GraphEdgeType,
    GraphNode,
    GraphNodeType,
)
from engine.evidence.graph_service import EvidenceGraphService


def node(
    node_id: str,
    node_type: GraphNodeType,
    label: str,
) -> GraphNode:
    return GraphNode(
        node_id=node_id,
        node_type=node_type,
        label=label,
    )


def test_graph_adds_nodes():
    builder = EvidenceGraphBuilder()

    result = builder.build(
        nodes=[
            node("person:1", GraphNodeType.PERSON, "Jasprit Bumrah"),
            node("evidence:1", GraphNodeType.EVIDENCE, "Evidence 1"),
        ],
        edges=[],
    )

    assert result.added_nodes == 2
    assert result.graph.node_count() == 2


def test_duplicate_nodes_are_ignored():
    builder = EvidenceGraphBuilder()

    first = node(
        "person:1",
        GraphNodeType.PERSON,
        "Jasprit Bumrah",
    )

    assert builder.add_node(first) is True
    assert builder.add_node(first) is False
    assert builder.graph.node_count() == 1


def test_edges_require_existing_endpoints():
    builder = EvidenceGraphBuilder()

    builder.add_node(
        node("person:1", GraphNodeType.PERSON, "Person")
    )

    edge = GraphEdge(
        edge_id="edge:1",
        source_id="person:1",
        target_id="evidence:1",
        relationship=GraphEdgeType.EVIDENCES,
    )

    assert builder.add_edge(edge) is False
    assert builder.graph.edge_count() == 0


def test_graph_creates_explicit_relationship():
    builder = EvidenceGraphBuilder()

    builder.add_nodes(
        [
            node("person:1", GraphNodeType.PERSON, "Person"),
            node("evidence:1", GraphNodeType.EVIDENCE, "Evidence"),
        ]
    )

    created = builder.connect(
        source_id="person:1",
        target_id="evidence:1",
        relationship=GraphEdgeType.EVIDENCES,
        confidence=0.95,
    )

    assert created is True
    assert builder.graph.edge_count() == 1

    edge = next(iter(builder.graph.edges.values()))

    assert edge.relationship == GraphEdgeType.EVIDENCES
    assert edge.confidence == 0.95


def test_duplicate_edges_are_ignored():
    builder = EvidenceGraphBuilder()

    builder.add_nodes(
        [
            node("person:1", GraphNodeType.PERSON, "Person"),
            node("evidence:1", GraphNodeType.EVIDENCE, "Evidence"),
        ]
    )

    assert builder.connect(
        "person:1",
        "evidence:1",
        GraphEdgeType.EVIDENCES,
    )

    assert not builder.connect(
        "person:1",
        "evidence:1",
        GraphEdgeType.EVIDENCES,
    )

    assert builder.graph.edge_count() == 1


def test_trace_follows_evidence_chain():
    builder = EvidenceGraphBuilder()

    builder.add_nodes(
        [
            node("dossier:1", GraphNodeType.DOSSIER, "Dossier"),
            node("claim:1", GraphNodeType.CLAIM, "Claim"),
            node("evidence:1", GraphNodeType.EVIDENCE, "Evidence"),
            node("source:1", GraphNodeType.SOURCE, "Official Source"),
        ]
    )

    builder.connect(
        "dossier:1",
        "claim:1",
        GraphEdgeType.DERIVED_FROM,
        confidence=0.90,
    )

    builder.connect(
        "claim:1",
        "evidence:1",
        GraphEdgeType.EVIDENCES,
        confidence=0.95,
    )

    builder.connect(
        "evidence:1",
        "source:1",
        GraphEdgeType.SOURCE_FOR,
        confidence=0.99,
    )

    service = EvidenceGraphService(builder.graph)

    trace = service.trace(
        "dossier:1",
        "source:1",
    )

    assert trace.found is True
    assert len(trace.steps) == 4
    assert trace.steps[0].node.node_id == "dossier:1"
    assert trace.steps[-1].node.node_id == "source:1"
    assert trace.confidence == 0.90


def test_trace_returns_not_found_for_disconnected_nodes():
    builder = EvidenceGraphBuilder()

    builder.add_nodes(
        [
            node("person:1", GraphNodeType.PERSON, "Person"),
            node("source:1", GraphNodeType.SOURCE, "Source"),
        ]
    )

    service = EvidenceGraphService(builder.graph)

    trace = service.trace(
        "person:1",
        "source:1",
    )

    assert trace.found is False
    assert trace.steps == []


def test_trace_respects_max_depth():
    builder = EvidenceGraphBuilder()

    for index in range(5):
        builder.add_node(
            node(
                f"node:{index}",
                GraphNodeType.EVIDENCE,
                f"Node {index}",
            )
        )

    for index in range(4):
        builder.connect(
            f"node:{index}",
            f"node:{index + 1}",
            GraphEdgeType.DERIVED_FROM,
        )

    service = EvidenceGraphService(builder.graph)

    trace = service.trace(
        "node:0",
        "node:4",
        max_depth=2,
    )

    assert trace.found is False


def test_neighbors_filter_by_relationship():
    builder = EvidenceGraphBuilder()

    builder.add_nodes(
        [
            node("person:1", GraphNodeType.PERSON, "Person"),
            node("evidence:1", GraphNodeType.EVIDENCE, "Evidence"),
            node("topic:1", GraphNodeType.TOPIC, "Topic"),
        ]
    )

    builder.connect(
        "person:1",
        "evidence:1",
        GraphEdgeType.EVIDENCES,
    )

    builder.connect(
        "person:1",
        "topic:1",
        GraphEdgeType.HAS_TOPIC,
    )

    service = EvidenceGraphService(builder.graph)

    evidence_neighbors = service.neighbors(
        "person:1",
        relationships=[GraphEdgeType.EVIDENCES],
    )

    assert len(evidence_neighbors) == 1
    assert evidence_neighbors[0].node_id == "evidence:1"


def test_trace_to_sources_finds_all_reachable_sources():
    builder = EvidenceGraphBuilder()

    builder.add_nodes(
        [
            node("claim:1", GraphNodeType.CLAIM, "Claim"),
            node("evidence:1", GraphNodeType.EVIDENCE, "Evidence"),
            node("source:1", GraphNodeType.SOURCE, "Source A"),
            node("source:2", GraphNodeType.SOURCE, "Source B"),
        ]
    )

    builder.connect(
        "claim:1",
        "evidence:1",
        GraphEdgeType.EVIDENCES,
    )

    builder.connect(
        "evidence:1",
        "source:1",
        GraphEdgeType.SOURCE_FOR,
    )

    builder.connect(
        "evidence:1",
        "source:2",
        GraphEdgeType.SOURCE_FOR,
    )

    service = EvidenceGraphService(builder.graph)

    traces = service.trace_to_sources("claim:1")

    assert len(traces) == 2
    assert all(trace.found for trace in traces)


def test_contradicting_evidence_is_explicit():
    builder = EvidenceGraphBuilder()

    builder.add_nodes(
        [
            node("evidence:1", GraphNodeType.EVIDENCE, "Earlier"),
            node("evidence:2", GraphNodeType.EVIDENCE, "Later"),
        ]
    )

    builder.connect(
        "evidence:1",
        "evidence:2",
        GraphEdgeType.CONTRADICTS,
        explanation="Opposing structured propositions.",
        confidence=0.90,
    )

    edge = next(iter(builder.graph.edges.values()))

    assert edge.relationship == GraphEdgeType.CONTRADICTS
    assert edge.confidence == 0.90
    assert "Opposing" in edge.explanation


def test_corroborating_evidence_is_explicit():
    builder = EvidenceGraphBuilder()

    builder.add_nodes(
        [
            node("evidence:1", GraphNodeType.EVIDENCE, "Source A"),
            node("evidence:2", GraphNodeType.EVIDENCE, "Source B"),
        ]
    )

    builder.connect(
        "evidence:1",
        "evidence:2",
        GraphEdgeType.CORROBORATES,
        confidence=0.88,
    )

    edge = next(iter(builder.graph.edges.values()))

    assert edge.relationship == GraphEdgeType.CORROBORATES
    assert edge.confidence == 0.88


def test_same_event_relationship_is_supported():
    builder = EvidenceGraphBuilder()

    builder.add_nodes(
        [
            node("event:1", GraphNodeType.TIMELINE_EVENT, "Event A"),
            node("event:2", GraphNodeType.TIMELINE_EVENT, "Event B"),
        ]
    )

    assert builder.connect(
        "event:1",
        "event:2",
        GraphEdgeType.SAME_EVENT,
    )

    assert builder.graph.edge_count() == 1


def test_missing_start_node_is_handled():
    builder = EvidenceGraphBuilder()

    builder.add_node(
        node("source:1", GraphNodeType.SOURCE, "Source")
    )

    service = EvidenceGraphService(builder.graph)

    trace = service.trace(
        "missing",
        "source:1",
    )

    assert trace.found is False
    assert trace.reason == "Start node does not exist."