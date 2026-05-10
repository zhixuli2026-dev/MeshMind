import React, { useEffect, useState } from 'react';
import { Card } from '@meshmind/design-system/src/components/Card';

export const MembersPage: React.FC = () => {
  const [members, setMembers] = useState<any[]>([]);
  const wsId = localStorage.getItem('meshmind_workspace_id') || '';

  useEffect(() => {
    if (!wsId) return;
    fetch(`/api/v1/workspaces/${wsId}/members`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('meshmind_token')}` },
    }).then(r => r.json()).then(d => setMembers(d.members || [])).catch(console.error);
  }, [wsId]);

  return (
    <div>
      <h1 style={{ fontSize: 28, fontWeight: 700, margin: '0 0 24px 0' }}>Members</h1>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {members.map((m: any) => (
          <Card key={m.author_id}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 600 }}>{m.name || m.user_id}</div>
                <div style={{ fontSize: 12, color: 'var(--color-text-tertiary)' }}>{m.user_id}</div>
              </div>
            </div>
          </Card>
        ))}
        {members.length === 0 && (
          <p style={{ color: 'var(--color-text-tertiary)' }}>No members yet.</p>
        )}
      </div>
    </div>
  );
};
