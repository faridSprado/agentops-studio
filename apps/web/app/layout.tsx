import './globals.css';
import { Providers } from '@/components/Providers';
import type { Metadata, Viewport } from 'next';
import { Manrope } from 'next/font/google';
import type { ReactNode } from 'react';

const sans = Manrope({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap'
});

export const metadata: Metadata = {
  title: 'Multimedia AgentOps Studio — Campañas multimedia con IA',
  description: 'Plataforma full-stack de orquestación multiagente para convertir briefs en campañas multimedia completas.',
  keywords: ['AgentOps', 'multi-agent', 'marketing', 'campañas', 'IA', 'creatividad', 'Next.js', 'FastAPI'],
  icons: { icon: '/agentops-logo.svg' }
};

export const viewport: Viewport = {
  themeColor: '#0a0908',
  width: 'device-width',
  initialScale: 1
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="es" className={sans.variable} suppressHydrationWarning>
      <body className="font-sans antialiased" suppressHydrationWarning>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
