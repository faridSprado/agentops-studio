'use client';

import { useMemo, useState } from 'react';
import type { AgentEvent } from '@/lib/types';
import { cx } from '@/lib/utils';

const order = ['system', 'normalizer', 'research', 'strategy', 'copy', 'storyboard', 'visual', 'execution_plan', 'kpis', 'brand_review', 'evaluator', 'assembler'];

const agentText: Record<string, { label: string; help: string }> = {
  system: { label: 'Sistema', help: 'prepara el trabajo' },
  normalizer: { label: 'Brief limpio', help: 'ordena el contexto' },
  research: { label: 'Investigación', help: 'detecta insights' },
  strategy: { label: 'Estrategia', help: 'define la ruta' },
  copy: { label: 'Copy', help: 'escribe piezas' },
  storyboard: { label: 'Storyboard', help: 'crea escenas' },
  visual: { label: 'Visual', help: 'define dirección de arte' },
  execution_plan: { label: 'Plan', help: 'organiza semanas' },
  kpis: { label: 'KPIs', help: 'mide impacto' },
  brand_review: { label: 'Revisión', help: 'revisa riesgos' },
  evaluator: { label: 'Evaluación', help: 'califica calidad' },
  assembler: { label: 'Entrega final', help: 'arma la campaña' }
};

export function AgentTimeline({ events, running }: { events: AgentEvent[]; running?: boolean }) {
  const [expanded, setExpanded] = useState(false);
  const compact = useMemo(() => compactEvents(events), [events]);
  const completed = compact.filter(event => event.status === 'completed').length;
  const total = order.length;
  const progress = Math.min(100, Math.round((completed / total) * 100));
  const active = compact.find(event => event.status === 'running');
  const visible = expanded ? compact : compact.filter(event => event.status === 'running' || event.status === 'failed').concat(compact.filter(event => event.status === 'completed').slice(-4));

  return (
    <section className="panel overflow-hidden">
      <div className="panel-head">
        <div>
          <p className="label-caps">Orquestación</p>
          <h2 className="mt-1 font-display text-xl text-cream">Flujo de agentes</h2>
          <p className="mt-1 text-xs text-cream-dim">
            {completed}/{total} pasos completados{active ? ` · ahora: ${agentText[active.agent]?.label || active.agent}` : running ? ' · iniciando' : ''}
          </p>
        </div>
        <button type="button" onClick={() => setExpanded(prev => !prev)} className="btn-secondary text-xs">
          {expanded ? 'Compactar' : 'Ver todo'}
        </button>
      </div>

      <div className="panel-body space-y-4">
        <div className="rounded-2xl border border-line bg-ink-soft/70 p-4">
          <div className="mb-2 flex items-center justify-between text-xs text-cream-dim">
            <span>Progreso de generación</span>
            <strong className="text-cream">{progress}%</strong>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-black/30">
            <div className={cx('h-full rounded-full bg-gradient-to-r from-brand-dark via-brand to-sage transition-all duration-700', running && 'animate-pulse-slow')} style={{ width: `${progress}%` }} />
          </div>
          <div className="mt-3 grid grid-cols-6 gap-1">
            {order.map(agent => {
              const event = compact.find(item => item.agent === agent);
              return <span key={agent} title={agentText[agent]?.label || agent} className={cx('h-1.5 rounded-full', event?.status === 'completed' && 'bg-sage', event?.status === 'running' && 'bg-brand shadow-glow', event?.status === 'failed' && 'bg-red-400', !event && 'bg-line')} />;
            })}
          </div>
        </div>

        <div className={cx('grid gap-2', expanded && 'max-h-[32rem] overflow-y-auto pr-1')}>
          {compact.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-line p-5 text-center text-sm text-cream-dim">
              Al generar una campaña verás cada agente trabajando en tiempo real.
            </div>
          ) : null}
          {visible.map(event => {
            const meta = agentText[event.agent] || { label: event.agent, help: '' };
            return (
              <article key={`${event.agent}-${event.status}`} className={cx('rounded-xl border border-line bg-white/[.025] p-3 transition', event.status === 'running' && 'border-brand/40 bg-brand/5', event.status === 'failed' && 'border-red-500/40 bg-red-500/5')}>
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-cream">{meta.label}</p>
                    <p className="mt-0.5 text-xs text-cream-dim">{meta.help}</p>
                  </div>
                  <Status status={event.status} />
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function Status({ status }: { status: string }) {
  const labels: Record<string, string> = { queued: 'en cola', running: 'trabajando', completed: 'listo', failed: 'falló', needs_review: 'revisión' };
  return <span className={cx('rounded-pill px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide', status === 'completed' && 'bg-sage-muted text-sage-light', status === 'running' && 'bg-brand/15 text-brand-light', status === 'failed' && 'bg-red-500/15 text-red-300', status === 'queued' && 'bg-white/5 text-cream-dim')}>{labels[status] || status}</span>;
}

function compactEvents(events: AgentEvent[]) {
  const map = new Map<string, AgentEvent>();
  for (const event of events) map.set(event.agent, event);
  return Array.from(map.values()).sort((a, b) => orderIndex(a.agent) - orderIndex(b.agent));
}

function orderIndex(agent: string) {
  const index = order.indexOf(agent);
  return index === -1 ? 99 : index;
}
