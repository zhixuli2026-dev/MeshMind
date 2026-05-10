import React from 'react';

interface Source { N: number; title: string; node_id: string; }

export const SourcePanel: React.FC<{ sources: Source[] }> = ({ sources }) => (
  <div>
    <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-secondary)', margin: '0 0 12px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
      Sources
    </h3>
    {sources.length === 0 && (
      <p style={{ fontSize: 13, color: 'var(--color-text-tertiary)' }}>Sources will appear here</p>
    )}
    {sources.map(s => (
      <div key={s.N} style={{
        padding: '10px 14px', marginBottom: 6,
        background: 'var(--color-bg-secondary)',
        borderRadius: 'var(--radius-sm)',
        border: '1px solid var(--color-border-light)',
        fontSize: 13,
      }}>
        <span style={{ fontWeight: 600, color: 'var(--color-accent)', marginRight: 8 }}>
          [{s.N}]
        </span>
        {s.title}
        <div style={{ fontSize: 11, color: 'var(--color-text-tertiary)', marginTop: 2 }}>
          {s.node_id.slice(0, 8)}...
        </div>
      </div>
    ))}
  </div>
);
