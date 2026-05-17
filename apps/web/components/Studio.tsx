'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { AgentTimeline } from '@/components/AgentTimeline';
import { BriefForm } from '@/components/BriefForm';
import { CampaignView } from '@/components/CampaignView';
import { Header } from '@/components/Header';
import { ProjectSidebar } from '@/components/ProjectSidebar';
import { ReviewPanel } from '@/components/ReviewPanel';
import { CampaignSkeleton } from '@/components/ui/Skeleton';
import { useCampaignSocket } from '@/hooks/useCampaignSocket';
import { useToast } from '@/hooks/useToast';
import { createCampaign, createProject, getCampaign, getHealth } from '@/lib/api';
import { saveRecentCampaign } from '@/lib/storage';
import type { Campaign, CampaignRequest, Health } from '@/lib/types';
import { statusLabel } from '@/lib/utils';

const terminal = new Set(['completed', 'failed', 'needs_review']);

type StudioProps = { initialCampaignId?: string };

export function Studio({ initialCampaignId }: StudioProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { push: toast } = useToast();
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [healthError, setHealthError] = useState(false);
  const [busy, setBusy] = useState(false);
  const [actionBusy, setActionBusy] = useState(false);
  const [error, setError] = useState('');
  const [loadingCampaign, setLoadingCampaign] = useState(Boolean(initialCampaignId));

  const campaignId = campaign?.id;
  const status = campaign?.status || 'idle';
  const running = useMemo(() => Boolean(campaign && !terminal.has(campaign.status)), [campaign]);
  const { events, setEvents, connected } = useCampaignSocket(campaignId, campaign?.status);

  const syncUrl = useCallback((id: string | null) => {
    const params = new URLSearchParams(searchParams.toString());
    if (id) params.set('campaign', id);
    else params.delete('campaign');
    const query = params.toString();
    router.replace(query ? `/?${query}` : '/', { scroll: false });
  }, [router, searchParams]);

  const loadCampaign = useCallback(async (id: string) => {
    setLoadingCampaign(true);
    setError('');
    try {
      const next = await getCampaign(id);
      setCampaign(next);
      syncUrl(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo cargar la campaña');
      toast('No encontramos esa campaña o la API no está disponible.', 'error');
    } finally {
      setLoadingCampaign(false);
    }
  }, [syncUrl, toast]);

  async function generate(payload: CampaignRequest, brandFile?: File | null) {
    setBusy(true);
    setError('');
    setEvents([]);
    setCampaign(null);
    try {
      const project = await createProject(payload.project);
      if (brandFile) {
        try {
          const { uploadBrandAsset } = await import('@/lib/api');
          await uploadBrandAsset(project.id, 'brand-kit', brandFile);
          toast('Brand kit cargado correctamente.', 'success');
        } catch {
          toast('La campaña seguirá, pero el brand kit no pudo cargarse.', 'error');
        }
      }
      const next = await createCampaign(project.id, payload.campaign);
      setCampaign(next);
      syncUrl(next.id);
      toast('Los agentes empezaron a trabajar.', 'info');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Ocurrió un error inesperado';
      setError(message);
      toast(message, 'error');
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    getHealth().then(data => {
      setHealth(data);
      setHealthError(false);
    }).catch(() => {
      setHealth(null);
      setHealthError(true);
    });
  }, []);

  useEffect(() => {
    const fromUrl = initialCampaignId || searchParams.get('campaign');
    if (fromUrl && fromUrl !== campaign?.id) loadCampaign(fromUrl);
  }, [initialCampaignId, searchParams, campaign?.id, loadCampaign]);

  useEffect(() => {
    if (!campaignId || terminal.has(campaign?.status || '')) return;
    const timer = window.setInterval(async () => {
      try {
        const next = await getCampaign(campaignId);
        setCampaign(next);
        if (terminal.has(next.status)) {
          toast(next.status === 'completed' ? 'Campaña completada.' : next.status === 'needs_review' ? 'Lista para revisión humana.' : 'La campaña falló.', next.status === 'failed' ? 'error' : 'success');
        }
      } catch {
        // Polling retry.
      }
    }, 1200);
    return () => window.clearInterval(timer);
  }, [campaignId, campaign?.status, toast]);

  useEffect(() => {
    if (!campaign) return;
    saveRecentCampaign({
      id: campaign.id,
      projectId: campaign.project_id,
      projectName: campaign.output?.title || campaign.brief.slice(0, 40) || 'Campaña',
      title: campaign.output?.title || campaign.brief.slice(0, 48),
      status: campaign.status,
      score: campaign.score,
      updatedAt: campaign.updated_at
    });
  }, [campaign]);

  return (
    <main className="app-shell">
      <Header health={health} healthError={healthError} connected={connected && running} />
      <section className="relative z-10 mx-auto max-w-[118rem] px-4 py-7 sm:px-6 lg:px-8">
        <div className="mb-7 grid gap-5 rounded-3xl border border-line bg-surface/70 p-5 shadow-panel lg:grid-cols-[1.2fr_.8fr] lg:p-7">
          <div>
            <p className="label-caps">Producto con IA</p>
            <h2 className="mt-2 font-display text-4xl leading-tight text-cream lg:text-5xl">De brief a campaña multimedia lista para presentar</h2>
            <p className="mt-4 max-w-3xl text-base leading-8 text-cream-muted">Convierte una idea de marca en una campaña completa: investigación, estrategia, copy, storyboard, dirección visual, plan de ejecución, KPIs y evaluación de calidad.</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
            <HeroMetric value="9" label="agentes especializados" />
            <HeroMetric value="4" label="formatos exportables" />
            <HeroMetric value={health?.llm_enabled ? 'IA' : 'Demo'} label="modo de generación" />
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[minmax(22rem,25rem)_minmax(0,1fr)]">
          <aside className="space-y-6 xl:sticky xl:top-24 xl:self-start">
            <BriefForm busy={busy || running || actionBusy} onSubmit={generate} onReset={() => { setCampaign(null); setEvents([]); setError(''); syncUrl(null); }} />
            <AgentTimeline events={events} running={running} />
            <ProjectSidebar activeCampaignId={campaignId} onSelectCampaign={loadCampaign} onCampaignUpdated={setCampaign} onActiveDeleted={() => { setCampaign(null); setEvents([]); syncUrl(null); }} />
          </aside>

          <section className="min-w-0 space-y-5">
            {error ? <div className="panel border-red-500/30 bg-red-500/5 p-4 text-sm leading-7 text-red-100"><strong>Necesita atención:</strong> {error}</div> : null}
            <StatusStrip status={status} health={health} connected={connected} running={running} />
            {campaign ? <ReviewPanel campaign={campaign} busy={actionBusy || running} onUpdate={setCampaign} onBusy={setActionBusy} onToast={toast} /> : null}
            {loadingCampaign && !campaign ? <CampaignSkeleton /> : null}
            <CampaignView campaign={campaign} loading={loadingCampaign && !campaign} />
          </section>
        </div>
      </section>
    </main>
  );
}

function HeroMetric({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-2xl border border-line bg-ink-soft/80 p-4">
      <div className="font-display text-3xl text-brand-light">{value}</div>
      <p className="mt-1 text-sm text-cream-dim">{label}</p>
    </div>
  );
}

function StatusStrip({ status, health, connected, running }: { status: string; health: Health | null; connected: boolean; running: boolean }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-line bg-ink-soft/70 px-4 py-3 text-sm">
      <span className="text-cream-dim">Estado <strong className="ml-1 font-semibold text-cream">{statusLabel(status)}</strong></span>
      <div className="flex flex-wrap items-center gap-2">
        {running && connected ? <span className="status-pill status-live">Streaming</span> : null}
        {running && !connected ? <span className="status-pill status-warn">Reconectando</span> : null}
        {health ? <span className="status-pill status-muted">{health.llm_enabled ? 'IA activa' : 'IA desactivada'} · v{health.version || '1'}</span> : null}
      </div>
    </div>
  );
}
