import React from 'react';
import { Search, Database } from 'lucide-react';
import type { SystemStatus } from '../types';

interface HeaderProps {
  systemStatus: SystemStatus | null;
  onOpenSearch: () => void;
  activeView: string;
  setActiveView: (view: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  systemStatus,
  onOpenSearch,
  activeView,
  setActiveView,
}) => {
  const isConnected = systemStatus?.status === 'ok';
  const latency = systemStatus?.database?.latency_ms ?? 12;

  return (
    <header className="glass-panel" style={{ borderRadius: '0', borderLeft: 'none', borderRight: 'none', borderTop: 'none', padding: '14px 28px', position: 'sticky', top: 0, zIndex: 40 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', maxWidth: '1440px', margin: '0 auto' }}>
        {/* Brand Logo & Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
          <div 
            onClick={() => setActiveView('dossier')}
            style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}
          >
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #00f0ff 0%, #3b82f6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(0, 240, 255, 0.4)'
            }}>
              <span style={{ fontWeight: 800, fontSize: '18px', color: '#07090e' }}>X</span>
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontWeight: 800, fontSize: '17px', letterSpacing: '0.08em', color: '#f1f5f9' }}>
                  PERSONA<span style={{ color: 'var(--accent-cyan)' }}>-X</span>
                </span>
                <span className="badge badge-cyan" style={{ fontSize: '9px', padding: '2px 6px' }}>v1.0 INTEL</span>
              </div>
              <p style={{ fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.02em' }}>
                Universal Public-Person Intelligence
              </p>
            </div>
          </div>

          <div style={{ height: '24px', width: '1px', background: 'var(--border-subtle)' }} />

          {/* Navigation Links */}
          <nav style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <button
              onClick={() => setActiveView('dossier')}
              style={{
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: 600,
                color: activeView === 'dossier' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                background: activeView === 'dossier' ? 'rgba(0, 240, 255, 0.08)' : 'transparent',
                border: activeView === 'dossier' ? '1px solid rgba(0, 240, 255, 0.25)' : '1px solid transparent',
                transition: 'all 0.15s ease'
              }}
            >
              Intelligence Dossiers
            </button>
            <button
              onClick={() => setActiveView('entities')}
              style={{
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: 600,
                color: activeView === 'entities' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                background: activeView === 'entities' ? 'rgba(0, 240, 255, 0.08)' : 'transparent',
                border: activeView === 'entities' ? '1px solid rgba(0, 240, 255, 0.25)' : '1px solid transparent',
                transition: 'all 0.15s ease'
              }}
            >
              Entities Directory
            </button>
            <button
              onClick={() => setActiveView('observability')}
              style={{
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: 600,
                color: activeView === 'observability' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                background: activeView === 'observability' ? 'rgba(0, 240, 255, 0.08)' : 'transparent',
                border: activeView === 'observability' ? '1px solid rgba(0, 240, 255, 0.25)' : '1px solid transparent',
                transition: 'all 0.15s ease'
              }}
            >
              Observability
            </button>
          </nav>
        </div>

        {/* Search Trigger & Status Indicators */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {/* Quick Search Omnibar Trigger */}
          <button
            onClick={onOpenSearch}
            className="glass-interactive"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '8px 16px',
              borderRadius: '10px',
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-medium)',
              color: 'var(--text-secondary)',
              minWidth: '280px',
              justifyContent: 'space-between',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Search size={15} color="var(--accent-cyan)" />
              <span style={{ fontSize: '13px' }}>Disambiguate public figure...</span>
            </div>
            <span style={{
              fontSize: '10px',
              fontFamily: 'var(--font-mono)',
              background: 'rgba(255, 255, 255, 0.07)',
              padding: '2px 6px',
              borderRadius: '4px',
              border: '1px solid var(--border-subtle)',
            }}>
              Ctrl+K
            </span>
          </button>

          {/* Database & System Pulse */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px', color: 'var(--text-muted)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                background: isConnected ? 'var(--accent-emerald)' : 'var(--accent-rose)',
                boxShadow: isConnected ? '0 0 10px var(--accent-emerald)' : 'none',
              }} className={isConnected ? 'pulse-active' : ''} />
              <span style={{ color: isConnected ? 'var(--text-emerald)' : 'var(--accent-rose)', fontWeight: 600 }}>
                {isConnected ? 'ONLINE' : 'CONNECTING'}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontFamily: 'var(--font-mono)' }}>
              <Database size={13} color="var(--text-muted)" />
              <span>{latency}ms</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
