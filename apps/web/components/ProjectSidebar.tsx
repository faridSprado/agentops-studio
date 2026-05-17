'use client';

import Link from 'next/link';
import { FormEvent, useEffect, useMemo, useState } from 'react';
import { campaignSharePath, deleteCampaign, renameCampaign } from '@/lib/api';
import {
  clearRecentCampaigns,
  deleteRecentCampaign,
  loadRecentCampaigns,
  renameRecentCampaign,
  togglePinnedRecentCampaign,
  type RecentCampaign
} from '@/lib/storage';
import type { Campaign } from '@/lib/types';
import { cx, statusLabel } from '@/lib/utils';

type Props = {
  activeCampaignId?: string;
  onSelectCampaign: (id: string) => void;
  onActiveDeleted?: () => void;
  onCampaignUpdated?: (campaign: Campaign) => void;
};

export function ProjectSidebar({ activeCampaignId, onSelectCampaign, onActiveDeleted, onCampaignUpdated }: Props) {
  const [recent, setRecent] = useState<RecentCampaign[]>([]);
  const [query, setQuery] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draftTitle, setDraftTitle] = useState('');
  const [busyId, setBusyId] = useState<string | null>(null);

  useEffect(() => {
    refresh();
    const update = () => setRecent(loadRecentCampaigns());
    window.addEventListener('agentops:recent-updated', update);
    return () => window.removeEventListener('agentops:recent-updated', update);
  }, [activeCampaignId]);

  const filtered = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) return recent;
    return recent.filter(item => `${item.title} ${item.projectName} ${item.status}`.toLowerCase().includes(value));
  }, [query, recent]);

  function refresh() {
    setRecent(loadRecentCampaigns());
  }

  function startRename(item: RecentCampaign) {
    setEditingId(item.id);
    setDraftTitle(item.title || item.projectName || 'Campaña');
  }

  async function submitRename(event: FormEvent, id: string) {
    event.preventDefault();
    const nextTitle = draftTitle.replace(/\s+/g, ' ').trim();
    if (!nextTitle) return;
    setBusyId(id);
    setRecent(renameRecentCampaign(id, nextTitle));
    try {
      const updated = await renameCampaign(id, nextTitle);
      onCampaignUpdated?.(updated);
    } catch {
      // El historial local ya queda actualizado aunque la API no esté disponible.
    } finally {
      setBusyId(null);
      setEditingId(null);
    }
  }

  async function remove(id: string) {
    const ok = window.confirm('¿Eliminar esta campaña del historial y de la base local?');
    if (!ok) return;
    setBusyId(id);
    setRecent(deleteRecentCampaign(id));
    try {
      await deleteCampaign(id);
    } catch {
      // Si la API ya no tiene la campaña, igual se elimina del historial local.
    } finally {
      setBusyId(null);
      if (activeCampaignId === id) onActiveDeleted?.();
    }
  }

  function pin(id: string) {
    setRecent(togglePinnedRecentCampaign(id));
  }

  function clearAll() {
    if (!recent.length) return;
    const ok = window.confirm('¿Vaciar el historial local? Las campañas guardadas en la API no se eliminan.');
    if (!ok) return;
    clearRecentCampaigns();
    setRecent([]);
  }

  return (
    <aside className="panel overflow-hidden">
      <div className="panel-head items-start">
        <div>
          <p className="label-caps">Historial</p>
          <h2 className="mt-1 text-xl font-bold text-cream">Campañas recientes</h2>
          <p className="mt-1 text-sm text-cream-dim">Abre, renombra, fija o elimina campañas guardadas.</p>
        </div>
        <span className="status-pill status-muted">{recent.length}</span>
      </div>

      <div className="panel-body space-y-5">
        <div className="grid gap-2">
          <input
            value={query}
            onChange={event => setQuery(event.target.value)}
            className="input-field py-2.5 text-sm"
            placeholder="Buscar por nombre, marca o estado"
            aria-label="Buscar campañas recientes"
          />
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={refresh} className="btn-secondary text-xs">Actualizar</button>
            <button type="button" onClick={clearAll} className="btn-ghost text-xs">Vaciar historial</button>
          </div>
        </div>

        <section className="max-h-[34rem] overflow-y-auto pr-1">
          {filtered.length === 0 ? (
            <p className="rounded-2xl border border-dashed border-line p-4 text-sm leading-7 text-cream-dim">
              {recent.length === 0 ? 'Cuando generes una campaña aparecerá aquí.' : 'No hay campañas con ese filtro.'}
            </p>
          ) : (
            <ul className="grid gap-3">
              {filtered.map(item => (
                <li key={item.id} className={cx('rounded-2xl border p-3 transition', activeCampaignId === item.id ? 'border-brand/50 bg-brand/10' : 'border-line bg-white/[.025] hover:border-line-soft hover:bg-white/[.045]')}>
                  {editingId === item.id ? (
                    <form onSubmit={event => submitRename(event, item.id)} className="grid gap-2">
                      <input
                        value={draftTitle}
                        onChange={event => setDraftTitle(event.target.value)}
                        className="input-field py-2 text-sm"
                        autoFocus
                        maxLength={120}
                      />
                      <div className="flex gap-2">
                        <button type="submit" disabled={busyId === item.id} className="btn-primary px-3 py-2 text-xs">Guardar</button>
                        <button type="button" onClick={() => setEditingId(null)} className="btn-secondary px-3 py-2 text-xs">Cancelar</button>
                      </div>
                    </form>
                  ) : (
                    <>
                      <button type="button" onClick={() => onSelectCampaign(item.id)} className="w-full text-left">
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-bold text-cream">{item.pinned ? '★ ' : ''}{item.title || item.projectName}</p>
                            <p className="mt-1 text-xs text-cream-dim">{statusLabel(item.status)}{item.score !== null ? ` · Puntaje ${item.score}` : ''}</p>
                          </div>
                          <span className="rounded-lg border border-line bg-ink-soft px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-cream-dim">Abrir</span>
                        </div>
                      </button>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <button type="button" onClick={() => startRename(item)} className="btn-ghost px-2 py-1.5 text-xs">Renombrar</button>
                        <button type="button" onClick={() => pin(item.id)} className="btn-ghost px-2 py-1.5 text-xs">{item.pinned ? 'Quitar fijo' : 'Fijar'}</button>
                        <Link href={campaignSharePath(item.id)} className="btn-ghost px-2 py-1.5 text-xs">Enlace</Link>
                        <button type="button" onClick={() => remove(item.id)} disabled={busyId === item.id} className="btn-ghost px-2 py-1.5 text-xs text-red-200 hover:text-red-100">Eliminar</button>
                      </div>
                    </>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
        <Link href="/" className="btn-secondary w-full text-center">Nueva campaña</Link>
      </div>
    </aside>
  );
}
