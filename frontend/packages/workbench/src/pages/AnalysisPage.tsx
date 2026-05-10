import React from 'react';
import { Card } from '@meshmind/design-system/src/components/Card';

export const AnalysisPage: React.FC = () => (
  <div>
    <h1 style={{ fontSize: 28, fontWeight: 700, margin: '0 0 24px 0' }}>Analysis</h1>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
      <Card>
        <h3 style={{ fontSize: 16, fontWeight: 600, margin: '0 0 16px 0' }}>Knowledge Growth</h3>
        <p style={{ fontSize: 14, color: 'var(--color-text-tertiary)' }}>
          Chart will appear here — using TimescaleDB vitality_events data.
        </p>
      </Card>
      <Card>
        <h3 style={{ fontSize: 16, fontWeight: 600, margin: '0 0 16px 0' }}>Vitality Distribution</h3>
        <p style={{ fontSize: 14, color: 'var(--color-text-tertiary)' }}>
          Chart will appear here.
        </p>
      </Card>
    </div>
  </div>
);
