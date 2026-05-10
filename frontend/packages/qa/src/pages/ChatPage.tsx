import React, { useState, useCallback } from 'react';
import { ChatPanel } from '../components/ChatPanel';
import { AgentTree } from '../components/AgentTree';
import { ReactLoopTimeline } from '../components/ReactLoopTimeline';
import { SourcePanel } from '../components/SourcePanel';
import { useAgentSSE } from '../hooks/useAgentSSE';

interface AgentState {
  id: string;
  topic: string;
  status: 'thinking' | 'acting' | 'observing' | 'done';
}

interface Source {
  N: number;
  title: string;
  node_id: string;
}

const layoutStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '1fr 320px',
  gridTemplateRows: '1fr 240px',
  height: '100vh',
  gap: 0,
  background: 'var(--color-bg-primary)',
};

const chatStyle: React.CSSProperties = {
  gridRow: '1 / 3',
  borderRight: '1px solid var(--color-border-light)',
  display: 'flex', flexDirection: 'column',
};

const agentStyle: React.CSSProperties = {
  borderBottom: '1px solid var(--color-border-light)',
  overflow: 'auto',
  padding: '20px',
};

const sourceStyle: React.CSSProperties = {
  overflow: 'auto',
  padding: '20px',
};

export const ChatPage: React.FC = () => {
  const [workspaceId, setWorkspaceId] = useState('');
  const [messages, setMessages] = useState<Array<{ role: string; content: string; sources?: Source[] }>>([]);
  const [agents, setAgents] = useState<AgentState[]>([]);
  const [loopSteps, setLoopSteps] = useState<Array<{ agent_id: string; step: string; detail: string }>>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [connected, setConnected] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [answer, setAnswer] = useState('');

  const { connect } = useAgentSSE();

  const handleSend = useCallback((question: string) => {
    if (!workspaceId) return;
    setMessages(prev => [...prev, { role: 'user', content: question }]);
    setThinking(true);
    setAnswer('');
    setAgents([]);
    setLoopSteps([]);
    setSources([]);

    const convId = crypto.randomUUID();
    connect(`/api/v1/workspaces/${workspaceId}/sse/agent/${convId}?q=${encodeURIComponent(question)}`, {
      agent_start: (d) => { setConnected(true); },
      main_agent_spawn: (d) => {
        setAgents(prev => [...prev, { id: d.agent_id, topic: d.topic, status: 'thinking' }]);
      },
      think: (d) => {
        setLoopSteps(prev => [...prev, { agent_id: d.agent_id, step: 'Think', detail: d.thought }]);
        setAgents(prev => prev.map(a => a.id === d.agent_id ? { ...a, status: 'thinking' as const } : a));
      },
      act: (d) => {
        setLoopSteps(prev => [...prev, { agent_id: d.agent_id, step: 'Act', detail: d.action }]);
        setAgents(prev => prev.map(a => a.id === d.agent_id ? { ...a, status: 'acting' as const } : a));
      },
      observe: (d) => {
        setLoopSteps(prev => [...prev, { agent_id: d.agent_id, step: 'Observe', detail: `${d.found_nodes} nodes found` }]);
        setAgents(prev => prev.map(a => a.id === d.agent_id ? { ...a, status: 'observing' as const } : a));
      },
      source_linked: (d) => {
        setSources(prev => [...prev, { N: prev.length + 1, title: d.title, node_id: d.node_id }]);
      },
      answer_chunk: (d) => {
        setAnswer(prev => prev + d.text);
      },
      answer_complete: (d) => {
        setAnswer(d.full_text);
        setSources(d.sources || []);
        setThinking(false);
        setMessages(prev => [...prev, { role: 'agent', content: d.full_text, sources: d.sources }]);
        setAgents(prev => prev.map(a => ({ ...a, status: 'done' as const })));
      },
      error: (d) => {
        setThinking(false);
        setMessages(prev => [...prev, { role: 'agent', content: `Error: ${d.message}` }]);
      },
    });
  }, [workspaceId, connect]);

  return (
    <div style={layoutStyle}>
      <div style={chatStyle}>
        <ChatPanel
          messages={messages}
          thinking={thinking}
          answer={answer}
          workspaceId={workspaceId}
          onWorkspaceChange={setWorkspaceId}
          onSend={handleSend}
        />
      </div>
      <div style={agentStyle}>
        <AgentTree agents={agents} />
        <ReactLoopTimeline steps={loopSteps} />
      </div>
      <div style={sourceStyle}>
        <SourcePanel sources={sources} />
      </div>
    </div>
  );
};
