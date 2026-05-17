export function statusLabel(status: string) {
  const labels: Record<string, string> = {
    idle: 'Listo',
    queued: 'En cola',
    running: 'Generando',
    completed: 'Completada',
    needs_review: 'Pendiente de revisión',
    failed: 'No completada'
  };
  return labels[status] || status;
}

export function sectionLabel(name: string) {
  const labels: Record<string, string> = {
    research: 'Investigación',
    strategy: 'Estrategia',
    copy: 'Textos multicanal',
    storyboard: 'Storyboard',
    visual: 'Dirección visual',
    execution_plan: 'Plan de ejecución',
    kpis: 'KPIs y medición',
    brand_review: 'Revisión de marca',
    evaluation: 'Evaluación'
  };
  return labels[name] || name.replaceAll('_', ' ');
}

export function scoreLabel(name: string) {
  const labels: Record<string, string> = {
    clarity: 'Claridad',
    brand_alignment: 'Ajuste a marca',
    channel_fit: 'Ajuste a canales',
    creative_depth: 'Profundidad creativa',
    execution_readiness: 'Lista para ejecutar',
    risk_control: 'Control de riesgo',
    overall: 'Puntaje final',
    summary: 'Resumen',
    execution: 'Ejecución',
    risk: 'Riesgo'
  };
  return labels[name] || name;
}

export function channelLabel(channel: string) {
  const labels: Record<string, string> = {
    instagram: 'Instagram',
    tiktok: 'TikTok',
    landing: 'Landing page',
    email: 'Email',
    youtube: 'YouTube',
    linkedin: 'LinkedIn'
  };
  return labels[channel] || channel;
}

export function cx(...items: Array<string | false | null | undefined>) {
  return items.filter(Boolean).join(' ');
}
