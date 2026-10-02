from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class GraphNodeType(str, Enum):
    PERSON = "person"
    SOURCE = "source"
    SOURCE_CAPTURE = "source_capture"
    EVIDENCE = "evidence"
    STATEMENT = "statement"
    CLAIM = "claim"
    TOPIC = "topic"
    TIMELINE_EVENT = "timeline_event"
    INITIATIVE = "initiative"
    ORGANIZATION = "organization"
    AFFILIATION = "affiliation"
    PROFESSION_FINDING = "profession_finding"
    POLITICAL_POSITION = "political_position"
    POLITICAL_CONFLICT = "political_conflict"
    ANALYSIS = "analysis"
    DOSSIER = "dossier"


class GraphEdgeType(str, Enum):
    ABOUT = "about"
    SOURCE_FOR = "source_for"
    CAPTURE_OF = "capture_of"
    EVIDENCES = "evidences"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DERIVED_FROM = "derived_from"
    CORROBORATES = "corroborates"
    ASSERTS = "asserts"
    HAS_TOPIC = "has_topic"
    HAS_POSITION = "has_position"
    HAS_EVENT = "has_event"
    HAS_INITIATIVE = "has_initiative"
    HAS_AFFILIATION = "has_affiliation"
    MEMBER_OF = "member_of"
    OCCURRED_DURING = "occurred_during"
    SAME_EVENT = "same_event"
    TEMPORAL_PREDECESSOR = "temporal_predecessor"
    TEMPORAL_SUCCESSOR = "temporal_successor"
    ANALYZED_BY = "analyzed_by"
    PRODUCED = "produced"
    CORROBORATES_SOURCE = "corroborates_source"


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: GraphNodeType
    label: str
    person_id: Optional[int] = None
    entity_id: Optional[int] = None
    confidence: Optional[float] = None
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphEdge:
    edge_id: str
    source_id: str
    target_id: str
    relationship: GraphEdgeType
    explanation: Optional[str] = None
    confidence: Optional[float] = None
    evidence_id: Optional[int] = None
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class EvidenceGraph:
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    edges: Dict[str, GraphEdge] = field(default_factory=dict)

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return len(self.edges)

    def outgoing(self, node_id: str) -> List[GraphEdge]:
        return [
            edge
            for edge in self.edges.values()
            if edge.source_id == node_id
        ]

    def incoming(self, node_id: str) -> List[GraphEdge]:
        return [
            edge
            for edge in self.edges.values()
            if edge.target_id == node_id
        ]


@dataclass
class EvidenceTraceStep:
    node: GraphNode
    via_edge: Optional[GraphEdge] = None


@dataclass
class EvidenceTrace:
    start_node_id: str
    target_node_id: str
    found: bool
    steps: List[EvidenceTraceStep] = field(default_factory=list)
    confidence: Optional[float] = None
    reason: Optional[str] = None


@dataclass
class GraphBuildResult:
    graph: EvidenceGraph
    added_nodes: int
    added_edges: int
    skipped_edges: int
    warnings: List[str] = field(default_factory=list)