import { Suspense } from 'react';
import { Studio } from '@/components/Studio';

function StudioFallback() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <p className="animate-pulse text-slate-400">Cargando AgentOps Studio…</p>
    </main>
  );
}

export default function Page() {
  return (
    <Suspense fallback={<StudioFallback />}>
      <Studio />
    </Suspense>
  );
}
