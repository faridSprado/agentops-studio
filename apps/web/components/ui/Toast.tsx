'use client';

import { useToast } from '@/hooks/useToast';
import { cx } from '@/lib/utils';

const kindStyles = {
  success: 'border-sage/30 bg-sage-muted text-sage-light',
  error: 'border-red-500/30 bg-red-500/10 text-red-200',
  info: 'border-brand/30 bg-brand/10 text-brand-light'
};

export function ToastViewport() {
  const { toasts, dismiss } = useToast();
  if (!toasts.length) return null;

  return (
    <div
      className="pointer-events-none fixed bottom-6 right-6 z-[100] flex w-full max-w-sm flex-col gap-2 px-4 sm:px-0"
      aria-live="polite"
    >
      {toasts.map(toast => (
        <div
          key={toast.id}
          role="status"
          className={cx(
            'pointer-events-auto animate-slide-up rounded-xl border px-4 py-3 text-sm shadow-panel backdrop-blur-md',
            kindStyles[toast.kind]
          )}
        >
          <div className="flex items-start justify-between gap-3">
            <span>{toast.message}</span>
            <button
              type="button"
              onClick={() => dismiss(toast.id)}
              className="shrink-0 opacity-60 hover:opacity-100"
              aria-label="Cerrar"
            >
              ✕
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
