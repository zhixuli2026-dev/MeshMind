import React, { useEffect, useState } from 'react';
import { Card } from '@meshmind/design-system/src/components/Card';
import { getWorkspaceStats } from '@meshmind/api-client/src/index';

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const wsId = localStorage.getItem('meshmind_workspace_id') || '';

  useEffect(() => {
    if (wsId) getWorkspaceStats(wsId).then(setStats).catch(console.error);
  }, [wsId]);

  return (
    <div>
      <h1 style={{ fontSize: 28, fontWeight: 700, margin: '0 0 32px 0' }}>Dashboard</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
        <Card>
          <div style={{ fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 8 }}>Total Knowledge Nodes</div>
          <div style={{ fontSize: 36, fontWeight: 700 }}>{stats?.node_count ?? '—'}</div>
        </Card>
        <Card>
          <div style={{ fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 8 }}>Types</div>
          <div style={{ fontSize: 14 }}>
            {stats?.type_distribution ? Object.entries(stats.type_distribution).map(([k, v]) => (
              <div key={k} style={{ marginBottom: 4 }}>{k}: <strong>{v as number}</strong></div>
            )) : '—'}
          </div>
        </Card>
        <Card>
          <div style={{ fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 8 }}>Workspace</div>
          <div style={{ fontSize: 14, wordBreak: 'break-all', color: 'var(--color-text-tertiary)' }}>
            {wsId || 'No workspace selected'}
          </div>
        </Card>
      </div>
    </div>
  );
};
