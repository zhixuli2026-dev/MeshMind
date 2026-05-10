import React from 'react';

interface Step { agent_id: string; step: string; detail: string; }

const stepColors: Record<string, string> = {
  Think: 'var(--color-accent)',
  Act: 'var(--color-warning)',
  Observe: '#5856d6',
};

export const ReactLoopTimeline: React.FC<{ steps: Step[] }> = ({ steps }) => {
  const recent = steps.slice(-20);
  return (
    <div style={{ marginTop: 24 }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-secondary)', margin: '0 0 12px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        React Loop
      </h3>
      {recent.length === 0 && (
        <p style={{ fontSize: 13, color: 'var(--color-text-tertiary)' }}>No activity yet</p>
      )}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {recent.map((s, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'flex-start', gap: 8, fontSize: 12,
            padding: '6px 0', borderBottom: '1px solid var(--color-border-light)',
          }}>
            <span style={{
              fontWeight: 600, color: stepColors[s.step] || 'var(--color-text-secondary)',
              minWidth: 56,
            }}>{s.step}</span>
            <span style={{ color: 'var(--color-text-secondary)', wordBreak: 'break-word' }}>
              {s.detail.length > 120 ? s.detail.slice(0, 120) + '...' : s.detail}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
