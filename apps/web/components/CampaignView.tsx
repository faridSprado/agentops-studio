'use client';

import { useMemo, useState } from 'react';
import type { AgentSection, Campaign, ExecutiveItem } from '@/lib/types';
import { exportUrl } from '@/lib/api';
import { CopyButton } from '@/components/ui/CopyButton';
import { CampaignSkeleton } from '@/components/ui/Skeleton';
import { channelLabel, cx, scoreLabel, sectionLabel, statusLabel } from '@/lib/utils';

const sectionOrder = ['research', 'strategy', 'copy', 'storyboard', 'visual', 'execution_plan', 'kpis', 'brand_review', 'evaluation'];
const tabs = [
  { id: 'overview', label: 'Vista ejecutiva' },
  { id: 'scores', label: 'Calidad' },
  { id: 'deliverables', label: 'Entregables' }
];

export function CampaignView({ campaign, loading }: { campaign: Campaign | null; loading?: boolean }) {
  const [raw, setRaw] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const sections = useMemo(() => {
    if (!campaign?.output?.sections) return [];
    return sectionOrder.filter(key => campaign.output?.sections[key]).map(key => [key, campaign.output!.sections[key]] as const);
  }, [campaign?.output]);

  if (loading) return <CampaignSkeleton />;

  if (!campaign) return <EmptyState />;

  const output = campaign.output;
  const running = !output && !campaign.error;

  if (running) {
    return (
      <section className="panel p-8">
        <CampaignSkeleton />
        <p className="mt-5 text-center text-sm text-cream-dim animate-pulse-slow">Preparando investigación, estrategia, copy y entregables...</p>
      </section>
    );
  }

  return (
    <section className="panel overflow-hidden animate-fade-in">
      <div className="panel-head flex-wrap items-start">
        <div className="min-w-0 flex-1">
          <p className="label-caps">{statusLabel(campaign.status)}</p>
          <h2 className="mt-2 font-display text-3xl leading-tight text-cream md:text-4xl">{output?.title || 'Campaña en ejecución'}</h2>
          {output ? <p className="mt-3 max-w-3xl text-base leading-7 text-cream-dim">{output.summary}</p> : null}
          {output ? (
            <div className="mt-4 flex flex-wrap gap-2 text-xs">
              {output.provider ? <span className="status-pill status-muted">IA: {output.provider}</span> : null}
              <span className={cx('status-pill', output.mock_mode ? 'status-warn' : 'status-success')}>{output.mock_mode ? 'Modo demo' : 'IA activa'}</span>
              {output.revisions ? <span className="status-pill status-muted">{output.revisions} revisión(es)</span> : null}
            </div>
          ) : null}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {campaign.score !== null ? <PuntajePill score={campaign.score} /> : null}
          {output ? <ExportButtons campaignId={campaign.id} title={output.title} /> : null}
        </div>
      </div>

      <div className="panel-body">
        {campaign.error ? <ErrorBox message={campaign.error} /> : null}
        {output ? (
          <>
            <div className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-line bg-ink-soft/60 p-4">
              <div>
                <p className="text-sm font-semibold text-cream">Canales seleccionados</p>
                <p className="mt-1 text-xs text-cream-dim">La campaña adapta mensajes y entregables a estos formatos.</p>
              </div>
              <div className="flex flex-wrap gap-2">
                {output.channels?.map(ch => <span key={ch} className="chip chip-active">{channelLabel(ch)}</span>)}
              </div>
            </div>

            <nav className="tabs mb-6" aria-label="Secciones de la campaña">
              {tabs.map(tab => (
                <button key={tab.id} type="button" onClick={() => setActiveTab(tab.id)} className={cx('tab', activeTab === tab.id && 'tab-active')}>
                  {tab.label}
                </button>
              ))}
            </nav>

            {activeTab === 'overview' ? <Overview output={output} /> : null}
            {activeTab === 'scores' ? <PuntajeBreakdown values={output.score_breakdown || { overall: output.score }} rationale={output.score_rationale || {}} /> : null}
            {activeTab === 'deliverables' ? <Deliverables sections={sections} raw={raw} setRaw={setRaw} /> : null}
          </>
        ) : null}
      </div>
    </section>
  );
}

