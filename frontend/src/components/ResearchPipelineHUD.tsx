import React, { useEffect, useState, useRef } from 'react';
import {
  CheckCircle2,
  Circle,
  Loader2,
  Activity,
  ArrowRight,
  Database,
  X,
} from 'lucide-react';
import { personaApi } from '../services/api';
import type { ResearchStreamEvent } from '../types';

interface ResearchPipelineHUDProps {
  jobId: number;
  personName: string;
  onCompleted: (personId: number) => void;
  onCancel?: () => void;
}

const PIPELINE_STAGES = [
  { id: 'identity', label: '1. Identity Disambiguation', desc: 'Querying Wikidata & Wikipedia entity graphs' },
  { id: 'query_gen', label: '2. Targeted Query Matrix', desc: 'Synthesizing professional & timeline vectors' },
  { id: 'search', label: '3. Multi-Source Search', desc: 'Crawling Groq, DuckDuckGo & academic repositories' },
  { id: 'capture', label: '4. Source Snapshot & SSRF', desc: 'Cryptographic hashing & clean text extraction' },
  { id: 'extraction', label: '5. Evidence Extraction', desc: 'Atomic factual extraction of quotes and milestones' },
  { id: 'grounding', label: '6. Cite-or-Drop Verifier', desc: 'Verbatim text span verification against snapshots' },
  { id: 'timeline', label: '7. Timeline & Statements', desc: 'Chronological mapping & attribution taxonomy' },
  { id: 'analysis', label: '8. Political & Profession', desc: 'Economic/social compass & career domain evaluation' },
  { id: 'graph', label: '9. Evidence Graph Assembly', desc: 'Interconnecting nodes, citations, and claims' },
  { id: 'dossier', label: '10. Living Dossier Synthesis', desc: 'Compiling executive summary & completeness score' },
];

