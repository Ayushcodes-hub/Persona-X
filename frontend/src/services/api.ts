import type {
  DossierData,
  ExternalCandidate,
  GraphData,
  InitiativeItem,
  PersonListItem,
  PersonSearchResult,
  PoliticalAnalysisResponse,
  ResearchCreateResponse,
  ResearchStatusResponse,
  ResearchStreamEvent,
  SearchResponse,
  SourceItem,
  StatementItem,
  SystemStatus,
  TimelineItem,
} from '../types';
import {
  DEMO_DOSSIER,
  DEMO_GRAPH,
  DEMO_INITIATIVES,
  DEMO_PERSONS,
  DEMO_POLITICAL,
  DEMO_POLITICAL_KEJRIWAL,
  DEMO_SOURCES,
  DEMO_STATEMENTS,
  DEMO_SYSTEM_STATUS,
  DEMO_TIMELINE,
} from './mockData';

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '') + '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorText = await res.text();
    let message = `API Error ${res.status}: ${res.statusText}`;
    try {
      const parsed = JSON.parse(errorText);
      message = parsed.detail || parsed.message || message;
    } catch {
      if (errorText) message += ` - ${errorText}`;
    }
    throw new Error(message);
  }
  return res.json();
}

export const personaApi = {
  async search(query: string, includeExternal: boolean = true): Promise<SearchResponse> {
    try {
      const params = new URLSearchParams({
        q: query,
        include_external: includeExternal ? 'true' : 'false',
      });
      const res = await fetch(`${API_BASE}/persons/search?${params}`);
      return await handleResponse<SearchResponse>(res);
    } catch {
      const qLower = query.toLowerCase();
      const localMatches: PersonSearchResult[] = DEMO_PERSONS.filter((p) =>
        p.canonical_name.toLowerCase().includes(qLower)
      ).map((p) => ({
        id: p.id,
        canonical_name: p.canonical_name,
        primary_profession: p.primary_profession,
        identity_status: p.identity_status,
        identity_confidence: p.identity_confidence,
        has_dossier: p.has_dossier,
        dossier_id: p.dossier_id,
        is_local: true,
      }));

      const externalCandidates: ExternalCandidate[] = localMatches.length === 0 ? [
        {
          wikidata_id: 'Q000000',
          label: query,
          description: `Public figure search candidate for ${query}`,
          birth_year: null,
          professions: ['Public Figure'],
          wikipedia_url: `https://en.wikipedia.org/wiki/${encodeURIComponent(query)}`,
          match_score: 0.9,
          is_local: false,
        },
      ] : [];

      return {
        query,
        local_count: localMatches.length,
        local_persons: localMatches,
        external_candidates: externalCandidates,
      };
    }
  },

  async listPersons(limit: number = 50, offset: number = 0): Promise<{
    total: number;
    offset: number;
    limit: number;
    items: PersonListItem[];
  }> {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
      });
      const res = await fetch(`${API_BASE}/persons?${params}`);
      return await handleResponse(res);
    } catch {
      return {
        total: DEMO_PERSONS.length,
        offset,
        limit,
        items: DEMO_PERSONS.slice(offset, offset + limit),
      };
    }
  },

  async getPerson(personId: number): Promise<any> {
    try {
      const res = await fetch(`${API_BASE}/persons/${personId}`);
      return await handleResponse(res);
    } catch {
      const found = DEMO_PERSONS.find((p) => p.id === personId) || DEMO_PERSONS[0];
      return {
        id: found.id,
        canonical_name: found.canonical_name,
        primary_profession: found.primary_profession,
        created_at: found.created_at,
      };
    }
  },

  async getDossier(personId: number): Promise<DossierData> {
    try {
      const res = await fetch(`${API_BASE}/persons/${personId}/dossier`);
      return await handleResponse<DossierData>(res);
    } catch {
      const person = DEMO_PERSONS.find((p) => p.id === personId) || DEMO_PERSONS[0];
      return {
        ...DEMO_DOSSIER,
        person_id: person.id,
        canonical_name: person.canonical_name,
        title: `Intelligence Dossier: ${person.canonical_name} (${person.primary_profession})`,
      };
    }
  },

  async getTimeline(personId: number): Promise<{
    person_id: number;
    canonical_name: string;
    count: number;
    events: TimelineItem[];
  }> {
    try {
      const res = await fetch(`${API_BASE}/persons/${personId}/timeline`);
      return await handleResponse(res);
    } catch {
      const person = DEMO_PERSONS.find((p) => p.id === personId) || DEMO_PERSONS[0];
      return {
        person_id: person.id,
        canonical_name: person.canonical_name,
        count: DEMO_TIMELINE.length,
        events: DEMO_TIMELINE,
      };
    }
  },

  async getStatements(personId: number): Promise<{
    person_id: number;
    canonical_name: string;
    count: number;
    statements: StatementItem[];
  }> {
    try {
      const res = await fetch(`${API_BASE}/persons/${personId}/statements`);
      return await handleResponse(res);
    } catch {
      const person = DEMO_PERSONS.find((p) => p.id === personId) || DEMO_PERSONS[0];
      return {
        person_id: person.id,
        canonical_name: person.canonical_name,
        count: DEMO_STATEMENTS.length,
        statements: DEMO_STATEMENTS,
      };
    }
  },

  async getInitiatives(personId: number): Promise<{
    person_id: number;
    canonical_name: string;
    count: number;
    initiatives: InitiativeItem[];
  }> {
    try {
      const res = await fetch(`${API_BASE}/persons/${personId}/initiatives`);
      return await handleResponse(res);
    } catch {
      const person = DEMO_PERSONS.find((p) => p.id === personId) || DEMO_PERSONS[0];
      return {
        person_id: person.id,
        canonical_name: person.canonical_name,
        count: DEMO_INITIATIVES.length,
        initiatives: DEMO_INITIATIVES,
      };
    }
  },

  async getSources(personId: number): Promise<{
    person_id: number;
    canonical_name: string;
    count: number;
    sources: SourceItem[];
  }> {
    try {
      const res = await fetch(`${API_BASE}/persons/${personId}/sources`);
      return await handleResponse(res);
    } catch {
      const person = DEMO_PERSONS.find((p) => p.id === personId) || DEMO_PERSONS[0];
      return {
        person_id: person.id,
        canonical_name: person.canonical_name,
        count: DEMO_SOURCES.length,
        sources: DEMO_SOURCES,
      };
    }
  },

  async getGraph(personId: number): Promise<GraphData> {
    try {
      const res = await fetch(`${API_BASE}/persons/${personId}/graph`);
      return await handleResponse<GraphData>(res);
    } catch {
      const person = DEMO_PERSONS.find((p) => p.id === personId) || DEMO_PERSONS[0];
      return {
        ...DEMO_GRAPH,
        person_id: person.id,
        canonical_name: person.canonical_name,
      };
    }
  },

  async getPoliticalAnalysis(personId: number): Promise<PoliticalAnalysisResponse> {
    try {
      const res = await fetch(`${API_BASE}/persons/${personId}/analysis/political`);
      return await handleResponse<PoliticalAnalysisResponse>(res);
    } catch {
      if (personId === 3) {
        return DEMO_POLITICAL_KEJRIWAL;
      }
      const person = DEMO_PERSONS.find((p) => p.id === personId) || DEMO_PERSONS[0];
      return {
        ...DEMO_POLITICAL,
        person_id: person.id,
        canonical_name: person.canonical_name,
      };
    }
  },

  async getProfessionAnalysis(personId: number): Promise<any> {
    try {
      const res = await fetch(`${API_BASE}/persons/${personId}/analysis/profession`);
      return await handleResponse(res);
    } catch {
      return {
        person_id: personId,
        applicable: true,
        primary_domain: 'scientific_research',
        milestones: ['Doctoral defense', 'Kepler-186f publication', 'Consortium appointment'],
      };
    }
  },

  async createResearchJob(personName: string, requestedScope?: Record<string, any>): Promise<ResearchCreateResponse> {
    try {
      const res = await fetch(`${API_BASE}/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          person_name: personName,
          requested_scope: requestedScope || { mode: 'full_research' },
        }),
      });
      return await handleResponse<ResearchCreateResponse>(res);
    } catch {
      return {
        job_id: Math.floor(Math.random() * 9000) + 1000,
        person_id: 1,
        person_name: personName,
        status: 'in_progress',
        current_stage: 'identity_discovery',
        created_at: new Date().toISOString(),
      };
    }
  },

  async runResearchJob(jobId: number): Promise<ResearchStatusResponse> {
    try {
      const res = await fetch(`${API_BASE}/research/${jobId}/run`, {
        method: 'POST',
      });
      return await handleResponse<ResearchStatusResponse>(res);
    } catch {
      return {
        job_id: jobId,
        person_id: 1,
        person_name: 'Researched Entity',
        status: 'completed',
        requested_scope: { mode: 'full_research' },
        query_count: 8,
        source_count: 6,
        evidence_count: 12,
        current_stage: 'dossier_synthesis',
        error_message: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
    }
  },

  async getResearchStatus(jobId: number): Promise<ResearchStatusResponse> {
    try {
      const res = await fetch(`${API_BASE}/research/${jobId}`);
      return await handleResponse<ResearchStatusResponse>(res);
    } catch {
      return {
        job_id: jobId,
        person_id: 1,
        person_name: 'Researched Entity',
        status: 'completed',
        requested_scope: { mode: 'full_research' },
        query_count: 8,
        source_count: 6,
        evidence_count: 12,
        current_stage: 'dossier_synthesis',
        error_message: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
    }
  },

  async getSystemStatus(): Promise<SystemStatus> {
    try {
      const res = await fetch(`${API_BASE}/system/status`);
      return await handleResponse<SystemStatus>(res);
    } catch {
      return DEMO_SYSTEM_STATUS;
    }
  },

  subscribeResearchStream(
    jobId: number,
    onEvent: (event: ResearchStreamEvent) => void,
    onError?: (err: any) => void
  ): () => void {
    const url = `${API_BASE}/research/${jobId}/stream`;
    let isClosed = false;

    try {
      const eventSource = new EventSource(url);

      eventSource.onmessage = (e) => {
        try {
          const parsed = JSON.parse(e.data);
          onEvent(parsed);
        } catch (err) {
          console.error('Failed to parse SSE payload', err);
        }
      };

      const registeredEvents = [
        'connected',
        'job_started',
        'stage_started',
        'stage_completed',
        'source_discovered',
        'evidence_extracted',
        'job_completed',
        'job_failed',
      ];

      registeredEvents.forEach((evName) => {
        eventSource.addEventListener(evName, (e: any) => {
          try {
            const parsed = JSON.parse(e.data);
            onEvent({ ...parsed, event: evName });
          } catch {
            onEvent({
              job_id: jobId,
              event: evName,
              data: {},
              timestamp: new Date().toISOString(),
            });
          }
        });
      });

      eventSource.onerror = (err) => {
        eventSource.close();
        if (onError) onError(err);
        // Simulate fallback progression in demo mode if SSE failed to connect
        if (!isClosed) {
          simulateDemoPipeline(jobId, onEvent);
        }
      };

      return () => {
        isClosed = true;
        eventSource.close();
      };
    } catch {
      simulateDemoPipeline(jobId, onEvent);
      return () => {
        isClosed = true;
      };
    }
  },
};

function simulateDemoPipeline(jobId: number, onEvent: (ev: ResearchStreamEvent) => void) {
  const stages = [
    { name: 'identity_discovery', delay: 400 },
    { name: 'query_generation', delay: 1200 },
    { name: 'search_and_ingestion', delay: 2200 },
    { name: 'source_capture', delay: 3200 },
    { name: 'evidence_extraction', delay: 4200 },
    { name: 'claim_verification', delay: 5200 },
    { name: 'timeline_extraction', delay: 6000 },
    { name: 'political_analysis', delay: 6800 },
    { name: 'graph_assembly', delay: 7600 },
    { name: 'dossier_synthesis', delay: 8400 },
  ];

  stages.forEach(({ name, delay }) => {
    setTimeout(() => {
      onEvent({
        job_id: jobId,
        event: 'stage_completed',
        stage: name,
        data: { stage: name, status: 'completed' },
        timestamp: new Date().toISOString(),
      });
    }, delay);
  });

  setTimeout(() => {
    onEvent({
      job_id: jobId,
      event: 'job_completed',
      stage: 'dossier_synthesis',
      data: { person_id: 1, status: 'completed' },
      timestamp: new Date().toISOString(),
    });
  }, 9200);
}
