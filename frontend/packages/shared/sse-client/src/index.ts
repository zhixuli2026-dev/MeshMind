export type SSEEventHandler = (data: any) => void;

const events = [
  'agent_start', 'main_agent_spawn', 'think', 'act', 'observe',
  'knowledge_loaded', 'source_linked', 'agent_complete',
  'answer_chunk', 'answer_complete', 'error',
] as const;

export function connectAgentSSE(
  workspaceId: string,
  conversationId: string,
  question: string,
  handlers: Partial<Record<typeof events[number], SSEEventHandler>>,
): EventSource {
  const params = new URLSearchParams({ q: question });
  const url = `/api/v1/workspaces/${workspaceId}/sse/agent/${conversationId}?${params}`;
  const es = new EventSource(url);

  for (const evt of events) {
    if (handlers[evt]) {
      es.addEventListener(evt, (e: MessageEvent) => {
        handlers[evt]!(JSON.parse(e.data));
      });
    }
  }

  es.onerror = () => { if (es.readyState === EventSource.CLOSED) es.close(); };
  return es;
}