export const ResearchPipelineHUD: React.FC<ResearchPipelineHUDProps> = ({
  jobId,
  personName,
  onCompleted,
  onCancel,
}) => {
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [status, setStatus] = useState<'running' | 'completed' | 'failed'>('running');
  const [events, setEvents] = useState<ResearchStreamEvent[]>([]);
  const [sourceCount, setSourceCount] = useState(0);
  const [evidenceCount, setEvidenceCount] = useState(0);
  const [secondsElapsed, setSecondsElapsed] = useState(0);
  const [resolvedPersonId, setResolvedPersonId] = useState<number | null>(null);
  const eventLogRef = useRef<HTMLDivElement>(null);
  const statusRef = useRef(status);

  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  // Timer
  useEffect(() => {
    if (status !== 'running') return;
    const interval = setInterval(() => {
      setSecondsElapsed((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [status]);

  // SSE Stream subscription
  useEffect(() => {
    let isSubscribed = true;

    const unsubscribe = personaApi.subscribeResearchStream(
      jobId,
      (ev) => {
        if (!isSubscribed) return;
        setEvents((prev) => [ev, ...prev.slice(0, 40)]);

        if (ev.data?.source_count !== undefined) {
          setSourceCount(ev.data.source_count);
        }
        if (ev.data?.evidence_count !== undefined) {
          setEvidenceCount(ev.data.evidence_count);
        }
        if (ev.data?.person_id) {
          setResolvedPersonId(ev.data.person_id);
        }

        // Map event stage to index
        const stageName = ev.stage || ev.data?.stage || '';
        const mappedIdx = PIPELINE_STAGES.findIndex(
          (s) => s.id === stageName || s.label.toLowerCase().includes(stageName.toLowerCase())
        );
        if (mappedIdx !== -1) {
          setCurrentStageIndex((prev) => (mappedIdx > prev ? mappedIdx : prev));
        }

        if (ev.event === 'job_completed') {
          setStatus('completed');
          setCurrentStageIndex(PIPELINE_STAGES.length - 1);
          if (ev.data?.person_id) {
            setResolvedPersonId(ev.data.person_id);
          }
        } else if (ev.event === 'job_failed') {
          setStatus('failed');
        }
      },
      (err) => {
        console.error('SSE Error:', err);
      }
    );

    // Initial poll & kick-off
    personaApi.runResearchJob(jobId).then((res) => {
      if (res.person_id) setResolvedPersonId(res.person_id);
      if (res.status === 'completed') {
        setStatus('completed');
        setCurrentStageIndex(PIPELINE_STAGES.length - 1);
      }
    }).catch(() => {});

    // Periodic status poll fallback
    const pollInterval = setInterval(async () => {
      if (statusRef.current === 'completed' || statusRef.current === 'failed') return;
      try {
        const poll = await personaApi.getResearchStatus(jobId);
        if (poll.source_count) setSourceCount(poll.source_count);
        if (poll.evidence_count) setEvidenceCount(poll.evidence_count);
        if (poll.person_id) setResolvedPersonId(poll.person_id);
        if (poll.status === 'completed') {
          setStatus('completed');
          setCurrentStageIndex(PIPELINE_STAGES.length - 1);
        } else if (poll.status === 'failed') {
          setStatus('failed');
        }
      } catch {}
    }, 4000);

    return () => {
      isSubscribed = false;
      unsubscribe();
      clearInterval(pollInterval);
    };
  }, [jobId]);

  return (
    <div style={{ maxWidth: '1280px', margin: '30px auto', padding: '0 24px' }}>
      {/* Header telemetry HUD */}
      <div className="glass-panel" style={{ padding: '24px 28px', marginBottom: '24px', border: '1px solid var(--border-glow)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="badge badge-cyan">AUTONOMOUS SYNTHESIS HUD</span>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                JOB ID #{jobId}
              </span>
            </div>
            <h1 style={{ fontSize: '28px', fontWeight: 800, margin: '8px 0 4px', color: '#f8fafc', letterSpacing: '-0.02em' }}>
              {personName}
            </h1>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              {status === 'running' && 'Real-time evidence acquisition, multi-tier search, and grounding verification active'}
              {status === 'completed' && 'Autonomous intelligence synthesis completed with verified citations'}
              {status === 'failed' && 'Research pipeline halted due to upstream network or search exception'}
            </p>
          </div>

          {/* Metric Badges */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div className="glass-panel" style={{ padding: '10px 16px', borderRadius: '10px', textAlign: 'center', minWidth: '95px' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Elapsed</div>
              <div style={{ fontSize: '18px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-cyan)' }}>
                {secondsElapsed}s
              </div>
            </div>

            <div className="glass-panel" style={{ padding: '10px 16px', borderRadius: '10px', textAlign: 'center', minWidth: '95px' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Sources</div>
              <div style={{ fontSize: '18px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-emerald)' }}>
                {sourceCount}
              </div>
            </div>

            <div className="glass-panel" style={{ padding: '10px 16px', borderRadius: '10px', textAlign: 'center', minWidth: '95px' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Evidence</div>
              <div style={{ fontSize: '18px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-amber)' }}>
                {evidenceCount}
              </div>
            </div>

            {status === 'completed' && resolvedPersonId && (
              <button
                onClick={() => onCompleted(resolvedPersonId)}
                className="badge badge-emerald glass-interactive"
                style={{
                  padding: '12px 20px',
                  fontSize: '13px',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  cursor: 'pointer',
                }}
              >
                <span>Open Intelligence Dossier</span>
                <ArrowRight size={16} />
              </button>
            )}

            {onCancel && (
              <button
                onClick={onCancel}
                className="glass-interactive"
                style={{
                  padding: '10px 14px',
                  borderRadius: '8px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  color: 'var(--text-secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '12px',
                  cursor: 'pointer',
                }}
                title="Dismiss or return to view"
              >
                <X size={14} />
                <span>Dismiss</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Grid: Left = 10 Stages Pipeline, Right = Live Telemetry Logs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1.2fr) minmax(320px, 1fr)', gap: '24px' }}>
        {/* Stages Card */}
        <div className="glass-panel" style={{ padding: '22px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={14} color="var(--accent-cyan)" />
            <span>10-Stage Idempotent Checkpointed Pipeline</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {PIPELINE_STAGES.map((stage, idx) => {
              const isPast = idx < currentStageIndex || status === 'completed';
              const isCurrent = idx === currentStageIndex && status === 'running';

              return (
                <div
                  key={stage.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    background: isCurrent ? 'rgba(0, 240, 255, 0.08)' : isPast ? 'rgba(16, 185, 129, 0.04)' : 'rgba(255, 255, 255, 0.01)',
                    border: isCurrent ? '1px solid var(--border-glow)' : isPast ? '1px solid rgba(16, 185, 129, 0.2)' : '1px solid var(--border-subtle)',
                    transition: 'all 0.2s ease',
                  }}
                >
                  {isPast ? (
                    <CheckCircle2 size={18} color="var(--accent-emerald)" />
                  ) : isCurrent ? (
                    <Loader2 size={18} color="var(--accent-cyan)" className="pulse-active" />
                  ) : (
                    <Circle size={18} color="var(--text-muted)" opacity={0.4} />
                  )}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '13px', fontWeight: isCurrent ? 700 : 500, color: isCurrent ? '#f8fafc' : isPast ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                      {stage.label}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{stage.desc}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Live SSE Telemetry Feed */}
        <div className="glass-panel" style={{ padding: '22px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '14px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Database size={14} color="var(--accent-cyan)" />
              <span>Live SSE Telemetry Stream</span>
            </div>
            <span style={{ fontSize: '10px', color: 'var(--accent-emerald)', fontFamily: 'var(--font-mono)' }}>
              PERSISTENT REPLAY READY
            </span>
          </div>

          <div
            ref={eventLogRef}
            style={{
              flex: 1,
              minHeight: '440px',
              maxHeight: '520px',
              overflowY: 'auto',
              background: 'rgba(7, 9, 14, 0.6)',
              borderRadius: '8px',
              padding: '12px 14px',
              border: '1px solid var(--border-subtle)',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
            }}
          >
            {events.length === 0 && (
              <div style={{ color: 'var(--text-muted)', fontStyle: 'italic', textAlign: 'center', paddingTop: '40px' }}>
                Connecting to real-time research event hub...
              </div>
            )}
            {events.map((ev, i) => (
              <div
                key={i}
                style={{
                  padding: '6px 8px',
                  borderRadius: '4px',
                  background: 'rgba(255, 255, 255, 0.02)',
                  borderLeft: `2px solid ${ev.event === 'job_completed' ? 'var(--accent-emerald)' : ev.event === 'job_failed' ? 'var(--accent-rose)' : 'var(--accent-cyan)'}`,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '10px' }}>
                  <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>[{ev.event}]</span>
                  <span>{ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : ''}</span>
                </div>
                <div style={{ color: 'var(--text-secondary)', marginTop: '2px', wordBreak: 'break-all' }}>
                  {JSON.stringify(ev.data || {})}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
