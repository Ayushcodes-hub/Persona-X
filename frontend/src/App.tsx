import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { OmnibarModal } from './components/OmnibarModal';
import { DossierView } from './components/DossierView';
import { EntitiesDirectory } from './components/EntitiesDirectory';
import { ObservabilityView } from './components/ObservabilityView';
import { ResearchPipelineHUD } from './components/ResearchPipelineHUD';
import { personaApi } from './services/api';
import type {
  DossierData,
  GraphData,
  InitiativeItem,
  PoliticalAnalysisResponse,
  SourceItem,
  StatementItem,
  SystemStatus,
  TimelineItem,
} from './types';
import { Loader2, Search, Sparkles } from 'lucide-react';

export function App() {
  const [activeView, setActiveView] = useState<'dossier' | 'entities' | 'observability' | 'hud'>('dossier');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  // Active Person & Dossier State
  const [selectedPersonId, setSelectedPersonId] = useState<number | null>(null);
  const [dossier, setDossier] = useState<DossierData | null>(null);
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [statements, setStatements] = useState<StatementItem[]>([]);
  const [initiatives, setInitiatives] = useState<InitiativeItem[]>([]);
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [politicalData, setPoliticalData] = useState<PoliticalAnalysisResponse | null>(null);
  const [loadingDossier, setLoadingDossier] = useState(false);

  // Active Research Job for HUD
  const [activeJob, setActiveJob] = useState<{ id: number; name: string } | null>(null);

  // Initial load: Fetch system status and pick first person
  useEffect(() => {
    personaApi.getSystemStatus().then(setSystemStatus).catch(console.error);

    personaApi.listPersons(10, 0).then((res) => {
      if (res.items && res.items.length > 0) {
        const first = res.items.find((p) => p.has_dossier) || res.items[0];
        setSelectedPersonId(first.id);
      }
    }).catch(console.error);
  }, []);

  // Fetch all dossier details whenever selectedPersonId changes
  useEffect(() => {
    if (!selectedPersonId) return;

    setLoadingDossier(true);
    Promise.all([
      personaApi.getDossier(selectedPersonId).catch(() => null),
      personaApi.getTimeline(selectedPersonId).catch(() => ({ events: [] })),
      personaApi.getStatements(selectedPersonId).catch(() => ({ statements: [] })),
      personaApi.getInitiatives(selectedPersonId).catch(() => ({ initiatives: [] })),
      personaApi.getSources(selectedPersonId).catch(() => ({ sources: [] })),
      personaApi.getGraph(selectedPersonId).catch(() => null),
      personaApi.getPoliticalAnalysis(selectedPersonId).catch(() => null),
    ]).then(([dossierRes, timeRes, statRes, initRes, srcRes, graphRes, polRes]) => {
      setDossier(dossierRes);
      setTimeline(timeRes?.events || []);
      setStatements(statRes?.statements || []);
      setInitiatives(initRes?.initiatives || []);
      setSources(srcRes?.sources || []);
      setGraphData(graphRes);
      setPoliticalData(polRes);
    }).finally(() => {
      setLoadingDossier(false);
    });
  }, [selectedPersonId]);

  // Handler to start research on any figure
  const handleStartResearch = async (name: string) => {
    try {
      const res = await personaApi.createResearchJob(name);
      setActiveJob({ id: res.job_id, name: res.person_name });
      setActiveView('hud');
    } catch (err) {
      console.error('Failed to create research job', err);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Header */}
      <Header
        systemStatus={systemStatus}
        onOpenSearch={() => setIsSearchOpen(true)}
        activeView={activeView}
        setActiveView={(v) => setActiveView(v as any)}
      />

      {/* Omnibar Disambiguation Modal */}
      <OmnibarModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        onSelectPerson={(id) => {
          setSelectedPersonId(id);
          setActiveView('dossier');
        }}
        onStartResearch={handleStartResearch}
      />

      {/* Main View Area */}
      <main style={{ flex: 1 }}>
        {activeView === 'hud' && activeJob && (
          <ResearchPipelineHUD
            jobId={activeJob.id}
            personName={activeJob.name}
            onCompleted={(personId) => {
              setSelectedPersonId(personId);
              setActiveView('dossier');
              setActiveJob(null);
            }}
          />
        )}

        {activeView === 'entities' && (
          <EntitiesDirectory
            onSelectPerson={(id) => {
              setSelectedPersonId(id);
              setActiveView('dossier');
            }}
            onOpenSearch={() => setIsSearchOpen(true)}
          />
        )}

        {activeView === 'observability' && (
          <ObservabilityView initialStatus={systemStatus} />
        )}

        {activeView === 'dossier' && (
          <>
            {loadingDossier ? (
              <div style={{ padding: '120px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
                <Loader2 size={36} color="var(--accent-cyan)" className="pulse-active" style={{ margin: '0 auto 16px' }} />
                <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Loading Intelligence Dossier...
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Retrieving cross-verified citations, timeline, and relational evidence graph
                </p>
              </div>
            ) : dossier ? (
              <DossierView
                dossier={dossier}
                timeline={timeline}
                statements={statements}
                initiatives={initiatives}
                sources={sources}
                graphData={graphData}
                politicalData={politicalData}
                onRefreshResearch={() => handleStartResearch(dossier.canonical_name)}
              />
            ) : (
              <div style={{ maxWidth: '800px', margin: '80px auto', padding: '0 24px', textAlign: 'center' }}>
                <div className="glass-panel" style={{ padding: '48px 32px' }}>
                  <div style={{
                    width: '56px',
                    height: '56px',
                    borderRadius: '16px',
                    background: 'rgba(0, 240, 255, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px',
                    border: '1px solid rgba(0, 240, 255, 0.25)',
                  }}>
                    <Sparkles size={28} color="var(--accent-cyan)" />
                  </div>
                  <h2 style={{ fontSize: '24px', fontWeight: 800, color: '#f8fafc', marginBottom: '8px' }}>
                    Universal Public-Person Intelligence Platform
                  </h2>
                  <p style={{ fontSize: '14px', color: 'var(--text-secondary)', maxWidth: '520px', margin: '0 auto 24px', lineHeight: 1.6 }}>
                    Autonomously aggregates, verifies, graphs, and synthesizes living intelligence dossiers on public figures from attributable, authoritative public sources.
                  </p>
                  <button
                    onClick={() => setIsSearchOpen(true)}
                    className="badge badge-cyan glass-interactive"
                    style={{ padding: '12px 24px', fontSize: '14px', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '8px' }}
                  >
                    <Search size={16} />
                    <span>Search or Disambiguate Figure</span>
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
