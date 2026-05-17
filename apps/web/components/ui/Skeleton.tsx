import { cx } from '@/lib/utils';

export function Skeleton({ className }: { className?: string }) {
  return <div className={cx('animate-shimmer rounded-lg bg-line/60', className)} aria-hidden />;
}

export function CampaignSkeleton() {
  return (
    <section className="panel overflow-hidden">
      <div className="panel-head">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="mt-3 h-8 w-2/3" />
      </div>
      <div className="panel-body space-y-4">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-xl" />
          ))}
        </div>
      </div>
    </section>
  );
}
