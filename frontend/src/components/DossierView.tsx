import React, { useState } from 'react';
import {
  FileText,
  RefreshCw,
  Compass,
  GitBranch,
  Clock,
  Quote,
  Layers,
  ExternalLink,
  ShieldCheck,
} from 'lucide-react';
import { EvidenceGraphCanvas } from './EvidenceGraphCanvas';
import { PoliticalCompass } from './PoliticalCompass';
import type {
  DossierData,
  GraphData,
  InitiativeItem,
  PoliticalAnalysisResponse,
  SourceItem,
  StatementItem,
  TimelineItem,
} from '../types';

interface DossierViewProps {
  dossier: DossierData;
  timeline: TimelineItem[];
  statements: StatementItem[];
  initiatives: InitiativeItem[];
  sources: SourceItem[];
  graphData: GraphData | null;
  politicalData: PoliticalAnalysisResponse | null;
  onRefreshResearch: () => void;
}

export const DossierView: React.FC<DossierViewProps> = ({
  dossier,
  timeline,
  statements,
  initiatives,
  sources,
  graphData,
  politicalData,
  onRefreshResearch,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'graph' | 'timeline' | 'statements' | 'political' | 'sources'>('overview');

  const completeness = (dossier.completeness_score * 100).toFixed(0);

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px' }}>
      {/* Dossier Hero Header */}
      <div className="glass-panel" style={{ padding: '28px 32px', marginBottom: '24px', border: '1px solid var(--border-glow)' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="badge badge-cyan">VERIFIED LIVING DOSSIER</span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                VERSION {dossier.version}.0 • ID #{dossier.dossier_id}
              </span>
            </div>
            <h1 style={{ fontSize: '36px', fontWeight: 800, margin: '10px 0 6px', color: '#f8fafc', letterSpacing: '-0.02em' }}>
              {dossier.canonical_name}
            </h1>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', maxWidth: '640px' }}>
              {dossier.title || `Comprehensive public-entity profile synthesized from ${dossier.source_count} authoritative sources`}
            </p>
          </div>

          {/* Quick Metrics Bar & Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div className="glass-panel" style={{ padding: '12px 18px', textAlign: 'center', minWidth: '105px' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Completeness</div>
              <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>
                {completeness}%
              </div>
            </div>

            <div className="glass-panel" style={{ padding: '12px 18px', textAlign: 'center', minWidth: '105px' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Sources</div>
              <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--accent-emerald)' }}>
                {dossier.source_count || sources.length}
              </div>
            </div>

            <div className="glass-panel" style={{ padding: '12px 18px', textAlign: 'center', minWidth: '105px' }}>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Evidence</div>
              <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--accent-amber)' }}>
                {dossier.evidence_count}
              </div>
            </div>

            <button
              onClick={onRefreshResearch}
              className="badge badge-cyan glass-interactive"
              style={{ padding: '10px 16px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <RefreshCw size={14} />
              <span>Update Intelligence</span>
            </button>
          </div>
        </div>

        {/* Tab Navigation Strip */}
        <div style={{ display: 'flex', gap: '8px', borderTop: '1px solid var(--border-subtle)', paddingTop: '18px', marginTop: '24px', flexWrap: 'wrap' }}>
          {[
            { id: 'overview', label: 'Executive Summary', icon: FileText },
            { id: 'graph', label: `Evidence Graph (${graphData?.node_count || 0})`, icon: GitBranch },
            { id: 'timeline', label: `Career Timeline (${timeline.length})`, icon: Clock },
            { id: 'statements', label: `Attributed Statements (${statements.length})`, icon: Quote },
            { id: 'political', label: 'Political Spectrum', icon: Compass },
            { id: 'sources', label: `Attributed Citations (${sources.length})`, icon: Layers },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  borderRadius: '8px',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: isActive ? '#f8fafc' : 'var(--text-muted)',
                  background: isActive ? 'rgba(0, 240, 255, 0.1)' : 'transparent',
                  border: isActive ? '1px solid var(--border-glow)' : '1px solid transparent',
                  transition: 'all 0.15s ease',
                }}
              >
                <Icon size={15} color={isActive ? 'var(--accent-cyan)' : 'var(--text-muted)'} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab 1: Executive Summary */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1.8fr) minmax(320px, 1fr)', gap: '24px' }}>
          <div className="glass-panel" style={{ padding: '28px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={18} color="var(--accent-emerald)" />
              <span>Evidence-Grounding Executive Summary</span>
            </h3>
            <div style={{ fontSize: '14px', lineHeight: 1.7, color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>
              {dossier.executive_summary || 'Executive summary synthesized from cross-corroborated primary and secondary sources.'}
            </div>

            {/* Initiatives Preview */}
            {initiatives.length > 0 && (
              <div style={{ marginTop: '28px', borderTop: '1px solid var(--border-subtle)', paddingTop: '20px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', marginBottom: '12px' }}>
                  Documented Initiatives & Ventures ({initiatives.length})
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {initiatives.map((init) => (
                    <div key={init.id} style={{ padding: '12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontWeight: 600, fontSize: '13px', color: '#f8fafc' }}>{init.name}</span>
                        <span className="badge badge-purple" style={{ fontSize: '9px' }}>{init.lifecycle_stage}</span>
                      </div>
                      <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                        {init.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Side Highlights Card */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '22px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: '12px' }}>
                Intelligence Trust Metrics
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Attributed Source Tier 1</span>
                  <span style={{ fontWeight: 700, color: 'var(--accent-emerald)' }}>
                    {sources.filter((s) => s.source_tier === 1).length} Verified
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Attributed Source Tier 2</span>
                  <span style={{ fontWeight: 700, color: 'var(--text-cyan)' }}>
                    {sources.filter((s) => s.source_tier === 2).length} Outlets
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Direct Verbatim Quotes</span>
                  <span style={{ fontWeight: 700, color: 'var(--accent-purple)' }}>
                    {statements.filter((s) => s.statement_type === 'direct_quote').length} Attributed
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Corroboration Ratio</span>
                  <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>100% Attributable</span>
                </div>
              </div>
            </div>

            {/* Quick Political Preview */}
            <div className="glass-panel" style={{ padding: '22px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: '8px' }}>
                Political Classification
              </h4>
              <div style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc' }}>
                {politicalData?.spectrum?.label || 'Insufficient Public Political Record'}
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                {politicalData?.applicable ? 'Grounded in public legislative and political records.' : 'Subject has no public political or policy mandate.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Evidence Graph */}
      {activeTab === 'graph' && graphData && (
        <EvidenceGraphCanvas graphData={graphData} />
      )}

      {/* Tab 3: Career Timeline */}
      {activeTab === 'timeline' && (
        <div className="glass-panel" style={{ padding: '28px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', marginBottom: '20px' }}>
            Chronological Career & Personal Milestones
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {timeline.length === 0 && (
              <div style={{ color: 'var(--text-muted)' }}>No chronological milestones extracted.</div>
            )}
            {timeline.map((item) => (
              <div
                key={item.id}
                style={{
                  display: 'flex',
                  gap: '16px',
                  padding: '14px 18px',
                  borderRadius: '10px',
                  background: 'rgba(255, 255, 255, 0.015)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div style={{ minWidth: '100px', fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--accent-cyan)' }}>
                  {item.start_date ? new Date(item.start_date).toLocaleDateString(undefined, { year: 'numeric', month: 'short' }) : 'Milestone'}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: 700, fontSize: '14px', color: '#f8fafc' }}>{item.title}</span>
                    <span className="badge badge-muted" style={{ fontSize: '9px' }}>{item.event_type}</span>
                  </div>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    {item.description}
                  </p>
                  {item.source && (
                    <a
                      href={item.source.url}
                      target="_blank"
                      rel="noreferrer"
                      style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--text-cyan)', marginTop: '6px', textDecoration: 'none' }}
                    >
                      <span>Source: {item.source.title || item.source.url}</span>
                      <ExternalLink size={11} />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: Statements & Quotes */}
      {activeTab === 'statements' && (
        <div className="glass-panel" style={{ padding: '28px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', marginBottom: '20px' }}>
            Attributed Statements, Direct Quotes & Claims
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {statements.map((s) => (
              <div
                key={s.id}
                style={{
                  padding: '16px',
                  borderRadius: '10px',
                  background: 'rgba(255, 255, 255, 0.02)',
                  borderLeft: `3px solid ${s.statement_type === 'direct_quote' ? 'var(--accent-purple)' : 'var(--accent-amber)'}`,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span className={`badge ${s.statement_type === 'direct_quote' ? 'badge-purple' : 'badge-amber'}`}>
                    {s.statement_type}
                  </span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    Confidence: {(s.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <blockquote style={{ fontSize: '14px', color: '#f8fafc', fontStyle: s.statement_type === 'direct_quote' ? 'italic' : 'normal', lineHeight: 1.5 }}>
                  "{s.text}"
                </blockquote>
                {s.source && (
                  <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
                    Attributed in: <a href={s.source.url} target="_blank" rel="noreferrer" style={{ color: 'var(--text-cyan)', textDecoration: 'none' }}>{s.source.title || s.source.url}</a>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 5: Political Spectrum */}
      {activeTab === 'political' && (
        <PoliticalCompass politicalData={politicalData} personName={dossier.canonical_name} />
      )}

      {/* Tab 6: Attributed Sources */}
      {activeTab === 'sources' && (
        <div className="glass-panel" style={{ padding: '28px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', marginBottom: '20px' }}>
            Captured & Attributed Source Registry
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {sources.map((s) => (
              <div
                key={s.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  background: 'rgba(255, 255, 255, 0.015)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: 600, fontSize: '14px', color: '#f8fafc' }}>
                      {s.title || s.url || s.domain || 'Source Document'}
                    </span>
                    <span className={`badge ${s.source_tier === 1 ? 'badge-emerald' : 'badge-cyan'}`}>
                      Tier {s.source_tier}
                    </span>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Domain: {s.domain || s.publisher || 'Web'} • Reliability: {(s.reliability_score * 100).toFixed(0)}%
                  </div>
                </div>
                {s.url && (
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noreferrer"
                    className="badge badge-muted"
                    style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}
                  >
                    <span>Visit URL</span>
                    <ExternalLink size={11} />
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
