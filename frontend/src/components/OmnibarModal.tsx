import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, X, Sparkles, Globe, UserCheck, ArrowRight, Loader2, BookOpen } from 'lucide-react';
import { personaApi } from '../services/api';
import type { ExternalCandidate, PersonSearchResult } from '../types';

interface OmnibarModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectPerson: (personId: number) => void;
  onStartResearch: (personName: string) => void;
}

export const OmnibarModal: React.FC<OmnibarModalProps> = ({
  isOpen,
  onClose,
  onSelectPerson,
  onStartResearch,
}) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [localPersons, setLocalPersons] = useState<PersonSearchResult[]>([]);
  const [candidates, setCandidates] = useState<ExternalCandidate[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleClose = useCallback(() => {
    setQuery('');
    setLocalPersons([]);
    setCandidates([]);
    onClose();
  }, [onClose]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) handleClose();
      }
      if (e.key === 'Escape' && isOpen) {
        handleClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, handleClose]);

  const handleQueryChange = (val: string) => {
    setQuery(val);
    if (!val.trim() || val.trim().length < 2) {
      setLocalPersons([]);
      setCandidates([]);
    }
  };

  // Debounced search
  useEffect(() => {
    if (!query.trim() || query.trim().length < 2) {
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await personaApi.search(query.trim(), true);
        setLocalPersons(res.local_persons || []);
        setCandidates(res.external_candidates || []);
      } catch (err) {
        console.error('Search error:', err);
      } finally {
        setLoading(false);
      }
    }, 280);

    return () => clearTimeout(timer);
  }, [query]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 50,
        backgroundColor: 'rgba(7, 9, 14, 0.85)',
        backdropFilter: 'blur(12px)',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '80px',
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) handleClose();
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '720px',
          maxHeight: '80vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 24px 64px -12px rgba(0, 0, 0, 0.8), 0 0 40px rgba(0, 240, 255, 0.15)',
          border: '1px solid var(--border-glow)',
          overflow: 'hidden',
        }}
      >
        {/* Search Input Bar */}
        <div style={{ display: 'flex', alignItems: 'center', padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', gap: '12px' }}>
          <Search size={20} color="var(--accent-cyan)" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => handleQueryChange(e.target.value)}
            placeholder="Search any public figure (e.g. Jasprit Bumrah, Arvind Kejriwal, Sundar Pichai)..."
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--text-primary)',
              fontSize: '16px',
              fontFamily: 'var(--font-sans)',
            }}
          />
          {loading && <Loader2 size={18} color="var(--accent-cyan)" className="pulse-active" />}
          {query && !loading && (
            <button onClick={() => handleQueryChange('')} style={{ color: 'var(--text-muted)' }}>
              <X size={16} />
            </button>
          )}
          <button
            onClick={handleClose}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              padding: '4px 8px',
              borderRadius: '6px',
              fontSize: '11px',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            ESC
          </button>
        </div>

        {/* Search Results Container */}
        <div style={{ overflowY: 'auto', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Quick Instant Research Option */}
          {query.trim().length >= 2 && (
            <div
              onClick={() => {
                onStartResearch(query.trim());
                handleClose();
              }}
              className="glass-interactive"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '12px 16px',
                borderRadius: '10px',
                background: 'linear-gradient(90deg, rgba(0, 240, 255, 0.08) 0%, rgba(59, 130, 246, 0.04) 100%)',
                border: '1px solid rgba(0, 240, 255, 0.25)',
                cursor: 'pointer',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Sparkles size={18} color="var(--accent-cyan)" />
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#f1f5f9' }}>
                    Autonomous Deep Research: <span style={{ color: 'var(--accent-cyan)' }}>"{query.trim()}"</span>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    Launch multi-source web crawl, evidence extraction, and living dossier synthesis
                  </div>
                </div>
              </div>
              <ArrowRight size={16} color="var(--accent-cyan)" />
            </div>
          )}

          {/* Section 1: Local Verified Records */}
          {localPersons.length > 0 && (
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <UserCheck size={13} color="var(--accent-emerald)" />
                <span>Verified Local Records ({localPersons.length})</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {localPersons.map((p) => (
                  <div
                    key={p.id}
                    onClick={() => {
                      onSelectPerson(p.id);
                      handleClose();
                    }}
                    className="glass-interactive"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px 14px',
                      borderRadius: '8px',
                      background: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid var(--border-subtle)',
                      cursor: 'pointer',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: 600, fontSize: '14px', color: '#f8fafc' }}>{p.canonical_name}</span>
                        {p.primary_profession && (
                          <span className="badge badge-cyan" style={{ fontSize: '10px' }}>{p.primary_profession}</span>
                        )}
                        <span className="badge badge-emerald" style={{ fontSize: '9px' }}>Dossier Ready</span>
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                        Confidence: {(p.identity_confidence * 100).toFixed(0)}% • Record ID #{p.id}
                      </div>
                    </div>
                    <ArrowRight size={14} color="var(--text-secondary)" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section 2: External Candidates (Wikidata Disambiguation) */}
          {candidates.length > 0 && (
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Globe size={13} color="var(--accent-cyan)" />
                <span>Wikidata Disambiguation Candidates ({candidates.length})</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {candidates.map((c, i) => (
                  <div
                    key={c.wikidata_id || i}
                    onClick={() => {
                      onStartResearch(c.label);
                      handleClose();
                    }}
                    className="glass-interactive"
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      padding: '12px 14px',
                      borderRadius: '8px',
                      background: 'rgba(255, 255, 255, 0.015)',
                      border: '1px solid var(--border-subtle)',
                      cursor: 'pointer',
                      gap: '12px',
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                        <span style={{ fontWeight: 600, fontSize: '14px', color: '#f8fafc' }}>{c.label}</span>
                        <span className="badge badge-muted" style={{ fontSize: '9px', fontFamily: 'var(--font-mono)' }}>{c.wikidata_id}</span>
                        {c.birth_year && (
                          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>b. {c.birth_year}</span>
                        )}
                        {c.professions?.slice(0, 2).map((prof) => (
                          <span key={prof} className="badge badge-purple" style={{ fontSize: '9px' }}>{prof}</span>
                        ))}
                      </div>
                      <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.4 }}>
                        {c.description || 'Public entity candidate from Wikidata'}
                      </p>
                    </div>
                    <button
                      className="badge badge-cyan"
                      style={{ padding: '6px 10px', fontSize: '11px', whiteSpace: 'nowrap' }}
                    >
                      Synthesize
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty Prompt State */}
          {!query && (
            <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
              <BookOpen size={32} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
              <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-secondary)' }}>
                Type any public figure to search or synthesize
              </div>
              <p style={{ fontSize: '12px', maxWidth: '380px', margin: '4px auto 0' }}>
                All intelligence dossiers are evidence-grounded using authoritative, attributable public records.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
