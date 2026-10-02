import React from 'react';
import { Compass, AlertCircle, CheckCircle, Info } from 'lucide-react';
import type { PoliticalAnalysisResponse } from '../types';

interface PoliticalCompassProps {
  politicalData: PoliticalAnalysisResponse | null;
  personName: string;
}

export const PoliticalCompass: React.FC<PoliticalCompassProps> = ({
  politicalData,
  personName,
}) => {
  if (!politicalData) {
    return (
      <div className="glass-panel" style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
        No political spectrum record synthesized for {personName}.
      </div>
    );
  }

  const isApplicable = politicalData.applicable && politicalData.spectrum?.applicable;
  const spectrum = politicalData.spectrum;

  // Coordinate mapping (-1.0..+1.0 -> 0%..100%)
  const econX = spectrum?.economic_axis !== null && spectrum?.economic_axis !== undefined
    ? ((spectrum.economic_axis + 1) / 2) * 100
    : 50;

  const socialY = spectrum?.social_axis !== null && spectrum?.social_axis !== undefined
    ? ((1 - spectrum.social_axis) / 2) * 100 // Inverted Y (Authoritarian up, Libertarian down)
    : 50;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1fr) minmax(320px, 1.2fr)', gap: '24px' }}>
      {/* 2D Compass Graph Card */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Compass size={16} color="var(--accent-cyan)" />
            <span style={{ fontSize: '13px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Political Spectrum Matrix
            </span>
          </div>
          <span className={`badge ${isApplicable ? 'badge-cyan' : 'badge-amber'}`}>
            {isApplicable ? spectrum?.label || 'Analyzed' : 'Non-Political Record'}
          </span>
        </div>

        {/* 2D Grid Plot */}
        <div
          style={{
            position: 'relative',
            width: '280px',
            height: '280px',
            borderRadius: '12px',
            background: 'rgba(7, 9, 14, 0.7)',
            border: '1px solid var(--border-medium)',
            overflow: 'hidden',
          }}
        >
          {/* Quadrant Backdrops */}
          <div style={{ position: 'absolute', top: 0, left: 0, width: '50%', height: '50%', background: 'rgba(239, 68, 68, 0.04)', borderRight: '1px solid var(--border-subtle)', borderBottom: '1px solid var(--border-subtle)' }}>
            <span style={{ position: 'absolute', top: 6, left: 6, fontSize: '9px', color: 'rgba(239, 68, 68, 0.6)', fontWeight: 600 }}>AUTH LEFT</span>
          </div>
          <div style={{ position: 'absolute', top: 0, right: 0, width: '50%', height: '50%', background: 'rgba(59, 130, 246, 0.04)', borderBottom: '1px solid var(--border-subtle)' }}>
            <span style={{ position: 'absolute', top: 6, right: 6, fontSize: '9px', color: 'rgba(59, 130, 246, 0.6)', fontWeight: 600 }}>AUTH RIGHT</span>
          </div>
          <div style={{ position: 'absolute', bottom: 0, left: 0, width: '50%', height: '50%', background: 'rgba(16, 185, 129, 0.04)', borderRight: '1px solid var(--border-subtle)' }}>
            <span style={{ position: 'absolute', bottom: 6, left: 6, fontSize: '9px', color: 'rgba(16, 185, 129, 0.6)', fontWeight: 600 }}>LIB LEFT</span>
          </div>
          <div style={{ position: 'absolute', bottom: 0, right: 0, width: '50%', height: '50%', background: 'rgba(245, 158, 11, 0.04)' }}>
            <span style={{ position: 'absolute', bottom: 6, right: 6, fontSize: '9px', color: 'rgba(245, 158, 11, 0.6)', fontWeight: 600 }}>LIB RIGHT</span>
          </div>

          {/* Crosshairs */}
          <div style={{ position: 'absolute', top: '50%', left: 0, right: 0, height: '1px', background: 'rgba(255, 255, 255, 0.15)' }} />
          <div style={{ position: 'absolute', left: '50%', top: 0, bottom: 0, width: '1px', background: 'rgba(255, 255, 255, 0.15)' }} />

          {/* Plotted Position Pin (Only if applicable) */}
          {isApplicable ? (
            <div
              style={{
                position: 'absolute',
                top: `${socialY}%`,
                left: `${econX}%`,
                transform: 'translate(-50%, -50%)',
                width: '14px',
                height: '14px',
                borderRadius: '50%',
                background: 'var(--accent-cyan)',
                border: '2px solid #ffffff',
                boxShadow: '0 0 16px var(--accent-cyan)',
                zIndex: 10,
              }}
              className="pulse-active"
            />
          ) : (
            <div
              style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'rgba(7, 9, 14, 0.85)',
                backdropFilter: 'blur(4px)',
                textAlign: 'center',
                padding: '16px',
              }}
            >
              <div>
                <AlertCircle size={28} color="var(--accent-amber)" style={{ margin: '0 auto 8px' }} />
                <div style={{ fontSize: '12px', fontWeight: 600, color: '#f8fafc' }}>
                  Insufficient Political Record
                </div>
                <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Non-political figure with no policy or legislative mandate
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Axis Labels */}
        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px' }}>
          <span>Economic: {spectrum?.economic_axis !== null ? spectrum?.economic_axis : 'N/A'}</span>
          <span>Social: {spectrum?.social_axis !== null ? spectrum?.social_axis : 'N/A'}</span>
        </div>
      </div>

      {/* Analysis Details & Indicators */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)' }}>
            Assessment Verdict
          </div>
          <h3 style={{ fontSize: '20px', fontWeight: 700, color: '#f8fafc', marginTop: '4px' }}>
            {isApplicable ? spectrum?.label : 'Insufficient Public Political Record'}
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '6px', lineHeight: 1.5 }}>
            {spectrum?.rationale || politicalData.sufficiency?.reason || 'Evaluation grounded solely on public attributable statements and verified records.'}
          </p>
        </div>

        {/* Key Indicators */}
        {spectrum?.key_indicators && spectrum.key_indicators.length > 0 && (
          <div>
            <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '8px' }}>
              Identified Factual Indicators
            </div>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {spectrum.key_indicators.map((ind, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  <CheckCircle size={14} color="var(--accent-emerald)" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span>{ind}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Evidence Sufficiency Disclaimer */}
        <div style={{ padding: '12px 14px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', display: 'flex', gap: '10px' }}>
          <Info size={16} color="var(--accent-cyan)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', lineHeight: 1.4 }}>
            <strong>Methodology & Limitations</strong>: Political spectra are computed strictly when attributable policy statements, political offices, or legislative actions exist. When public evidence is absent or insufficient (e.g. for athletes, artists, or private executives), the platform strictly reports an insufficient public record.
          </div>
        </div>
      </div>
    </div>
  );
};
