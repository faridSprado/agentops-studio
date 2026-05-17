'use client';

import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import type { CampaignRequest } from '@/lib/types';
import { clearBriefDraft, loadBriefDraft, saveBriefDraft } from '@/lib/storage';
import { channelLabel, cx } from '@/lib/utils';

const channelOptions = ['instagram', 'tiktok', 'landing', 'email', 'youtube', 'linkedin'];

const emptyBrief: CampaignRequest = {
  project: { name: '', brand_voice: '', audience: '', constraints: '' },
  campaign: { brief: '', channels: ['instagram', 'landing', 'email'], language: 'es', tone: '', human_review: false }
};

const samples: Record<string, CampaignRequest> = {
  SaaS: {
    project: {
      name: 'NovaDesk',
      brand_voice: 'clara, útil, directa y sin sonar corporativa',
      audience: 'freelancers, diseñadores y equipos pequeños que gestionan varios proyectos a la vez',
      constraints: 'no prometer productividad milagrosa, evitar lenguaje exagerado y mantener promesas verificables'
    },
    campaign: {
      brief:
        'Quiero lanzar una herramienta visual para organizar proyectos creativos y tareas diarias. Necesito una campaña para Instagram, TikTok, landing page y email. La campaña debe transmitir claridad, menos caos mental y control del flujo de trabajo creativo.',
      channels: ['instagram', 'tiktok', 'landing', 'email'],
      language: 'es',
      tone: 'moderno, profesional y cercano',
      human_review: false
    }
  },
  Café: {
    project: {
      name: 'Noctra Coffee',
      brand_voice: 'sofisticada, relajada y visual',
      audience: 'diseñadores, programadores, artistas y amantes del café de especialidad',
      constraints: 'evitar clichés típicos de cafeterías hipster y no usar promesas absolutas'
    },
    campaign: {
      brief:
        'Quiero una campaña visual para posicionar una nueva marca de café premium enfocada en creatividad nocturna y sesiones de trabajo profundas. Necesito ideas para Instagram, reels, landing page, email y storytelling de marca.',
      channels: ['instagram', 'youtube', 'landing', 'email'],
      language: 'es',
      tone: 'premium, cinematográfico y emocional',
      human_review: false
    }
  },
  Moda: {
    project: {
      name: 'Kairo District',
      brand_voice: 'urbana, segura, visual y directa',
      audience: 'jóvenes interesados en streetwear, sneakers, diseño gráfico y cultura urbana',
      constraints: 'evitar parecer una copia de marcas famosas y no usar clichés vacíos de cultura urbana'
    },
    campaign: {
      brief:
        'Necesito una campaña para una colección streetwear inspirada en arquitectura brutalista, neón nocturno y cultura visual asiática. Quiero piezas para Instagram, TikTok, landing page y un video hero corto.',
      channels: ['instagram', 'tiktok', 'landing', 'youtube'],
      language: 'es',
      tone: 'urbano, editorial y contundente',
      human_review: false
    }
  }
};

type Props = {
  busy: boolean;
  onSubmit: (value: CampaignRequest, brandFile?: File | null) => void;
  onReset?: () => void;
};

