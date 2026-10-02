export interface PersonSearchResult {
  id: number;
  canonical_name: string;
  primary_profession: string | null;
  identity_status: string;
  identity_confidence: number;
  has_dossier: boolean;
  dossier_id: number | null;
  is_local: boolean;
}

export interface ExternalCandidate {
  wikidata_id: string;
  label: string;
  description: string;
  birth_year: string | null;
  professions: string[];
  wikipedia_url: string | null;
  match_score: number;
  is_local: boolean;
}

export interface SearchResponse {
  query: string;
  local_count: number;
  local_persons: PersonSearchResult[];
  external_candidates: ExternalCandidate[];
}

export interface PersonListItem {
  id: number;
  canonical_name: string;
  primary_profession: string | null;
  identity_status: string;
  identity_confidence: number;
  has_dossier: boolean;
  dossier_id: number | null;
  dossier_completeness: number | null;
  counts: {
    sources: number;
    evidence: number;
    timeline_events: number;
  };
  created_at: string | null;
}

export interface DossierData {
  dossier_id: number;
  person_id: number;
  canonical_name: string;
  research_job_id: number;
  version: number;
  status: string;
  title: string;
  executive_summary: string;
  dossier_content: Record<string, any>;
  source_count: number;
  evidence_count: number;
  completeness_score: number;
  created_at: string;
  updated_at: string;
}

export interface TimelineItem {
  id: number;
  event_type: string;
  title: string;
  description: string;
  start_date: string | null;
  end_date: string | null;
  organization: string | null;
  location: string | null;
  status: string;
  confidence: number;
  evidence_id: number | null;
  source: {
    id: number;
    title: string | null;
    url: string;
    source_tier: number;
  } | null;
}

export interface StatementItem {
  id: number;
  statement_type: string;
  text: string;
  paraphrase: string | null;
  topic: string | null;
  context: string | null;
  statement_date: string | null;
  attribution_status: string;
  confidence: number;
  evidence_id: number | null;
  source: {
    id: number;
    title: string | null;
    url: string;
    source_tier: number;
  } | null;
}

export interface InitiativeItem {
  id: number;
  name: string;
  initiative_type: string;
  description: string;
  objective: string;
  lifecycle_stage: string;
  start_date: string | null;
  end_date: string | null;
  evidence_id: number | null;
  source: {
    id: number;
    title: string | null;
    url: string;
  } | null;
}

export interface SourceItem {
  id: number;
  title: string | null;
  publisher: string | null;
  url?: string | null;
  domain: string;
  source_type: string;
  source_tier: number;
  reliability_score: number;
  created_at: string;
}

export interface GraphNode {
  id: string;
  type: 'person' | 'source' | 'evidence' | 'claim' | 'statement' | 'initiative' | 'timeline';
  label: string;
  confidence: number;
  metadata: Record<string, any>;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  confidence: number;
}

export interface GraphData {
  person_id: number;
  canonical_name: string;
  node_count: number;
  edge_count: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface PoliticalSpectrumData {
  applicable: boolean;
  score: number | null;
  label: string;
  economic_axis: number | null;
  social_axis: number | null;
  governance_axis: number | null;
  foreign_policy_axis: number | null;
  confidence: number;
  rationale: string;
  key_indicators: string[];
}

export interface PoliticalAnalysisResponse {
  person_id: number;
  canonical_name: string;
  applicable: boolean;
  evidence_count: number;
  sufficiency: {
    sufficient: boolean;
    evidence_count: number;
    qualifying_evidence_count: number;
    dimensions_covered: number;
    confidence: number;
    reason: string;
  };
  spectrum: PoliticalSpectrumData | null;
  dimensions: Array<{
    name: string;
    confidence: number;
    evidence_count: number;
  }>;
  limitations: string[];
}

export interface SystemStatus {
  status: string;
  timestamp: string;
  service: string;
  version: string;
  database: {
    status: string;
    dialect: string;
    latency_ms: number | null;
    is_supabase: boolean;
  };
  research_engine: {
    status: string;
    worker_count: number;
    queued_jobs: number;
    running_jobs: number;
    active_workers: number;
  };
  ai_providers?: Record<string, any>;
}

export interface ResearchCreateResponse {
  job_id: number;
  person_id: number;
  person_name: string;
  status: string;
  current_stage: string;
  created_at: string;
}

export interface ResearchStatusResponse {
  job_id: number;
  person_id: number;
  person_name: string;
  status: string;
  requested_scope: Record<string, any> | null;
  query_count: number;
  source_count: number;
  evidence_count: number;
  current_stage: string;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ResearchStreamEvent {
  id?: number;
  job_id: number;
  event: string;
  stage?: string;
  data: Record<string, any>;
  timestamp: string;
}
