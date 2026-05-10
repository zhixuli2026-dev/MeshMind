import React, { useState } from 'react';
import { Card } from '@meshmind/design-system/src/components/Card';
import { Input } from '@meshmind/design-system/src/components/Input';
import { Button } from '@meshmind/design-system/src/components/Button';
import { Badge } from '@meshmind/design-system/src/components/Badge';
import { search } from '@meshmind/api-client/src/index';

export const KnowledgePage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const wsId = localStorage.getItem('meshmind_workspace_id') || '';

  const handleSearch = async () => {
    if (!query.trim() || !wsId) return;
    const data = await search(wsId, query);
    setResults(data.results || []);
  };

  return (
    <div>
      <h1 style={{ fontSize: 28, fontWeight: 700, margin: '0 0 24px 0' }}>Knowledge</h1>
      <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
        <Input placeholder="Search knowledge..." value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
        />
        <Button onClick={handleSearch}>Search</Button>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {results.map((r: any) => (
          <Card key={r.node_id}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <strong>{r.title}</strong>
              <Badge variant={r.knowledge_type as any}>{r.knowledge_type}</Badge>
              <span style={{ fontSize: 12, color: 'var(--color-text-tertiary)', marginLeft: 'auto' }}>
                vitality: {(r.computed_vitality || r.vitality).toFixed(2)}
              </span>
            </div>
            <p style={{ fontSize: 14, color: 'var(--color-text-secondary)', margin: 0 }}>
              {r.summary}
            </p>
          </Card>
        ))}
      </div>
    </div>
  );
};
