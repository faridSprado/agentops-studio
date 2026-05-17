'use client';

import { useEffect, useRef, useState } from 'react';
import type { AgentEvent } from '@/lib/types';
import { getEvents, wsUrl } from '@/lib/api';

const terminal = new Set(['completed', 'failed', 'needs_review']);

function dedupeEvents(prev: AgentEvent[], next: AgentEvent) {
  if (
    next.sequence &&
    prev.some(
      item =>
        item.sequence === next.sequence && item.status === next.status && item.agent === next.agent
    )
  ) {
    return prev;
  }
  const map = new Map<string, AgentEvent>();
  for (const event of prev) map.set(event.agent, event);
  map.set(next.agent, next);
  return Array.from(map.values());
}

export function useCampaignSocket(campaignId: string | undefined, status: string | undefined) {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const retries = useRef(0);

  useEffect(() => {
    if (!campaignId) {
      setEvents([]);
      setConnected(false);
      return;
    }
    if (status && terminal.has(status)) {
      getEvents(campaignId).then(setEvents).catch(() => undefined);
      setConnected(false);
      return;
    }

    let socket: WebSocket | null = null;
    let closed = false;
    let reconnectTimer: number | undefined;

    const connect = () => {
      socket = new WebSocket(wsUrl(campaignId));
      socket.onopen = () => {
        retries.current = 0;
        setConnected(true);
      };
      socket.onmessage = message => {
        try {
          const next = JSON.parse(message.data) as AgentEvent;
          setEvents(prev => dedupeEvents(prev, next));
        } catch {
          /* ignore malformed */
        }
      };
      socket.onclose = () => {
        setConnected(false);
        if (closed) return;
        const delay = Math.min(8000, 800 * 2 ** retries.current);
        retries.current += 1;
        reconnectTimer = window.setTimeout(connect, delay);
      };
      socket.onerror = () => socket?.close();
    };

    connect();
    getEvents(campaignId).then(setEvents).catch(() => undefined);

    return () => {
      closed = true;
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [campaignId, status]);

  return { events, setEvents, connected };
}
