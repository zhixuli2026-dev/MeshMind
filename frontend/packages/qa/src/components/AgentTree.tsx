import React from 'react';

interface Agent { id: string; topic: string; status: 'thinking' | 'acting' | 'observing' | 'done'; }

const statusColors: Record<string, string> = {
  thinking: 'var(--color-accent)',
  acting: 'var(--color-warning)',
  observing: '#5856d6',
  done: 'var(--color-success)',
};

export const AgentTree: React.FC<{ agents: Agent[] }> = ({ agents }) => (
  <div>
    <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-secondary)', margin: '0 0 12px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
      Agents
    </h3>
    {agents.length === 0 && (
      <p style={{ fontSize: 13, color: 'var(--color-text-tertiary)' }}>Waiting for agents...</p>
    )}
    {agents.map(a => (
      <div key={a.id} style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '10px 14px', marginBottom: 6,
        background: 'var(--color-bg-secondary)',
        borderRadius: 'var(--radius-sm)',
        border: '1px solid var(--color-border-light)',
      }}>
        <div style={{
          width: 8, height: 8, borderRadius: 4,
          background: statusColors[a.status],
          transition: 'background var(--transition-normal)',
        }} />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 13, fontWeight: 500 }}>{a.topic}</div>
          <div style={{ fontSize: 11, color: 'var(--color-text-tertiary)' }}>{a.id} · {a.status}</div>
        </div>
      </div>
    ))}
  </div>
);
