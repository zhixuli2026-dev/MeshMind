import React, { useState, useRef, useEffect } from 'react';
import { Input } from '@meshmind/design-system/src/components/Input';
import { Button } from '@meshmind/design-system/src/components/Button';

interface Source { N: number; title: string; node_id: string; }
interface Message { role: string; content: string; sources?: Source[]; }

export const ChatPanel: React.FC<{
  messages: Message[];
  thinking: boolean;
  answer: string;
  workspaceId: string;
  onWorkspaceChange: (v: string) => void;
  onSend: (q: string) => void;
}> = ({ messages, thinking, answer, workspaceId, onWorkspaceChange, onSend }) => {
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, answer]);

  const handleSubmit = () => {
    if (!input.trim()) return;
    onSend(input.trim());
    setInput('');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '20px', borderBottom: '1px solid var(--color-border-light)' }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, margin: 0, color: 'var(--color-text-primary)' }}>
          MeshMind Q&A
        </h1>
        <div style={{ marginTop: 12 }}>
          <Input
            placeholder="Workspace ID"
            value={workspaceId}
            onChange={e => onWorkspaceChange(e.target.value)}
            style={{ fontSize: 13 }}
          />
        </div>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: '20px' }}>
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 24 }}>
            <div style={{
              fontSize: 12, fontWeight: 600, color: 'var(--color-text-tertiary)',
              marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.05em',
            }}>
              {m.role === 'user' ? 'You' : 'MeshMind'}
            </div>
            <div style={{
              fontSize: 15, lineHeight: 1.6, color: 'var(--color-text-primary)',
              background: m.role === 'user' ? 'var(--color-bg-primary)' : 'transparent',
              padding: m.role === 'user' ? '12px 16px' : 0,
              borderRadius: 'var(--radius-md)',
              whiteSpace: 'pre-wrap',
            }}>
              {m.content}
            </div>
            {m.sources && m.sources.length > 0 && (
              <div style={{ marginTop: 8, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {m.sources.map(s => (
                  <span key={s.N} style={{
                    fontSize: 12, color: 'var(--color-accent)',
                    background: 'var(--color-accent)14', padding: '2px 8px',
                    borderRadius: 4, cursor: 'pointer',
                  }}>[{s.N}] {s.title}</span>
                ))}
              </div>
            )}
          </div>
        ))}
        {thinking && (
          <div style={{ fontSize: 15, color: 'var(--color-text-tertiary)' }}>
            {answer ? (
              <span style={{ whiteSpace: 'pre-wrap', color: 'var(--color-text-primary)' }}>{answer}</span>
            ) : 'Thinking...'}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--color-border-light)', display: 'flex', gap: 12 }}>
        <Input
          placeholder="Ask a question..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSubmit()}
        />
        <Button onClick={handleSubmit} disabled={thinking}>Send</Button>
      </div>
    </div>
  );
};
