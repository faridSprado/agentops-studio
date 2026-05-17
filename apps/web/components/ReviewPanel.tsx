'use client';

import { FormEvent, useState } from 'react';
import type { Campaign } from '@/lib/types';
import { approveCampaign, rerunCampaign, sendFeedback } from '@/lib/api';
import { cx } from '@/lib/utils';

type Props = {
  campaign: Campaign;
  busy: boolean;
  onUpdate: (campaign: Campaign) => void;
  onBusy: (busy: boolean) => void;
  onToast: (message: string, kind?: 'success' | 'error' | 'info') => void;
};

export function ReviewPanel({ campaign, busy, onUpdate, onBusy, onToast }: Props) {
  const [feedback, setFeedback] = useState(campaign.feedback || '');
  const show =
    campaign.human_review ||
    campaign.status === 'needs_review' ||
    (campaign.status === 'completed' && campaign.score !== null && campaign.score < 84);

  if (!show) return null;

  async function submitFeedback(event: FormEvent) {
    event.preventDefault();
    if (feedback.trim().length < 3) return;
    onBusy(true);
    try {
      const next = await sendFeedback(campaign.id, feedback.trim());
      onUpdate(next);
      onToast('Comentarios enviados.', 'info');
    } catch (err) {
      onToast(err instanceof Error ? err.message : 'Error', 'error');
    } finally {
      onBusy(false);
    }
  }

  async function approve() {
    onBusy(true);
    try {
      onUpdate(await approveCampaign(campaign.id));
      onToast('Campaña aprobada.', 'success');
    } catch (err) {
      onToast(err instanceof Error ? err.message : 'Error', 'error');
    } finally {
      onBusy(false);
    }
  }

  async function rerun() {
    onBusy(true);
    try {
      onUpdate(await rerunCampaign(campaign.id));
      onToast('Reejecutando flujo.', 'info');
    } catch (err) {
      onToast(err instanceof Error ? err.message : 'Error', 'error');
    } finally {
      onBusy(false);
    }
  }

  return (
    <section className="panel overflow-hidden border-gold/20">
      <div className="panel-head bg-gold-muted/30">
        <div>
          <p className="label-caps text-gold">Revisión humana</p>
          <h3 className="mt-0.5 font-display text-lg text-cream">
            {campaign.status === 'needs_review' ? 'Aprobación pendiente' : 'Control de calidad'}
          </h3>
        </div>
        <span className={cx('badge', campaign.status === 'needs_review' ? 'badge-warn' : 'badge-neutral')}>
          {campaign.status}
        </span>
      </div>
      <form onSubmit={submitFeedback} className="panel-body space-y-4">
        <label className="grid gap-2 text-sm text-cream-muted">
          Comentarios para ajustar la campaña
          <textarea
            value={feedback}
            onChange={e => setFeedback(e.target.value)}
            placeholder="Refuerza el llamado a la acción, ajusta el tono o corrige promesas exageradas…"
            className="input-field min-h-24"
            disabled={busy}
          />
        </label>
        <div className="flex flex-wrap gap-2">
          <button type="submit" disabled={busy || feedback.trim().length < 3} className="btn-primary text-sm">
            Enviar y reorquestar
          </button>
          <button type="button" disabled={busy} onClick={approve} className="btn-secondary text-sm">
            Aprobar
          </button>
          <button type="button" disabled={busy} onClick={rerun} className="btn-ghost text-sm">
            Reejecutar
          </button>
        </div>
      </form>
    </section>
  );
}
