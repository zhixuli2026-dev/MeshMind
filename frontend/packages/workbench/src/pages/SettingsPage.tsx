import React, { useState } from 'react';
import { Card } from '@meshmind/design-system/src/components/Card';
import { Input } from '@meshmind/design-system/src/components/Input';
import { Button } from '@meshmind/design-system/src/components/Button';
import { createWorkspace } from '@meshmind/api-client/src/index';

export const SettingsPage: React.FC = () => {
  const [name, setName] = useState('');
  const [creating, setCreating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleCreate = async () => {
    if (!name.trim()) return;
    setCreating(true);
    try {
      const ws = await createWorkspace(name);
      setResult(ws);
      localStorage.setItem('meshmind_workspace_id', ws.workspace_id);
    } catch (e: any) {
      setResult({ error: e.message });
    }
    setCreating(false);
  };

  return (
    <div>
      <h1 style={{ fontSize: 28, fontWeight: 700, margin: '0 0 24px 0' }}>Settings</h1>
      <Card>
        <h3 style={{ fontSize: 16, fontWeight: 600, margin: '0 0 16px 0' }}>Create Workspace</h3>
        <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
          <Input placeholder="Team name" value={name} onChange={e => setName(e.target.value)} />
          <Button onClick={handleCreate} loading={creating}>Create</Button>
        </div>
        {result && !result.error && (
          <div style={{
            padding: 16, background: 'var(--color-bg-tertiary)',
            borderRadius: 'var(--radius-md)', fontSize: 14,
          }}>
            <div>Workspace ID: <code>{result.workspace_id}</code></div>
            <div style={{ marginTop: 8 }}>
              API Key: <code style={{ color: 'var(--color-accent)' }}>{result.api_key}</code>
            </div>
            <div style={{ fontSize: 12, color: 'var(--color-warning)', marginTop: 8 }}>
              Save this API key — it won't be shown again.
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};
