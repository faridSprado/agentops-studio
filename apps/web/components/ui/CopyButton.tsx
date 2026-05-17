'use client';

import { useState } from 'react';
import { cx } from '@/lib/utils';

export function CopyButton({ text, label = 'Copiar' }: { text: string; label?: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard blocked */
    }
  }

  return (
    <button
      type="button"
      onClick={copy}
      className={cx(
        'btn-ghost text-xs',
        copied && 'border-lime-300/40 text-lime-200'
      )}
    >
      {copied ? 'Copiado' : label}
    </button>
  );
}
