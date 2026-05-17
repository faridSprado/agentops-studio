from __future__ import annotations

from typing import Any, Callable, TypedDict

from app.core.config import Settings, get_settings
from app.services.llm import LLMClient
from app.services.metrics import score_breakdown, score_rationale, score_state
from app.services.prompts import PROMPTS

try:
    from langgraph.graph import END, START, StateGraph
except Exception:
    END = "__end__"
    START = "__start__"
    StateGraph = None


class CampaignState(TypedDict, total=False):
    project: dict[str, Any]
    brief: str
    channels: list[str]
    language: str
    tone: str
    human_review: bool
    feedback: str
    memory: list[dict[str, Any]]
    normalized: dict[str, Any]
    research: dict[str, Any]
    strategy: dict[str, Any]
    copy: dict[str, Any]
    storyboard: dict[str, Any]
    visual: dict[str, Any]
    execution_plan: dict[str, Any]
    kpis: dict[str, Any]
    brand_review: dict[str, Any]
    evaluation: dict[str, Any]
    revision: dict[str, Any]
    revision_count: int
    score: int
    score_breakdown: dict[str, Any]
    final: dict[str, Any]
    status: str


class AgentWorkflow:
    def __init__(self, settings: Settings | None = None, llm: LLMClient | None = None, emit: Callable[[str, str, dict[str, Any] | None], None] | None = None):
        self.settings = settings or get_settings()
        self.llm = llm or LLMClient(self.settings)
        self.emit = emit or (lambda agent, status, payload=None: None)
        self.graph = self._build_graph() if StateGraph and self.settings.use_langgraph else None

    def run(self, state: CampaignState) -> CampaignState:
        state.setdefault("revision_count", 0)
        if self.graph:
            return self.graph.invoke(state)
        return self._run_fallback(state)

    def _build_graph(self):
        graph = StateGraph(CampaignState)
        graph.add_node("normalize", self.normalize)
        graph.add_node("research", self.research)
        graph.add_node("strategy", self.strategy)
        graph.add_node("copy", self.copy)
        graph.add_node("storyboard", self.storyboard)
        graph.add_node("visual", self.visual)
        graph.add_node("execution_plan", self.execution_plan)
        graph.add_node("kpis", self.kpis)
        graph.add_node("brand_review", self.brand_review)
        graph.add_node("evaluate", self.evaluate)
        graph.add_node("revise", self.revise)
        graph.add_node("assemble", self.assemble)
        graph.add_edge(START, "normalize")
        graph.add_edge("normalize", "research")
        graph.add_edge("research", "strategy")
        graph.add_edge("strategy", "copy")
        graph.add_edge("copy", "storyboard")
        graph.add_edge("storyboard", "visual")
        graph.add_edge("visual", "execution_plan")
        graph.add_edge("execution_plan", "kpis")
        graph.add_edge("kpis", "brand_review")
        graph.add_edge("brand_review", "evaluate")
        graph.add_conditional_edges("evaluate", self.route, {"revise": "revise", "finish": "assemble"})
        graph.add_edge("revise", "copy")
        graph.add_edge("assemble", END)
        return graph.compile()

    def _run_fallback(self, state: CampaignState) -> CampaignState:
        for step in [self.normalize, self.research, self.strategy, self.copy, self.storyboard, self.visual, self.execution_plan, self.kpis, self.brand_review, self.evaluate]:
            state.update(step(state))
        while self.route(state) == "revise":
            state.update(self.revise(state))
            for step in [self.copy, self.storyboard, self.visual, self.execution_plan, self.kpis, self.brand_review, self.evaluate]:
                state.update(step(state))
        state.update(self.assemble(state))
        return state

    def normalize(self, state: CampaignState) -> dict[str, Any]:
        payload = self._base_payload(state)
        return {"normalized": self._run_agent("normalizer", payload)}

    def research(self, state: CampaignState) -> dict[str, Any]:
        payload = self._base_payload(state) | {"normalized": state.get("normalized")}
        return {"research": self._run_agent("research", payload)}

    def strategy(self, state: CampaignState) -> dict[str, Any]:
        payload = self._base_payload(state) | {"normalized": state.get("normalized"), "research": state.get("research")}
        return {"strategy": self._run_agent("strategy", payload)}

    def copy(self, state: CampaignState) -> dict[str, Any]:
        payload = self._base_payload(state) | {"strategy": state.get("strategy"), "revision": state.get("revision")}
        return {"copy": self._run_agent("copy", payload)}

    def storyboard(self, state: CampaignState) -> dict[str, Any]:
        payload = self._base_payload(state) | {"strategy": state.get("strategy"), "copy": state.get("copy")}
        return {"storyboard": self._run_agent("storyboard", payload)}

    def visual(self, state: CampaignState) -> dict[str, Any]:
        payload = self._base_payload(state) | {"strategy": state.get("strategy"), "storyboard": state.get("storyboard")}
        return {"visual": self._run_agent("visual", payload)}

    def execution_plan(self, state: CampaignState) -> dict[str, Any]:
        payload = self._base_payload(state) | {"strategy": state.get("strategy"), "copy": state.get("copy"), "storyboard": state.get("storyboard"), "visual": state.get("visual")}
        return {"execution_plan": self._run_agent("execution_plan", payload)}

    def kpis(self, state: CampaignState) -> dict[str, Any]:
        payload = self._base_payload(state) | {"strategy": state.get("strategy"), "copy": state.get("copy"), "execution_plan": state.get("execution_plan")}
        return {"kpis": self._run_agent("kpis", payload)}

    def brand_review(self, state: CampaignState) -> dict[str, Any]:
        payload = self._base_payload(state) | {"strategy": state.get("strategy"), "copy": state.get("copy"), "storyboard": state.get("storyboard"), "visual": state.get("visual"), "execution_plan": state.get("execution_plan"), "kpis": state.get("kpis")}
        return {"brand_review": self._run_agent("brand_review", payload)}

    def evaluate(self, state: CampaignState) -> dict[str, Any]:
        payload = self._base_payload(state) | {"state": {key: state.get(key) for key in ["research", "strategy", "copy", "storyboard", "visual", "execution_plan", "kpis", "brand_review"]}}
        output = self._run_agent("evaluator", payload)
        breakdown = score_breakdown(state | {"evaluation": output})
        score = int(breakdown["overall"])
        output["data"] = output.get("data", {}) | breakdown | {"threshold": self.settings.quality_threshold}
        return {"evaluation": output, "score": score, "score_breakdown": breakdown}

    def revise(self, state: CampaignState) -> dict[str, Any]:
        payload = self._base_payload(state) | {"evaluation": state.get("evaluation"), "score": state.get("score"), "current": {key: state.get(key) for key in ["strategy", "copy", "storyboard", "visual", "execution_plan", "kpis"]}}
        revision = self._run_agent("reviser", payload)
        return {"revision": revision, "revision_count": int(state.get("revision_count") or 0) + 1}

    def assemble(self, state: CampaignState) -> dict[str, Any]:
        score = int(state.get("score") or 0)
        status = "needs_review" if state.get("human_review") or score < self.settings.quality_threshold else "completed"
        sections = {
            "research": state.get("research"),
            "strategy": state.get("strategy"),
            "copy": state.get("copy"),
            "storyboard": state.get("storyboard"),
            "visual": state.get("visual"),
            "execution_plan": state.get("execution_plan"),
            "kpis": state.get("kpis"),
            "brand_review": state.get("brand_review"),
            "evaluation": state.get("evaluation"),
        }
        strategy = state.get("strategy") or {}
        final = {
            "title": strategy.get("title") or "Campaña multimedia",
            "summary": strategy.get("summary") or "Campaña generada por agentes especializados.",
            "brief": state.get("brief", ""),
            "channels": state.get("channels", []),
            "score": score,
            "score_breakdown": state.get("score_breakdown") or {},
            "score_rationale": score_rationale(state.get("score_breakdown") or {}),
            "revisions": int(state.get("revision_count") or 0),
            "provider": self.settings.provider,
            "mock_mode": self.settings.mock_mode or self.settings.provider == "mock",
            "sections": sections,
            "executive": self._executive_summary(sections),
        }
        self.emit("assembler", status, {"score": score})
        return {"final": final, "status": status}

    def route(self, state: CampaignState) -> str:
        score = int(state.get("score") or 0)
        revisions = int(state.get("revision_count") or 0)
        return "revise" if score < self.settings.quality_threshold and revisions < self.settings.max_revisions else "finish"

    def _base_payload(self, state: CampaignState) -> dict[str, Any]:
        return {
            "project": state.get("project", {}),
            "brief": state.get("brief", ""),
            "channels": state.get("channels", []),
            "language": state.get("language", "es"),
            "tone": state.get("tone", "profesional"),
            "feedback": state.get("feedback", ""),
            "memory": state.get("memory", []),
        }

    def _run_agent(self, agent: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.emit(agent, "running", {})
        output = self.llm.run(agent, PROMPTS[agent], payload)
        output = self._polish_agent_output(agent, output, payload)
        self.emit(agent, "completed", {"title": output.get("title"), "summary": output.get("summary")})
        return output


    def _polish_agent_output(self, agent: str, output: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        project = payload.get("project") or {}
        brand = str(project.get("name") or "la marca").strip()
        audience = str(project.get("audience") or "la audiencia objetivo").strip()
        channels = payload.get("channels") or ["instagram", "landing", "email"]
        tone = str(payload.get("tone") or "profesional").strip()
        brief = str(payload.get("brief") or "campaña multimedia").strip()
        data = output.get("data") if isinstance(output.get("data"), dict) else {}
        items = self._dedupe_items(output.get("items") or [])

        templates = self._specific_templates(agent, brand, audience, channels, tone, brief)
        output["title"] = templates["title"]
        output["summary"] = self._agent_summary(agent, brand, audience, channels, brief, str(output.get("summary") or ""), templates["summary"])
        output["items"] = self._merge_items(agent, items, templates["items"])[:6]
        output["data"] = self._merge_data(data, templates["data"])
        output["data"]["agent_focus"] = self._agent_focus(agent)
        return output

    def _specific_templates(self, agent: str, brand: str, audience: str, channels: list[str], tone: str, brief: str) -> dict[str, Any]:
        channel_text = ", ".join(channels[:5])
        brand_short = brand if brand != "la marca" else "la marca"
        if agent == "research":
            return {
                "title": f"Mapa de insights para {brand_short}",
                "summary": f"Lectura de audiencia y oportunidades para conectar {brand_short} con {audience} sin caer en mensajes genéricos.",
                "items": [
                    f"Tensión principal: {audience} busca inspiración, pero filtra rápido las marcas que suenan decorativas o vacías",
                    "Oportunidad: convertir el beneficio en una escena concreta de uso, no en una promesa abstracta",
                    f"Objeción probable: validar por qué {brand_short} merece atención frente a alternativas conocidas",
                    f"Canales prioritarios: adaptar el mismo territorio creativo a {channel_text} con formatos nativos",
                    "Supuesto a validar: qué mensaje activa más guardados, clics y registros cualificados",
                ],
                "data": {
                    "audience_tension": f"{audience} necesita una razón visual y práctica para recordar la marca",
                    "content_opportunity": "demostrar el beneficio en contexto real durante los primeros 3 segundos",
                    "validation_assumptions": ["hook visual", "prueba de utilidad", "CTA sin fricción"],
                },
            }
        if agent == "strategy":
            return {
                "title": f"Sistema estratégico para {brand_short}",
                "summary": f"Posicionar {brand_short} con una idea central clara, un rol por canal y una ruta de conversión accionable.",
                "items": [
                    f"Big idea: transformar {brand_short} en un ritual reconocible para {audience}",
                    "Mensaje rector: menos ruido, más intención y una acción clara después de cada pieza",
                    f"Rol de canales: {channel_text} distribuyen descubrimiento, prueba, conversión y retención",
                    "Funnel: awareness visual, consideración con prueba concreta, conversión con oferta simple",
                    "Riesgo estratégico: sonar aspiracional sin mostrar una diferencia comprobable",
                ],
                "data": {
                    "big_idea": f"{brand_short} como ritual de enfoque para {audience}",
                    "channel_roles": {str(ch): self._channel_role(str(ch)) for ch in channels},
                    "campaign_phases": ["teaser", "lanzamiento", "prueba social", "optimización"],
                },
            }
        if agent == "copy":
            return {
                "title": f"Piezas de copy listas para {brand_short}",
                "summary": f"Hooks, titulares y CTAs concretos para que {brand_short} convierta atención en acción medible.",
                "items": [
                    f'Hook 1: "Cuando el ruido baja, {brand_short} empieza a trabajar."',
                    'Hook 2: "Tu próxima sesión merece algo mejor que improvisación."',
                    f'Landing hero: "{brand_short}: una marca para convertir intención en progreso."',
                    "CTA principal: Ver la campaña / Probar ahora / Empezar mi ritual",
                    "Email subject: Tu próxima sesión profunda empieza aquí",
                    "Variante A/B: beneficio funcional vs. beneficio emocional",
                ],
                "data": {
                    "hooks": [f"Cuando el ruido baja, {brand_short} empieza a trabajar", "Menos distracción. Más intención.", "Haz que tu próxima sesión cuente"],
                    "landing_hero": {"headline": f"{brand_short} para quienes trabajan con intención", "subheadline": f"Una propuesta {tone} para {audience}.", "cta": "Empezar ahora"},
                    "ctas": ["Empezar ahora", "Ver cómo funciona", "Crear mi ritual"],
                },
            }
        if agent == "storyboard":
            return {
                "title": f"Storyboard producible para {brand_short}",
                "summary": f"Guion corto, visual y ejecutable para convertir el territorio creativo de {brand_short} en video de portfolio.",
                "items": [
                    "0-3s: plano detalle del contexto/problema con texto en pantalla fuerte",
                    f"3-7s: aparece {brand_short} como cambio de ritmo o solución visual",
                    "7-12s: montaje de uso real, gesto humano y resultado observable",
                    "12-18s: beneficio principal con una frase memorable",
                    "18-22s: cierre con logo, CTA y variación para formato vertical",
                ],
                "data": {
                    "scenes": [
                        {"time": "0-3s", "shot": "plano detalle", "action": "mostrar tensión cotidiana", "screen_text": "Cuando todo compite por tu atención", "audio": "ambiente bajo + golpe suave", "transition": "corte seco"},
                        {"time": "3-7s", "shot": "medio", "action": f"introducir {brand_short} como ritual", "screen_text": "Elige tu próxima sesión", "audio": "beat cálido", "transition": "match cut"},
                        {"time": "7-12s", "shot": "montaje", "action": "mostrar proceso y resultado", "screen_text": "Menos ruido. Más intención.", "audio": "ritmo ascendente", "transition": "whip pan"},
                        {"time": "12-18s", "shot": "hero", "action": "cerrar con promesa concreta", "screen_text": f"{brand_short}", "audio": "cierre limpio", "transition": "fade"},
                    ],
                    "production_assets": ["logo", "packshot o UI", "tomas detalle", "música licenciada", "versión 9:16"],
                },
            }
        if agent == "visual":
            return {
                "title": f"Dirección visual premium para {brand_short}",
                "summary": f"Guía visual legible y producible para que {brand_short} tenga consistencia en piezas sociales, landing y video.",
                "items": [
                    "Paleta: fondo profundo, acento luminoso y neutros cálidos para contraste editorial",
                    "Tipografía: sans bold para titulares y serif/sans humanista para detalles premium",
                    "Composición: sujeto/objeto en primer tercio, mucho espacio negativo y foco en textura",
                    "Regla visual: cada pieza debe mostrar contexto, beneficio y gesto humano",
                    "Evitar: clichés visuales, exceso de stock, filtros genéricos o promesas grandilocuentes",
                ],
                "data": {
                    "palette": ["#020617", "#38BDF8", "#E2E8F0", "#A16207"],
                    "composition_rules": ["alto contraste", "espacio negativo", "texturas reales", "CTA visible"],
                    "visual_prompts": [f"campaign hero for {brand_short}, cinematic editorial lighting, premium product texture", f"vertical social ad for {audience}, clean composition, strong negative space"],
                    "avoid": ["stock evidente", "clichés", "saturación visual", "claims absolutos"],
                },
            }
        if agent == "execution_plan":
            return {
                "title": f"Plan operativo de 4 semanas para {brand_short}",
                "summary": f"Ruta de producción para convertir la campaña de {brand_short} en piezas publicables, medibles y ajustables.",
                "items": [
                    "Semana 1: cerrar concepto, guiones, arte base y tracking",
                    "Semana 2: producir videos, landing y emails principales",
                    "Semana 3: lanzar teaser, hero video y primeras piezas por canal",
                    "Semana 4: optimizar según CTR, retención, leads y feedback cualitativo",
                    "Checklist: assets aprobados, eventos medidos, enlaces UTM y revisión de marca",
                ],
                "data": {
                    "timeline_weeks": [
                        {"week": 1, "focus": "concepto, scripts y guía visual"},
                        {"week": 2, "focus": "producción y landing"},
                        {"week": 3, "focus": "lanzamiento multicanal"},
                        {"week": 4, "focus": "optimización y reporte"},
                    ],
                    "owner_roles": ["producer", "copywriter", "designer", "editor", "growth"],
                    "launch_checklist": ["UTMs", "pixel/eventos", "QA mobile", "exports 9:16", "aprobación legal/marca"],
                },
            }
        if agent == "kpis":
            return {
                "title": f"Medición accionable para {brand_short}",
                "summary": f"KPIs realistas para medir si la campaña de {brand_short} genera atención útil, intención y conversión.",
                "items": [
                    "North Star: leads o conversiones cualificadas por canal",
                    "Awareness: alcance, frecuencia y retención de video al 50%",
                    "Engagement: guardados, clics al perfil, respuestas y shares",
                    "Conversión: CTR landing, formularios enviados y coste por lead",
                    "Aprendizaje: comparar hook emocional vs. hook funcional",
                ],
                "data": {
                    "north_star_metric": "conversiones cualificadas por canal",
                    "targets": {"ctr_landing": "2-5%", "video_retention_50": "25-40%", "lead_conversion": "3-8%"},
                    "tracking_events": ["view_content", "video_50", "click_cta", "lead_submit", "purchase"],
                    "dashboard_view": ["canal", "pieza", "hook", "retención", "CTR", "conversiones"],
                    "learning_questions": ["qué hook retiene mejor", "qué canal convierte más", "qué objeción frena la compra"],
                },
            }
        if agent == "brand_review":
            return {
                "title": f"QA de marca para {brand_short}",
                "summary": f"Auditoría práctica para mantener consistencia, evitar claims débiles y preparar {brand_short} para publicación.",
                "items": [
                    "Mantener una sola promesa central por pieza",
                    "Sustituir superlativos por beneficios observables",
                    "Revisar coherencia visual entre social, landing y email",
                    "Asegurar CTA visible y específico en cada formato",
                    "Validar que las metas no prometan resultados garantizados",
                ],
                "data": {
                    "risk_level": "low",
                    "recommended_edits": ["reducir repetición del posicionamiento", "concretar CTAs", "alinear visuales con beneficio"],
                    "approval_status": "approved_with_minor_edits",
                },
            }
        if agent == "evaluator":
            return {
                "title": f"Evaluación profesional de {brand_short}",
                "summary": f"Revisión de calidad para determinar si la campaña de {brand_short} está lista para demo, producción piloto o iteración.",
                "items": [
                    "La campaña tiene una narrativa clara y adaptable a varios canales",
                    "El plan operativo y los KPIs mejoran la accionabilidad",
                    "La profundidad creativa puede subir con más pruebas de concepto visual",
                    "Riesgo bajo si se mantienen claims verificables y tono consistente",
                ],
                "data": {
                    "go_no_go": "go_for_pilot",
                    "revision_priorities": ["más variaciones de hooks", "mayor especificidad visual", "validar métricas tras primera semana"],
                },
            }
        return {"title": f"{agent.replace('_', ' ').title()} para {brand_short}", "summary": f"Entregable de {agent} para {brand_short}.", "items": [], "data": {}}

    def _agent_focus(self, agent: str) -> str:
        return {
            "normalizer": "convertir el brief en insumos operativos",
            "research": "hallazgos, tensiones y supuestos verificables",
            "strategy": "decisiones de posicionamiento, funnel y rol de canales",
            "copy": "textos finales listos para publicar",
            "storyboard": "escenas producibles con tiempos, planos y CTA",
            "visual": "dirección de arte, reglas visuales y prompts",
            "execution_plan": "semanas, entregables, responsables y dependencias",
            "kpis": "métricas, eventos, metas y tablero",
            "brand_review": "riesgos, inconsistencias y correcciones concretas",
            "evaluator": "score, justificación y decisión go/no-go",
        }.get(agent, "entregable especializado")

    def _agent_summary(self, agent: str, brand: str, audience: str, channels: list[str], brief: str, llm_summary: str, template_summary: str) -> str:
        llm_summary = " ".join(str(llm_summary or "").split())[:260]
        channel_text = ", ".join(channels[:4])
        summaries = {
            "normalizer": f"Brief convertido en variables operativas: objetivo, audiencia, tono, restricciones y canales para ejecutar sin ambigüedad.",
            "research": f"Lectura de mercado para detectar tensiones de {audience}, objeciones de compra y oportunidades verificables antes de producir piezas.",
            "strategy": f"Sistema de posicionamiento para {brand}: big idea, mensaje rector, funnel y rol específico de {channel_text}.",
            "copy": f"Banco de hooks, titulares, CTAs, hero de landing y variantes A/B para transformar la estrategia de {brand} en lenguaje publicable.",
            "storyboard": f"Guion audiovisual por escenas para que {brand} pueda producir piezas verticales con planos, ritmo, texto en pantalla y cierre claro.",
            "visual": f"Dirección de arte para {brand}: moodboard, paleta, composición, prompts y reglas de consistencia visual.",
            "execution_plan": f"Plan operativo de 4 semanas con hitos, responsables, dependencias y checklist para lanzar la campaña sin improvisación.",
            "kpis": f"Modelo de medición para {brand}: North Star, eventos, metas iniciales, dashboard y preguntas de aprendizaje.",
            "brand_review": f"Auditoría de coherencia para detectar claims débiles, riesgos de tono, repetición y ajustes concretos antes de publicar.",
            "evaluator": f"Evaluación profesional con score, fortalezas, debilidades, riesgos y decisión de producción piloto.",
        }
        generic_hits = sum(1 for token in ("desarrollar una", "posicionar", "campaña multimedia", "identidad visual y narrativa", "estrategia de campaña") if token in llm_summary.lower())
        if agent in summaries and (not llm_summary or generic_hits >= 1 or len(llm_summary) < 80):
            return summaries[agent]
        return llm_summary or template_summary

    def _channel_role(self, channel: str) -> str:
        mapping = {
            "instagram": "descubrimiento visual y guardados",
            "tiktok": "alcance rápido y prueba de hooks",
            "youtube": "storytelling y demostración larga",
            "landing": "conversión y claridad de oferta",
            "email": "nutrición, objeciones y cierre",
            "linkedin": "credibilidad B2B y autoridad",
        }
        return mapping.get(channel.lower(), "adaptación de mensaje y medición")

    def _dedupe_items(self, items: list[Any]) -> list[str]:
        clean = []
        seen = set()
        for item in items:
            text = " ".join(str(item).replace("\n", " ").split())
            if not text or len(text) < 6:
                continue
            key = text.lower()[:90]
            if key in seen:
                continue
            seen.add(key)
            clean.append(text)
        return clean

    def _merge_items(self, agent: str, current: list[str], templates: list[str]) -> list[str]:
        weak_words = ("crear contenido", "diseñar", "desarrollar", "posicionar", "definir")
        agent_ban = {
            "research": ("cta", "caption", "storyboard", "semana ", "landing hero"),
            "strategy": ("hook", "caption", "plano", "time", "shot"),
            "copy": ("funnel", "kpi", "riesgo operativo", "semana "),
            "storyboard": ("kpi", "north star", "funnel", "paleta"),
            "visual": ("kpi", "semana ", "funnel", "email subject"),
            "execution_plan": ("hook", "caption", "moodboard"),
            "kpis": ("storyboard", "paleta", "caption", "guion"),
            "brand_review": ("hook", "semana ", "north star"),
            "evaluator": ("hook", "caption", "paleta"),
        }.get(agent, ())
        concrete = []
        for item in current:
            low = item.lower()
            if len(item) < 30 or low.startswith(weak_words):
                continue
            if any(term in low for term in agent_ban):
                continue
            concrete.append(item)
        return self._dedupe_items(templates + concrete)

    def _merge_data(self, current: dict[str, Any], templates: dict[str, Any]) -> dict[str, Any]:
        merged = dict(current)
        for key, value in templates.items():
            if key not in merged or merged.get(key) in ({}, [], "", None):
                merged[key] = value
        return merged

    def _executive_summary(self, sections: dict[str, Any]) -> list[dict[str, Any]]:
        order = [
            ("strategy", "Estrategia"),
            ("copy", "Copy multicanal"),
            ("storyboard", "Storyboard"),
            ("visual", "Dirección visual"),
            ("execution_plan", "Plan de ejecución"),
            ("kpis", "KPIs y medición"),
            ("brand_review", "Revisión de marca"),
        ]
        items = []
        for key, label in order:
            section = sections.get(key) or {}
            items.append({
                "label": label,
                "title": section.get("title") or label,
                "summary": section.get("summary") or "",
                "items": section.get("items") or [],
            })
        return items