function EmptyState() {
  return (
    <section className="panel relative min-h-[460px] overflow-hidden p-10">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-brand/60 to-transparent" />
      <div className="mx-auto flex max-w-3xl flex-col items-center text-center">
        <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-3xl border border-brand/30 bg-brand/10 text-3xl shadow-glow">✦</div>
        <p className="label-caps">Listo para trabajar</p>
        <h2 className="mt-3 font-display text-4xl leading-tight text-cream">Convierte un brief en una campaña completa</h2>
        <p className="mt-4 text-base leading-8 text-cream-dim">Escribe el contexto de marca y el sistema ejecutará agentes especializados para entregar investigación, estrategia, copy, storyboard, dirección visual, plan de ejecución, KPIs y revisión de marca.</p>
        <div className="mt-8 grid gap-3 text-left sm:grid-cols-3">
          {['Resumen ejecutivo', 'Timeline de agentes', 'Exportaciones listas'].map(item => (
            <div key={item} className="rounded-2xl border border-line bg-white/[.03] p-4 text-sm text-cream-muted">{item}</div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Overview({ output }: { output: NonNullable<Campaign['output']> }) {
  const items = output.executive || [];
  const hero = items.slice(0, 3);
  const rest = items.slice(3);
  return (
    <div className="grid gap-6 animate-fade-in">
      <article className="rounded-3xl border border-line bg-gradient-to-br from-ink-soft to-surface p-6 md:p-7">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="label-caps">Resumen ejecutivo</p>
            <h3 className="mt-2 font-display text-2xl text-cream">Resumen de campaña</h3>
          </div>
          <CopyButton text={output.summary} label="Copiar resumen" />
        </div>
        <p className="mt-4 max-w-4xl text-lg leading-9 text-cream-muted">{output.summary}</p>
      </article>

      <div className="grid gap-4 xl:grid-cols-3">
        {hero.map(item => <ExecutiveCard key={item.label} item={item} featured />)}
      </div>
      {rest.length ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{rest.map(item => <ExecutiveCard key={item.label} item={item} />)}</div> : null}
    </div>
  );
}

function ExecutiveCard({ item, featured }: { item: ExecutiveItem; featured?: boolean }) {
  return (
    <article className={cx('group rounded-3xl border border-line bg-ink-soft/70 p-5 transition hover:-translate-y-0.5 hover:border-brand/35 hover:bg-surface', featured && 'min-h-[17rem]')}>
      <p className="label-caps">{item.label}</p>
      <h4 className="mt-3 text-xl font-bold text-cream">{item.title}</h4>
      <p className="mt-3 text-[15px] leading-7 text-cream-muted">{item.summary}</p>
      {item.items?.length ? (
        <ul className="mt-4 grid gap-2 text-sm leading-6 text-cream-dim">
          {item.items.slice(0, featured ? 5 : 4).map(point => <li key={point} className="flex gap-2"><span className="mt-1 text-brand-light">•</span><span>{point}</span></li>)}
        </ul>
      ) : null}
    </article>
  );
}

function Deliverables({ sections, raw, setRaw }: { sections: readonly (readonly [string, AgentSection])[]; raw: boolean; setRaw: (fn: (prev: boolean) => boolean) => void }) {
  return (
    <div className="grid gap-5 animate-fade-in">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-xl font-bold text-cream">Entregables por agente</h3>
          <p className="mt-1 text-sm text-cream-dim">Revisa el aporte de cada agente y copia las piezas que quieras usar.</p>
        </div>
        <button type="button" onClick={() => setRaw(prev => !prev)} className="btn-secondary">{raw ? 'Ocultar datos' : 'Ver datos'}</button>
      </div>
      {sections.map(([name, section]) => <Section key={name} name={name} section={section} raw={raw} />)}
    </div>
  );
}

function ExportButtons({ campaignId, title }: { campaignId: string; title: string }) {
  const formats = [
    { fmt: 'zip' as const, label: 'ZIP' },
    { fmt: 'pdf' as const, label: 'PDF' },
    { fmt: 'markdown' as const, label: 'MD' },
    { fmt: 'json' as const, label: 'JSON' }
  ];
  return <>{formats.map(({ fmt, label }) => <a key={fmt} className="btn-secondary text-xs" href={exportUrl(campaignId, fmt)} download title={`Exportar ${title}`}>{label}</a>)}</>;
}

function PuntajePill({ score }: { score: number }) {
  const tone = score >= 90 ? 'from-sage to-brand-light' : score >= 84 ? 'from-brand to-gold' : 'from-gold to-brand';
  return <span className={cx('rounded-2xl bg-gradient-to-br px-4 py-2 text-sm font-bold text-ink shadow-glow', tone)}>Puntaje {score}</span>;
}

function PuntajeBreakdown({ values, rationale }: { values: Record<string, number | string>; rationale: Record<string, string> }) {
  const entries = Object.entries(values).filter(([key]) => key !== 'recommendation');
  return (
    <article className="animate-fade-in rounded-3xl border border-line bg-ink-soft/75 p-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="label-caps">Control de calidad</p>
          <h3 className="mt-2 text-2xl font-bold text-cream">¿Qué tan lista está la campaña?</h3>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-cream-dim">Se revisan claridad, ajuste a marca, canales, profundidad creativa, ejecución y riesgo antes de recomendar producción.</p>
        </div>
        {values.recommendation ? <span className="status-pill status-muted">Recomendación: {String(values.recommendation)}</span> : null}
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {entries.map(([key, value]) => <Metric key={key} name={key} value={value} />)}
      </div>
      {Object.keys(rationale).length ? (
        <div className="mt-5 rounded-3xl border border-line bg-black/20 p-5">
          <h4 className="text-lg font-bold text-cream">Notas de evaluación</h4>
          <ul className="mt-3 grid gap-2 text-sm leading-7 text-cream-muted">
            {Object.entries(rationale).map(([key, value]) => <li key={key} className="flex gap-2"><span className="text-brand-light">•</span><span><strong className="text-cream">{scoreLabel(key)}:</strong> {value}</span></li>)}
          </ul>
        </div>
      ) : null}
    </article>
  );
}

function Metric({ name, value }: { name: string; value: number | string }) {
  const numeric = typeof value === 'number' ? value : Number(value);
  return (
    <div className="rounded-2xl border border-line bg-white/[.03] p-4">
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="text-cream-muted">{scoreLabel(name)}</span>
        <strong className="text-cream">{value}</strong>
      </div>
      {Number.isFinite(numeric) ? <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-gradient-to-r from-brand to-sage transition-all duration-700" style={{ width: `${Math.max(0, Math.min(100, numeric))}%` }} /></div> : null}
    </div>
  );
}

function Section({ name, section, raw }: { name: string; section: AgentSection; raw: boolean }) {
  const scenes = name === 'storyboard' ? extractScenes(section.data) : [];
  const palette = name === 'visual' ? extractPalette(section.data) : [];
  return (
    <article className="rounded-3xl border border-line bg-ink-soft/75 p-6 transition hover:border-white/15">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="label-caps">{sectionLabel(name)}</p>
          <h3 className="mt-2 text-2xl font-bold text-cream">{section?.title || sectionLabel(name)}</h3>
        </div>
        {section?.summary ? <CopyButton text={section.summary} /> : null}
      </div>
      {section?.summary ? <p className="mt-3 max-w-4xl text-base leading-8 text-cream-muted">{section.summary}</p> : null}
      {scenes.length > 0 ? <SceneGrid scenes={scenes} /> : null}
      {palette.length > 0 ? <Palette colors={palette} /> : null}
      {section?.items?.length ? (
        <ul className="mt-5 grid gap-3 text-sm leading-7 text-cream-muted md:grid-cols-2">
          {section.items.map(item => <li key={item} className="flex gap-3 rounded-xl border border-line/60 bg-white/[.02] p-3"><span className="text-brand-light">•</span><span>{item}</span></li>)}
        </ul>
      ) : null}
      {raw && section?.data ? <DataBlock value={section.data} /> : null}
    </article>
  );
}

function SceneGrid({ scenes }: { scenes: string[] }) {
  return <div className="mt-5 grid gap-3 md:grid-cols-2">{scenes.map((scene, i) => <div key={i} className="rounded-2xl border border-line bg-gradient-to-br from-surface to-ink-soft p-4"><span className="text-xs font-bold uppercase tracking-[.18em] text-brand-light">Escena {i + 1}</span><p className="mt-2 text-sm leading-7 text-cream-muted">{scene}</p></div>)}</div>;
}

function Palette({ colors }: { colors: string[] }) {
  return <div className="mt-5 flex flex-wrap gap-2">{colors.map(color => <span key={color} className="rounded-xl border border-line px-3 py-2 text-xs font-semibold text-cream" style={{ background: `linear-gradient(135deg, ${color}55, rgba(255,255,255,0.02))` }}>{color}</span>)}</div>;
}

function ErrorBox({ message }: { message: string }) {
  return <div className="mb-5 rounded-2xl border border-red-400/30 bg-red-500/10 p-4 text-sm leading-7 text-red-100"><strong>No se pudo completar:</strong> {message}</div>;
}

function extractScenes(data?: Record<string, unknown>): string[] {
  if (!data) return [];
  const candidates = [data.scenes, data.beats, data.shots, data.shot_list, data.hero_video, data.short_reels];
  const values: string[] = [];
  for (const candidate of candidates) collectStrings(candidate, values);
  return unique(values).slice(0, 8);
}

function extractPalette(data?: Record<string, unknown>): string[] {
  if (!data) return [];
  const colors = data.palette ?? data.colors ?? data.color_palette;
  if (Array.isArray(colors)) return colors.map(String).filter(item => item.startsWith('#') || item.length <= 24).slice(0, 8);
  return [];
}

function collectStrings(value: unknown, target: string[]) {
  if (!value) return;
  if (typeof value === 'string') {
    if (value.length > 4) target.push(value);
    return;
  }
  if (Array.isArray(value)) {
    value.forEach(item => collectStrings(item, target));
    return;
  }
  if (typeof value === 'object') {
    const object = value as Record<string, unknown>;
    const line = ['time', 'shot', 'action', 'screen_text', 'audio', 'transition'].map(key => object[key]).filter(Boolean).join(' · ');
    if (line) target.push(line);
    else Object.values(object).forEach(item => collectStrings(item, target));
  }
}

function unique(values: string[]) {
  return Array.from(new Set(values.map(item => item.trim()).filter(Boolean)));
}

function DataBlock({ value }: { value: Record<string, unknown> }) {
  return <pre className="mt-5 max-h-96 overflow-auto rounded-2xl border border-line bg-black/40 p-4 text-xs leading-relaxed text-cream-muted">{JSON.stringify(value, null, 2)}</pre>;
}
