import type { AgentEvent, Campaign, CampaignRequest, Health, Project } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function parseError(res: Response): Promise<string> {
  const text = await res.text();
  try {
    const json = JSON.parse(text) as { detail?: string | { msg?: string }[] };
    if (typeof json.detail === 'string') return json.detail;
    if (Array.isArray(json.detail)) return json.detail.map(d => d.msg || String(d)).join(', ');
  } catch {
    /* plain text */
  }
  if (res.status === 429) return 'El proveedor de IA alcanzó el límite temporal. Espera unos minutos o usa un modelo más pequeño.';
  if (res.status === 413) return 'La solicitud es demasiado grande. Reduce el brief o el archivo adjunto.';
  return text || `HTTP ${res.status}`;
}

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {})
    },
    cache: 'no-store'
  });
  if (!res.ok) {
    const detail = await parseError(res);
    throw new ApiError(detail, res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export async function getHealth(): Promise<Health> {
  return api<Health>('/health');
}

export async function listProjects(): Promise<Project[]> {
  return api<Project[]>('/projects');
}

export async function createProject(payload: CampaignRequest['project']): Promise<Project> {
  return api<Project>('/projects', { method: 'POST', body: JSON.stringify(payload) });
}

export async function createCampaign(projectId: string, payload: CampaignRequest['campaign']): Promise<Campaign> {
  return api<Campaign>(`/projects/${projectId}/campaigns`, { method: 'POST', body: JSON.stringify(payload) });
}

export async function getCampaign(id: string): Promise<Campaign> {
  return api<Campaign>(`/campaigns/${id}`);
}

export async function renameCampaign(id: string, title: string): Promise<Campaign> {
  return api<Campaign>(`/campaigns/${id}/title`, {
    method: 'PATCH',
    body: JSON.stringify({ title })
  });
}

export async function deleteCampaign(id: string): Promise<void> {
  return api<void>(`/campaigns/${id}`, { method: 'DELETE' });
}

export async function getEvents(id: string): Promise<AgentEvent[]> {
  return api<AgentEvent[]>(`/campaigns/${id}/events`);
}

export async function sendFeedback(campaignId: string, feedback: string): Promise<Campaign> {
  return api<Campaign>(`/campaigns/${campaignId}/feedback`, {
    method: 'POST',
    body: JSON.stringify({ feedback })
  });
}

export async function approveCampaign(campaignId: string): Promise<Campaign> {
  return api<Campaign>(`/campaigns/${campaignId}/approve`, { method: 'POST' });
}

export async function rerunCampaign(campaignId: string): Promise<Campaign> {
  return api<Campaign>(`/campaigns/${campaignId}/run`, { method: 'POST' });
}

export async function uploadBrandAsset(projectId: string, label: string, file: File): Promise<void> {
  const form = new FormData();
  form.append('label', label);
  form.append('file', file);
  const res = await fetch(`${API_URL}/projects/${projectId}/brand-assets`, {
    method: 'POST',
    body: form,
    cache: 'no-store'
  });
  if (!res.ok) {
    const detail = await parseError(res);
    throw new ApiError(detail, res.status, detail);
  }
}

export function exportUrl(id: string, format: 'json' | 'markdown' | 'zip' | 'pdf') {
  return `${API_URL}/campaigns/${id}/export/${format}`;
}

export function wsUrl(id: string) {
  const base = API_URL.replace(/^http/, 'ws');
  return `${base}/ws/campaigns/${id}`;
}

export function campaignSharePath(id: string) {
  return `/campaigns/${id}`;
}
