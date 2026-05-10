import React, { useState } from 'react';
import { Card } from '@meshmind/design-system/src/components/Card';
import { Button } from '@meshmind/design-system/src/components/Button';

export const DocumentsPage: React.FC = () => {
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    setUploading(true);
    setTimeout(() => setUploading(false), 2000);
  };

  return (
    <div>
      <h1 style={{ fontSize: 28, fontWeight: 700, margin: '0 0 24px 0' }}>Documents</h1>
      <Card>
        <p style={{ fontSize: 14, color: 'var(--color-text-secondary)', marginBottom: 16 }}>
          Upload Markdown documents to extract knowledge. Max 30MB per file.
        </p>
        <Button onClick={handleUpload} loading={uploading}>Upload Document</Button>
      </Card>
    </div>
  );
};
