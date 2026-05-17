import type { CampaignRequest } from './types';

const RECENT_KEY = 'agentops:recent-campaigns';
const DRAFT_KEY = 'agentops:brief-draft';
const MAX_RECENT = 16;

export type RecentCampaign = {
  id: string;
  projectId?: string;
  projectName: string;
  title: string;
  status: string;
  score: number | null;
  updatedAt: string;
  pinned?: boolean;
  customTitle?: boolean;
};

function safeParse<T>(raw: string | null, fallback: T): T {
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeRecentCampaigns(list: RecentCampaign[]) {
  if (typeof window === 'undefined') return;
  const deduped = Array.from(new Map(list.map(item => [item.id, item])).values());
  const sorted = deduped.sort((a, b) => {
    if (a.pinned && !b.pinned) return -1;
    if (!a.pinned && b.pinned) return 1;
    return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
  });
  localStorage.setItem(RECENT_KEY, JSON.stringify(sorted.slice(0, MAX_RECENT)));
  window.dispatchEvent(new CustomEvent('agentops:recent-updated'));
}

export function loadRecentCampaigns(): RecentCampaign[] {
  if (typeof window === 'undefined') return [];
  return safeParse<RecentCampaign[]>(localStorage.getItem(RECENT_KEY), []).filter(item => Boolean(item.id));
}

export function saveRecentCampaign(entry: RecentCampaign) {
  const list = loadRecentCampaigns();
  const existing = list.find(item => item.id === entry.id);
  const next: RecentCampaign = {
    ...entry,
    title: existing?.customTitle ? existing.title : entry.title,
    pinned: existing?.pinned || false,
    customTitle: existing?.customTitle || false
  };
  writeRecentCampaigns([next, ...list.filter(item => item.id !== entry.id)]);
}

export function renameRecentCampaign(id: string, title: string): RecentCampaign[] {
  const cleanTitle = title.replace(/\s+/g, ' ').trim().slice(0, 120);
  if (!cleanTitle) return loadRecentCampaigns();
  const next = loadRecentCampaigns().map(item => (item.id === id ? { ...item, title: cleanTitle, customTitle: true, updatedAt: new Date().toISOString() } : item));
  writeRecentCampaigns(next);
  return next;
}

export function deleteRecentCampaign(id: string): RecentCampaign[] {
  const next = loadRecentCampaigns().filter(item => item.id !== id);
  writeRecentCampaigns(next);
  return next;
}

export function togglePinnedRecentCampaign(id: string): RecentCampaign[] {
  const next = loadRecentCampaigns().map(item => (item.id === id ? { ...item, pinned: !item.pinned } : item));
  writeRecentCampaigns(next);
  return next;
}

export function clearRecentCampaigns() {
  writeRecentCampaigns([]);
}

export function loadBriefDraft(): CampaignRequest | null {
  if (typeof window === 'undefined') return null;
  return safeParse<CampaignRequest | null>(localStorage.getItem(DRAFT_KEY), null);
}

export function saveBriefDraft(draft: CampaignRequest) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
}

export function clearBriefDraft() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(DRAFT_KEY);
}
