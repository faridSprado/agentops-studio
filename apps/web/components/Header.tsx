import Link from 'next/link';
import type { Health } from '@/lib/types';
import { ProductLogo, ProviderBadge, TechLogoCloud } from '@/components/BrandIdentity';

export function Header({ health, healthError, connected }: { health?: Health | null; healthError?: boolean; connected?: boolean }) {
  return (
    <header className="relative z-20 border-b border-line/80 bg-ink/80 backdrop-blur-2xl">
      <div className="mx-auto flex max-w-[118rem] flex-wrap items-center justify-between gap-5 px-5 py-4 sm:px-8">
        <Link href="/" aria-label="Ir al inicio" className="group">
          <ProductLogo compact />
        </Link>
        <div className="flex flex-wrap items-center justify-end gap-3">
          <TechLogoCloud />
          {connected ? <span className="status-pill status-live">Flujo en vivo</span> : null}
          <ProviderBadge health={health} healthError={healthError} />
        </div>
      </div>
    </header>
  );
}
