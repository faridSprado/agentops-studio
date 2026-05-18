import type { Health } from '@/lib/types';
import { cx } from '@/lib/utils';

type TechItem = { name: string; tone: string; icon: 'next' | 'fastapi' | 'groq' | 'python' | 'ts' };

export function ProductLogo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div className="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 48 48" className="h-7 w-7">
          <defs>
            <linearGradient id="agentops-mark" x1="0" x2="1" y1="0" y2="1">
              <stop offset="0" stopColor="#f3b49f" />
              <stop offset="0.5" stopColor="#d4715c" />
              <stop offset="1" stopColor="#7d9b8a" />
            </linearGradient>
          </defs>
          <path d="M24 5 41 14.5v19L24 43 7 33.5v-19L24 5Z" fill="url(#agentops-mark)" opacity="0.92" />
          <path d="M16 18.5h16M16 24h16M16 29.5h10" stroke="#0a0908" strokeWidth="3" strokeLinecap="round" />
          <circle cx="34" cy="29" r="3" fill="#0a0908" />
        </svg>
      </div>
      <div className={compact ? 'hidden sm:block' : ''}>
        <p className="label-caps">Creative AgentOps</p>
        <h1 className="font-display text-[1.65rem] font-extrabold leading-none tracking-tight text-cream sm:text-3xl">Multimedia AgentOps Studio</h1>
      </div>
    </div>
  );
}

export function ProviderBadge({ health, healthError }: { health?: Health | null; healthError?: boolean }) {
  if (healthError) return <span className="status-pill status-warn">API iniciando</span>;
  if (!health) return <span className="status-pill status-muted">Verificando API</span>;
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className={cx('status-pill', health.llm_enabled ? 'status-success' : 'status-warn')}>
        API conectada · IA: {health.provider || 'mock'}
      </span>
      <span className={cx('status-pill', health.mock_mode ? 'status-warn' : 'status-success')}>
        {health.mock_mode ? 'Modo demo' : 'IA real'}
      </span>
    </div>
  );
}

export function TechLogoCloud() {
  const items: TechItem[] = [
    { name: 'Next.js', tone: 'dark', icon: 'next' },
    { name: 'FastAPI', tone: 'green', icon: 'fastapi' },
    { name: 'Groq', tone: 'orange', icon: 'groq' },
    { name: 'Python', tone: 'blue', icon: 'python' },
    { name: 'TypeScript', tone: 'blue', icon: 'ts' }
  ];
  return (
    <div className="hidden flex-wrap items-center gap-2 lg:flex" aria-label="Tecnologías del proyecto">
      {items.map(item => (
        <span key={item.name} className={cx('tech-logo', `tech-logo-${item.tone}`)}>
          <TechIcon icon={item.icon} />
          <span>{item.name}</span>
        </span>
      ))}
    </div>
  );
}

function TechIcon({ icon }: { icon: TechItem['icon'] }) {
  const base = 'h-3.5 w-3.5 shrink-0';
  if (icon === 'next') {
    return (
      <svg viewBox="0 0 24 24" className={base} aria-hidden="true">
        <circle cx="12" cy="12" r="11" fill="currentColor" opacity=".92" />
        <path d="M8 7.5h2.4l5.2 8.5V7.5H18v9h-2.4l-5.2-8.4v8.4H8v-9Z" fill="#0a0908" />
      </svg>
    );
  }
  if (icon === 'fastapi') {
    return (
      <svg viewBox="0 0 24 24" className={base} aria-hidden="true">
        <circle cx="12" cy="12" r="11" fill="currentColor" opacity=".35" />
        <path d="M13.2 2.8 6.4 13h4.7l-1 8.2 7.4-11.6h-4.7l.4-6.8Z" fill="currentColor" />
      </svg>
    );
  }
  if (icon === 'groq') {
    return (
      <svg viewBox="0 0 24 24" className={base} aria-hidden="true">
        <rect x="3" y="3" width="18" height="18" rx="5" fill="currentColor" opacity=".25" />
        <path d="M8 8.2h5.6a3.8 3.8 0 0 1 0 7.6H11v-2.3h2.5a1.5 1.5 0 0 0 0-3H8V8.2Zm0 5.3h2.4v2.3H8v-2.3Z" fill="currentColor" />
      </svg>
    );
  }
  if (icon === 'python') {
    return (
      <svg viewBox="0 0 24 24" className={base} aria-hidden="true">
        <path d="M12 3c-3 0-4.5 1.1-4.5 3.3V9H14v1.5H6.3C4.1 10.5 3 12 3 14.5 3 17 4.2 18 6.3 18h2.2v-3c0-2.1 1.3-3.5 3.5-3.5h5c2 0 3.5-1.3 3.5-3.5V6.3C20.5 4.1 18.9 3 16 3h-4Z" fill="currentColor" opacity=".55" />
        <path d="M12 21c3 0 4.5-1.1 4.5-3.3V15H10v-1.5h7.7c2.2 0 3.3-1.5 3.3-4 0-2.4-1.2-3.5-3.3-3.5h-2.2v3c0 2.1-1.3 3.5-3.5 3.5H7c-2 0-3.5 1.3-3.5 3.5v1.7C3.5 19.9 5.1 21 8 21h4Z" fill="currentColor" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 24 24" className={base} aria-hidden="true">
      <rect x="3" y="3" width="18" height="18" rx="3" fill="currentColor" opacity=".35" />
      <path d="M7 8h10v2H13v7h-2v-7H7V8Zm8.2 8.9c-1.1 0-2-.3-2.7-.9l.9-1.5c.5.4 1.1.7 1.8.7.6 0 1-.2 1-.6 0-.5-.5-.6-1.3-.9-1.2-.4-2-1-2-2.2 0-1.3 1-2.2 2.7-2.2.9 0 1.7.2 2.4.7l-.8 1.5c-.5-.3-1-.5-1.6-.5s-.8.2-.8.5c0 .4.5.6 1.2.8 1.3.4 2.1 1 2.1 2.3 0 1.5-1.1 2.3-2.9 2.3Z" fill="currentColor" />
    </svg>
  );
}
