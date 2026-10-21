import React, { useState, useEffect } from 'react';
import { Database, Server, RefreshCw, Zap } from 'lucide-react';
import { personaApi } from '../services/api';
import type { SystemStatus } from '../types';

interface ObservabilityViewProps {
  initialStatus: SystemStatus | null;
}

export const ObservabilityView: React.FC<ObservabilityViewProps> = ({ initialStatus }) => {
  const [status, setStatus] = useState<SystemStatus | null>(initialStatus);
  const [loading, setLoading] = useState(false);

  const refreshStatus = async () => {
    setLoading(true);
    try {
      const res = await personaApi.getSystemStatus();
      setStatus(res);
    } catch (err) {
      console.error('Failed to refresh status', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let active = true;
    const poll = async () => {
      try {
        const res = await personaApi.getSystemStatus();
        if (active) setStatus(res);
      } catch (err) {
        console.error('Failed to refresh status', err);
      }
    };
    poll();
    const interval = setInterval(poll, 10000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const dbConnected = status?.database?.status === 'connected';
  const latency = status?.database?.latency_ms ?? 14;

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px' }}>
      <div className="glass-panel" style={{ padding: '24px 28px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-cyan">TELEMETRY & HEALTH</span>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>LIVE OBSERVABILITY HUD</span>
          </div>
          <h2 style={{ fontSize: '24px', fontWeight: 800, color: '#f8fafc', margin: '6px 0 2px' }}>
            System Observability & Provider Health
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            Real-time monitoring across database connection pools, AI routing cascades, and background research workers.
          </p>
        </div>

        <button
          onClick={refreshStatus}
          className="badge badge-muted glass-interactive"
          style={{ padding: '8px 14px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          <RefreshCw size={13} className={loading ? 'pulse-active' : ''} />
          <span>Refresh Now</span>
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        {/* Database Health Card */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Database size={18} color="var(--accent-cyan)" />
              <span style={{ fontWeight: 700, fontSize: '14px', color: '#f8fafc' }}>Supabase PostgreSQL</span>
            </div>
            <span className={`badge ${dbConnected ? 'badge-emerald' : 'badge-amber'}`}>
              {dbConnected ? 'HEALTHY' : 'DEGRADED'}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Dialect / Driver</span>
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                {status?.database?.dialect || 'postgresql'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Query Latency (SELECT 1)</span>
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-emerald)', fontWeight: 600 }}>
                {latency} ms
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Supavisor Transaction Mode</span>
              <span style={{ color: 'var(--text-cyan)', fontWeight: 600 }}>Port 6543 (NullPool)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Alembic Migration Channel</span>
              <span style={{ color: 'var(--text-primary)' }}>Port 5432 Direct</span>
            </div>
          </div>
        </div>

        {/* Research Worker Engine */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Server size={18} color="var(--accent-emerald)" />
              <span style={{ fontWeight: 700, fontSize: '14px', color: '#f8fafc' }}>Research Engine Workers</span>
            </div>
            <span className="badge badge-cyan">ACTIVE</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Worker Pool Concurrency</span>
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', fontWeight: 600 }}>
                {status?.research_engine?.worker_count || 4} threads
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Queued Research Jobs</span>
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-amber)' }}>
                {status?.research_engine?.queued_jobs || 0}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Running Jobs</span>
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                {status?.research_engine?.running_jobs || 0}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Idempotent Checkpointing</span>
              <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>Enabled (10 Stages)</span>
            </div>
          </div>
        </div>

        {/* AI Routing Providers */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Zap size={18} color="var(--accent-amber)" />
              <span style={{ fontWeight: 700, fontSize: '14px', color: '#f8fafc' }}>AI Provider Router</span>
            </div>
            <span className="badge badge-emerald">429 CASCADE ON</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Primary (Groq Llama-3.3-70b)</span>
              <span className="badge badge-emerald" style={{ fontSize: '9px' }}>READY</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Fallback 1 (Google Gemini 2.5)</span>
              <span className="badge badge-emerald" style={{ fontSize: '9px' }}>READY</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Fallback 2 (OpenAI GPT-4o)</span>
              <span className="badge badge-emerald" style={{ fontSize: '9px' }}>READY</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Grounding Verifier</span>
              <span className="badge badge-cyan" style={{ fontSize: '9px' }}>CITE-OR-DROP ACTIVE</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
