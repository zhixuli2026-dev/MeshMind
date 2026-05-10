import { useRef, useCallback } from 'react';

type Handler = (data: any) => void;
type EventMap = Record<string, Handler>;

export function useAgentSSE() {
  const esRef = useRef<EventSource | null>(null);

  const connect = useCallback((url: string, handlers: EventMap) => {
    if (esRef.current) { esRef.current.close(); }

    console.log('[SSE] Connecting to:', url);
    const es = new EventSource(url);
    esRef.current = es;

    es.onopen = () => {
      console.log('[SSE] Connected');
      if (handlers.agent_start) handlers.agent_start({});
    };

    for (const [event, handler] of Object.entries(handlers)) {
      es.addEventListener(event, (e: Event) => {
        const me = e as MessageEvent;
        try {
          const data = JSON.parse(me.data);
          handler(data);
        } catch {
          handler(me.data || {});
        }
      });
    }

    es.onerror = (e) => {
      console.log('[SSE] Connection error, readyState:', es.readyState);
      if (es.readyState === EventSource.CLOSED) {
        console.log('[SSE] Connection closed');
        if (handlers.error) {
          handlers.error({ message: 'Connection to server failed. Is the backend running?' });
        }
      }
    };

    return () => es.close();
  }, []);

  return { connect };
}
