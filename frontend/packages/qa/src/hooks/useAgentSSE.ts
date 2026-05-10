import { useRef, useCallback } from 'react';

type Handler = (data: any) => void;
type EventMap = Record<string, Handler>;

export function useAgentSSE() {
  const esRef = useRef<EventSource | null>(null);

  const connect = useCallback((url: string, handlers: EventMap) => {
    if (esRef.current) { esRef.current.close(); }
    const es = new EventSource(url);
    esRef.current = es;

    for (const [event, handler] of Object.entries(handlers)) {
      es.addEventListener(event, (e: MessageEvent) => {
        try { handler(JSON.parse(e.data)); } catch { handler(e.data); }
      });
    }

    es.onerror = () => {
      if (es.readyState === EventSource.CLOSED) es.close();
    };

    return () => es.close();
  }, []);

  return { connect };
}
