import React, { useState, useEffect } from 'react';
import { Search, ArrowRight, Loader2 } from 'lucide-react';
import { personaApi } from '../services/api';
import type { PersonListItem } from '../types';

interface EntitiesDirectoryProps {
  onSelectPerson: (personId: number) => void;
  onOpenSearch: () => void;
}

export const EntitiesDirectory: React.FC<EntitiesDirectoryProps> = ({
  onSelectPerson,
  onOpenSearch,
}) => {
  const [persons, setPersons] = useState<PersonListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filterProfession, setFilterProfession] = useState<string>('all');

  useEffect(() => {
    personaApi.listPersons(100, 0)
      .then((res) => {
        setPersons(res.items || []);
        setTotal(res.total || 0);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const professions = ['all', 'athlete', 'entrepreneur', 'politician', 'scientist', 'actor', 'journalist'];

  const filtered = filterProfession === 'all'
    ? persons
    : persons.filter((p) => (p.primary_profession || '').toLowerCase().includes(filterProfession.toLowerCase()));

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px' }}>
      {/* Directory Header */}
      <div className="glass-panel" style={{ padding: '24px 28px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-cyan">PUBLIC FIGURES DIRECTORY</span>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{total} INDEXED ENTITIES</span>
          </div>
          <h2 style={{ fontSize: '24px', fontWeight: 800, color: '#f8fafc', margin: '6px 0 2px' }}>
            Universal Public-Person Knowledge Index
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            Authoritative, evidence-backed public intelligence dossiers across global athletics, industry, governance, and science.
          </p>
        </div>

        <button
          onClick={onOpenSearch}
          className="badge badge-cyan glass-interactive"
          style={{ padding: '10px 16px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          <Search size={14} />
          <span>Disambiguate New Figure</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
        {professions.map((prof) => (
          <button
            key={prof}
            onClick={() => setFilterProfession(prof)}
            style={{
              padding: '6px 14px',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: 600,
              textTransform: 'capitalize',
              background: filterProfession === prof ? 'var(--accent-cyan)' : 'rgba(18, 24, 36, 0.6)',
              color: filterProfession === prof ? '#07090e' : 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
              transition: 'all 0.15s ease',
            }}
          >
            {prof}
          </button>
        ))}
      </div>

      {/* Cards Grid */}
      {loading ? (
        <div style={{ padding: '60px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
          <Loader2 size={32} color="var(--accent-cyan)" className="pulse-active" style={{ margin: '0 auto 12px' }} />
          <div>Loading verified intelligence records...</div>
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
          No records matching the selected profession filter. Use the search omnibar to synthesize new figures.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '18px' }}>
          {filtered.map((p) => (
            <div
              key={p.id}
              onClick={() => onSelectPerson(p.id)}
              className="glass-panel glass-interactive"
              style={{
                padding: '20px',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <span className="badge badge-purple" style={{ fontSize: '10px' }}>
                    {p.primary_profession || 'Public Entity'}
                  </span>
                  {p.has_dossier && (
                    <span className="badge badge-emerald" style={{ fontSize: '9px' }}>
                      Dossier Ready
                    </span>
                  )}
                </div>

                <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', marginBottom: '6px' }}>
                  {p.canonical_name}
                </h3>

                <div style={{ display: 'flex', gap: '12px', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '14px' }}>
                  <span>{p.counts.sources} Attributed Sources</span>
                  <span>•</span>
                  <span>{p.counts.evidence} Evidence Units</span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: '12px', marginTop: '6px' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  ID #{p.id} • {(p.identity_confidence * 100).toFixed(0)}% Confidence
                </span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', fontWeight: 600, color: 'var(--text-cyan)' }}>
                  <span>Open Dossier</span>
                  <ArrowRight size={13} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
