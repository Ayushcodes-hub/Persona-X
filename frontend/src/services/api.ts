import type {
  DossierData,
  GraphData,
  InitiativeItem,
  PersonListItem,
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
    const params = new URLSearchParams({
      q: query,
      include_external: includeExternal ? 'true' : 'false',
    });
    const res = await fetch(`${API_BASE}/persons/search?${params}`);
    return handleResponse<SearchResponse>(res);
  },

  async listPersons(limit: number = 50, offset: number = 0): Promise<{
    total: number;
    offset: number;
    limit: number;
    items: PersonListItem[];
  }> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    const res = await fetch(`${API_BASE}/persons?${params}`);
    return handleResponse(res);
  },

  async getPerson(personId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/persons/${personId}`);
    return handleResponse(res);
  },

  async getDossier(personId: number): Promise<DossierData> {
    const res = await fetch(`${API_BASE}/persons/${personId}/dossier`);
    return handleResponse<DossierData>(res);
  },

  async getTimeline(personId: number): Promise<{
    person_id: number;
    canonical_name: string;
    count: number;
    events: TimelineItem[];
  }> {
    const res = await fetch(`${API_BASE}/persons/${personId}/timeline`);
    return handleResponse(res);
  },

  async getStatements(personId: number): Promise<{
    person_id: number;
    canonical_name: string;
    count: number;
    statements: StatementItem[];
  }> {
    const res = await fetch(`${API_BASE}/persons/${personId}/statements`);
    return handleResponse(res);
  },

  async getInitiatives(personId: number): Promise<{
    person_id: number;
    canonical_name: string;
    count: number;
    initiatives: InitiativeItem[];
  }> {
    const res = await fetch(`${API_BASE}/persons/${personId}/initiatives`);
    return handleResponse(res);
  },

  async getSources(personId: number): Promise<{
    person_id: number;
    canonical_name: string;
    count: number;
    sources: SourceItem[];
  }> {
    const res = await fetch(`${API_BASE}/persons/${personId}/sources`);
    return handleResponse(res);
  },

  async getGraph(personId: number): Promise<GraphData> {
    const res = await fetch(`${API_BASE}/persons/${personId}/graph`);
    return handleResponse<GraphData>(res);
  },

  async getPoliticalAnalysis(personId: number): Promise<PoliticalAnalysisResponse> {
    const res = await fetch(`${API_BASE}/persons/${personId}/analysis/political`);
    return handleResponse<PoliticalAnalysisResponse>(res);
  },

  async getProfessionAnalysis(personId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/persons/${personId}/analysis/profession`);
    return handleResponse(res);
  },

  async createResearchJob(personName: string, requestedScope?: Record<string, any>): Promise<ResearchCreateResponse> {
    const res = await fetch(`${API_BASE}/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        person_name: personName,
        requested_scope: requestedScope || { mode: 'full_research' },
      }),
    });
    return handleResponse<ResearchCreateResponse>(res);
  },

  async runResearchJob(jobId: number): Promise<ResearchStatusResponse> {
    const res = await fetch(`${API_BASE}/research/${jobId}/run`, {
      method: 'POST',
    });
    return handleResponse<ResearchStatusResponse>(res);
  },

  async getResearchStatus(jobId: number): Promise<ResearchStatusResponse> {
    const res = await fetch(`${API_BASE}/research/${jobId}`);
    return handleResponse<ResearchStatusResponse>(res);
  },

  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/system/status`);
    return handleResponse<SystemStatus>(res);
  },

  subscribeResearchStream(
    jobId: number,
    onEvent: (event: ResearchStreamEvent) => void,
    onError?: (err: any) => void
  ): () => void {
    const url = `${API_BASE}/research/${jobId}/stream`;
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
      if (onError) onError(err);
    };

    return () => {
      eventSource.close();
    };
  },
};
