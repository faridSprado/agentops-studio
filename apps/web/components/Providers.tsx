'use client';

import { ToastProvider } from '@/hooks/useToast';
import { ToastViewport } from '@/components/ui/Toast';
import type { ReactNode } from 'react';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ToastProvider>
      {children}
      <ToastViewport />
    </ToastProvider>
  );
}
