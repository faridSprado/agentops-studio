import { Suspense } from 'react';
import { Studio } from '@/components/Studio';

type Props = {
  params: Promise<{ id: string }>;
};

export default async function CampaignPage({ params }: Props) {
  const { id } = await params;
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center">
          <p className="text-slate-400">Cargando campaña…</p>
        </main>
      }
    >
      <Studio initialCampaignId={id} />
    </Suspense>
  );
}