export function BriefForm({ busy, onSubmit, onReset }: Props) {
  const [value, setValue] = useState(emptyBrief);
  const [brandFile, setBrandFile] = useState<File | null>(null);
  const [advanced, setAdvanced] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const saveTimer = useRef<number | undefined>(undefined);

  useEffect(() => {
    const draft = loadBriefDraft();
    if (draft) setValue(draft);
  }, []);

  useEffect(() => {
    window.clearTimeout(saveTimer.current);
    saveTimer.current = window.setTimeout(() => saveBriefDraft(value), 500);
    return () => window.clearTimeout(saveTimer.current);
  }, [value]);

  const briefChars = value.campaign.brief.length;
  const completed = useMemo(() => {
    const fields = [value.project.name, value.campaign.tone, value.project.audience, value.project.brand_voice, value.campaign.brief];
    return fields.filter(item => item.trim().length > 2).length;
  }, [value]);

  const disabled = busy || value.project.name.trim().length < 2 || value.campaign.brief.trim().length < 20 || value.campaign.channels.length === 0;

  function setProject(key: keyof CampaignRequest['project'], next: string) {
    setValue(prev => ({ ...prev, project: { ...prev.project, [key]: next } }));
  }

  function setCampaign<T extends keyof CampaignRequest['campaign']>(key: T, next: CampaignRequest['campaign'][T]) {
    setValue(prev => ({ ...prev, campaign: { ...prev.campaign, [key]: next } }));
  }

  function toggleChannel(channel: string) {
    const channels = value.campaign.channels.includes(channel)
      ? value.campaign.channels.filter(item => item !== channel)
      : [...value.campaign.channels, channel];
    setCampaign('channels', channels);
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    if (disabled) return;
    onSubmit(
      {
        project: {
          name: clean(value.project.name),
          brand_voice: clean(value.project.brand_voice),
          audience: clean(value.project.audience),
          constraints: clean(value.project.constraints)
        },
        campaign: {
          ...value.campaign,
          brief: clean(value.campaign.brief),
          tone: clean(value.campaign.tone) || 'profesional y claro',
          channels: value.campaign.channels.slice(0, 6)
        }
      },
      brandFile
    );
  }

  function loadSample(sample: CampaignRequest) {
    setValue(sample);
    clearBriefDraft();
  }

  function resetForm() {
    setValue(emptyBrief);
    setBrandFile(null);
    fileRef.current?.value && (fileRef.current.value = '');
    clearBriefDraft();
    onReset?.();
  }

  return (
    <form onSubmit={submit} className="panel overflow-hidden">
      <div className="panel-head items-start">
        <div>
          <p className="label-caps">Brief creativo</p>
          <h2 className="mt-1 font-display text-2xl text-cream">Cuéntale a los agentes qué quieres construir</h2>
          <p className="mt-2 text-sm text-cream-dim">Puedes escribir un brief propio o cargar un ejemplo. Guardamos el borrador en tu navegador.</p>
        </div>
        <span className="rounded-pill border border-line bg-white/[.03] px-3 py-1 text-xs text-cream-dim">{completed}/5 listo</span>
      </div>

      <div className="panel-body space-y-5">
        <div className="rounded-2xl border border-line bg-ink-soft/70 p-3">
          <div className="mb-2 flex items-center justify-between gap-3">
            <p className="text-sm font-semibold text-cream">Casos de prueba</p>
            <button type="button" onClick={resetForm} className="btn-ghost text-xs">Limpiar todo</button>
          </div>
          <div className="grid gap-2 sm:grid-cols-3">
            {Object.entries(samples).map(([label, sample]) => (
              <button key={label} type="button" onClick={() => loadSample(sample)} className="sample-card">
                <span>{label}</span>
                <small>cargar brief</small>
              </button>
            ))}
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Field label="Marca" hint="Nombre comercial o proyecto">
            <input className="input-field" value={value.project.name} onChange={event => setProject('name', event.target.value)} placeholder="Ej: Noctra Coffee" maxLength={120} />
          </Field>
          <Field label="Tono" hint="Cómo debe sonar la campaña">
            <input className="input-field" value={value.campaign.tone} onChange={event => setCampaign('tone', event.target.value)} placeholder="Ej: premium, cinematográfico y emocional" maxLength={160} />
          </Field>
        </div>

        <Field label="Audiencia" hint="Mientras más específica, mejor trabajan los agentes">
          <input className="input-field" value={value.project.audience} onChange={event => setProject('audience', event.target.value)} placeholder="Ej: diseñadores, programadores y artistas nocturnos" maxLength={220} />
        </Field>

        <Field label="Voz de marca" hint="Personalidad, estilo y palabras que sí usarías">
          <input className="input-field" value={value.project.brand_voice} onChange={event => setProject('brand_voice', event.target.value)} placeholder="Ej: sofisticada, relajada, visual y concreta" maxLength={220} />
        </Field>

        <Field label="Brief" hint="Objetivo, producto, canales, estilo, entregables y resultado esperado">
          <textarea className="input-field min-h-40 resize-y" value={value.campaign.brief} onChange={event => setCampaign('brief', event.target.value)} placeholder="Ej: Quiero una campaña para lanzar..." maxLength={1800} />
          <div className="mt-2 flex justify-between text-xs text-cream-dim">
            <span>{briefChars < 20 ? 'Mínimo recomendado: 20 caracteres' : 'Buen nivel de contexto'}</span>
            <span>{briefChars}/1800</span>
          </div>
        </Field>

        <div>
          <div className="mb-2 flex items-center justify-between gap-3">
            <p className="text-sm font-semibold text-cream">Canales</p>
            <p className="text-xs text-cream-dim">Elige al menos uno</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {channelOptions.map(channel => (
              <button key={channel} type="button" onClick={() => toggleChannel(channel)} className={cx('chip transition', value.campaign.channels.includes(channel) && 'chip-active')}>
                {channelLabel(channel)}
              </button>
            ))}
          </div>
        </div>

        <button type="button" onClick={() => setAdvanced(prev => !prev)} className="flex w-full items-center justify-between rounded-xl border border-line bg-white/[.02] px-4 py-3 text-left text-sm text-cream-muted transition hover:border-line-soft hover:text-cream">
          <span>Opciones avanzadas</span>
          <span>{advanced ? 'Ocultar' : 'Mostrar'}</span>
        </button>

        {advanced ? (
          <div className="grid gap-4 rounded-2xl border border-line bg-ink-soft/60 p-4 animate-fade-in">
            <Field label="Restricciones" hint="Riesgos legales, tono prohibido, promesas que no deben aparecer">
              <input className="input-field" value={value.project.constraints} onChange={event => setProject('constraints', event.target.value)} placeholder="Ej: no prometer resultados imposibles" maxLength={320} />
            </Field>
            <Field label="Brand kit opcional" hint="Solo .txt, .md o .csv. Útil para guías de tono o atributos de marca.">
              <input ref={fileRef} type="file" accept=".txt,.md,.csv" className="input-field cursor-pointer file:mr-3 file:rounded-lg file:border-0 file:bg-brand file:px-3 file:py-1 file:text-sm file:font-semibold file:text-ink" onChange={e => setBrandFile(e.target.files?.[0] || null)} />
              {brandFile ? <span className="mt-2 block text-xs text-cream-dim">Archivo cargado: {brandFile.name}</span> : null}
            </Field>
            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-line bg-white/[.02] px-4 py-3 text-sm text-cream-muted">
              <input type="checkbox" className="mt-1 h-4 w-4 accent-brand" checked={value.campaign.human_review} onChange={event => setCampaign('human_review', event.target.checked)} />
              <span>
                <strong className="text-cream">Pedir revisión humana antes de cerrar</strong>
                <span className="mt-0.5 block text-xs text-cream-dim">La campaña queda en revisión para aprobar o ajustar antes de exportar.</span>
              </span>
            </label>
          </div>
        ) : null}

        <button disabled={disabled} className="btn-primary w-full text-base" type="submit">
          {busy ? 'Generando campaña con agentes...' : 'Generar campaña completa'}
        </button>

        {disabled && !busy ? (
          <p className="text-center text-xs text-cream-dim">Completa marca, brief y al menos un canal para iniciar.</p>
        ) : null}
      </div>
    </form>
  );
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <label className="grid gap-2 text-sm text-cream-muted">
      <span className="flex flex-wrap items-baseline justify-between gap-2">
        <strong className="font-semibold text-cream">{label}</strong>
        {hint ? <small className="text-xs text-cream-dim">{hint}</small> : null}
      </span>
      {children}
    </label>
  );
}

function clean(value: string) {
  return value.replace(/\s+/g, ' ').trim();
}
