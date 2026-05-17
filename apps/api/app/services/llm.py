from __future__ import annotations

import json
import re
from typing import Any

from app.core.config import Settings, get_settings
from app.schemas import AgentOutput


class LLMClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.client = None
        self.model = ""
        if self.settings.mock_mode or self.settings.provider == "mock":
            return
        if self.settings.provider == "openai" and self.settings.openai_api_key:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.settings.openai_api_key)
            self.model = self.settings.openai_model
            return
        if self.settings.provider == "groq" and self.settings.groq_api_key:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.settings.groq_api_key, base_url="https://api.groq.com/openai/v1")
            self.model = self.settings.groq_model

    def run(self, agent: str, instructions: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.client:
            if self.settings.mock_mode or self.settings.provider == "mock":
                return self._mock(agent, payload)
            raise RuntimeError(self._missing_config_message())
        text = self._input_text(agent, instructions, payload)
        content = self._completion(text)
        try:
            data = self._parse_json(content)
            return AgentOutput.model_validate(data).model_dump()
        except Exception as exc:
            return AgentOutput.model_validate(self._fallback_from_invalid(agent, content, payload, exc)).model_dump()

    def _completion(self, text: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un agente senior de estrategia multimedia. Responde solo JSON válido. "
                    "Sin Markdown. Sin texto adicional. Todos los valores deben tener claves válidas. "
                    "Si necesitas listar hipótesis, metas, riesgos o preguntas, usa arrays, no objetos sin claves."
                ),
            },
            {"role": "user", "content": text},
        ]
        kwargs = {"model": self.model, "messages": messages, "temperature": 0.35, "max_tokens": self.settings.max_output_tokens}
        if self.settings.provider == "openai":
            kwargs["response_format"] = {"type": "json_object"}
        try:
            rsp = self.client.chat.completions.create(**kwargs)
            return rsp.choices[0].message.content or "{}"
        except Exception as exc:
            failed = self._failed_generation(exc)
            if failed:
                return failed
            raise

    def _failed_generation(self, exc: Exception) -> str:
        body = getattr(exc, "body", None)
        if isinstance(body, dict):
            error = body.get("error") or {}
            failed = error.get("failed_generation")
            if failed:
                return str(failed)
        text = str(exc)
        match = re.search(r"'failed_generation':\s*'(.+)'\s*}}", text, re.S)
        if match:
            return match.group(1).encode("utf-8").decode("unicode_escape")
        match = re.search(r'"failed_generation"\s*:\s*"(.+?)"\s*[,}]', text, re.S)
        if match:
            return match.group(1).encode("utf-8").decode("unicode_escape")
        return ""

    def _missing_config_message(self) -> str:
        provider = self.settings.provider
        if provider == "groq":
            return "Falta GROQ_API_KEY o MOCK_MODE=true. Crea apps/api/.env con LLM_PROVIDER=groq, GROQ_API_KEY=your_groq_key_here, MOCK_MODE=false."
        if provider == "openai":
            return "Falta OPENAI_API_KEY o MOCK_MODE=true. Crea apps/api/.env con LLM_PROVIDER=openai, OPENAI_API_KEY=sk_..., MOCK_MODE=false."
        return f"Proveedor LLM no soportado: {provider}. Usa groq, openai o mock."

    def _parse_json(self, content: str) -> dict[str, Any]:
        source = self._extract_json(content)
        for candidate in [source, self._repair_json(source)]:
            try:
                data = json.loads(candidate)
                return self._normalize_output(data)
            except json.JSONDecodeError:
                continue
        raise ValueError(f"El proveedor devolvió JSON inválido y no pudo repararse: {source[:500]}")

    def _extract_json(self, content: str) -> str:
        content = content.strip()
        if content.startswith("{"):
            return content
        match = re.search(r"\{.*\}", content, re.S)
        if not match:
            raise ValueError(f"El proveedor no devolvió JSON: {content[:500]}")
        return match.group(0)

    def _fallback_from_invalid(self, agent: str, content: str, payload: dict[str, Any], exc: Exception) -> dict[str, Any]:
        title = self._regex_string(content, "title") or f"{agent.replace('_', ' ').title()} recuperado"
        summary = self._regex_string(content, "summary") or self._summary_from_payload(agent, payload)
        items = self._regex_array_strings(content, "items")
        if not items:
            items = self._strings_from_partial(content)[:6]
        if not items:
            items = ["El proveedor devolvió una respuesta incompleta", "Se conservó una vista recuperada para no interrumpir la campaña"]
        return self._normalize_output({
            "title": title,
            "summary": summary,
            "items": items[:8],
            "data": {
                "recovered": True,
                "agent": agent,
                "reason": str(exc)[:240],
                "raw_preview": content[:1400],
                "note": "Salida recuperada automáticamente porque el proveedor devolvió JSON truncado o inválido."
            },
        })

    def _regex_string(self, content: str, key: str) -> str:
        match = re.search(rf'"{re.escape(key)}"\s*:\s*"((?:\\.|[^"\\])*)"', content, re.S)
        if not match:
            return ""
        try:
            return json.loads(f'"{match.group(1)}"')
        except Exception:
            return match.group(1).replace('\\"', '"')

    def _regex_array_strings(self, content: str, key: str) -> list[str]:
        match = re.search(rf'"{re.escape(key)}"\s*:\s*\[(.*?)\]', content, re.S)
        if not match:
            return []
        values = []
        for raw in re.findall(r'"((?:\\.|[^"\\])*)"', match.group(1)):
            try:
                values.append(json.loads(f'"{raw}"'))
            except Exception:
                values.append(raw.replace('\\"', '"'))
        return [v for v in values if v]

    def _strings_from_partial(self, content: str) -> list[str]:
        keys = {"title", "summary", "items", "data", "time", "shot", "action", "screen_text", "audio", "transition"}
        values = []
        for raw in re.findall(r'"((?:\\.|[^"\\])*)"', content):
            value = raw.strip()
            if not value or value in keys or len(value) < 8:
                continue
            if value not in values:
                values.append(value)
        return values

    def _summary_from_payload(self, agent: str, payload: dict[str, Any]) -> str:
        project = payload.get("project") or {}
        brand = project.get("name") or "la marca"
        brief = str(payload.get("brief") or "campaña multimedia")
        return f"Entregable de {agent.replace('_', ' ')} para {brand}. {brief[:180]}"

    def _repair_json(self, source: str) -> str:
        fixed = source.replace("\ufeff", "").strip()
        fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
        fixed = re.sub(r"(?<=\d)\.(?=\d{3}\b)", "", fixed)

        def replace_string_set(match: re.Match) -> str:
            key = match.group(1)
            body = match.group(2).strip()
            if ":" in body:
                return match.group(0)
            items = re.findall(r'"(?:\\.|[^"\\])*"', body)
            return f'"{key}":[{",".join(items)}]'

        fixed = re.sub(r'"([^"]+)"\s*:\s*\{\s*((?:"(?:\\.|[^"\\])*"\s*,?\s*){1,})\s*\}', replace_string_set, fixed)
        return fixed

    def _normalize_output(self, data: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("La salida del agente debe ser un objeto JSON.")
        data.setdefault("title", "Entregable de campaña")
        data.setdefault("summary", "Entregable generado por agente.")
        items = data.get("items") or []
        if isinstance(items, str):
            items = [items]
        data["items"] = [str(item) for item in items if item is not None]
        if not isinstance(data.get("data"), dict):
            data["data"] = {"value": data.get("data")}
        return data

    def _input_text(self, agent: str, instructions: str, payload: dict[str, Any]) -> str:
        schema = {
            "title": "string",
            "summary": "string",
            "items": ["string"],
            "data": {},
        }
        anti_repetition = {
            "research": "No escribas plan, copy ni storyboard; entrega insights y supuestos verificables.",
            "strategy": "No escribas captions; entrega decisiones estratégicas, fases y roles de canal.",
            "copy": "No repitas pilares; entrega textos finales listos para publicar.",
            "storyboard": "No resumas estrategia; entrega escenas producibles con tiempos y recursos.",
            "visual": "No escribas copy largo; entrega dirección de arte, prompts y reglas visuales.",
            "execution_plan": "No propongas ideas nuevas; ordena la producción en semanas, responsables y checklists.",
            "kpis": "No escribas campaña; define medición, eventos, metas y tablero.",
            "brand_review": "No reescribas todo; audita riesgos y mejoras puntuales.",
            "evaluator": "No seas complaciente; justifica el score con fortalezas y debilidades.",
        }.get(agent, "Evita repetir contenido de otros agentes; aporta solo lo que corresponde a tu rol.")
        return "\n".join(
            [
                instructions,
                anti_repetition,
                "Genera una salida profesional, específica, accionable y diferenciada para una demo de portfolio senior.",
                "Mantén la respuesta compacta: máximo 6 items y data con máximo 8 claves principales.",
                "Evita estructuras profundamente anidadas; prefiere arrays simples de strings u objetos pequeños.",
                "Cada item debe ser una decisión o entregable concreto, no una frase genérica.",
                "Usa español claro. Evita repetir el mismo posicionamiento en todas las secciones.",
                "Devuelve solo JSON válido con este esquema exacto:",
                json.dumps(schema, ensure_ascii=False),
                "Reglas JSON estrictas: no Markdown, no comentarios, no trailing commas, no objetos usados como listas.",
                "Si un campo tiene varias frases, usa array de strings. Ejemplo correcto: {'hypotheses':['a','b']}. Ejemplo incorrecto: {'hypotheses':{'a','b'}}.",
                "Usa números sin separadores de miles. Para metas aproximadas prefiere strings como '50k-80k impresiones'.",
                f"Agente: {agent}",
                "Payload compacto:",
                json.dumps(self._compact_payload(payload), ensure_ascii=False, default=str),
            ]
        )


    def _compact_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        keys = ["project", "brief", "channels", "language", "tone", "feedback"]
        compact: dict[str, Any] = {}
        for key in keys:
            if key in payload:
                compact[key] = self._clip_value(payload[key], 700 if key == "brief" else 300)

        context_keys = [
            "normalized", "research", "strategy", "copy", "storyboard", "visual",
            "execution_plan", "kpis", "brand_review", "evaluation", "revision"
        ]
        for key in context_keys:
            value = payload.get(key)
            if isinstance(value, dict):
                compact[key] = {
                    "title": self._clip_value(value.get("title"), 120),
                    "summary": self._clip_value(value.get("summary"), 220),
                    "items": self._clip_value((value.get("items") or [])[:4], 220),
                }

        state = payload.get("state")
        if isinstance(state, dict):
            compact["state"] = {
                key: {
                    "title": self._clip_value((value or {}).get("title"), 100) if isinstance(value, dict) else "",
                    "summary": self._clip_value((value or {}).get("summary"), 160) if isinstance(value, dict) else "",
                    "items": self._clip_value(((value or {}).get("items") or [])[:3], 180) if isinstance(value, dict) else [],
                }
                for key, value in state.items()
            }

        current = payload.get("current")
        if isinstance(current, dict):
            compact["current"] = {
                key: {
                    "title": self._clip_value((value or {}).get("title"), 100) if isinstance(value, dict) else "",
                    "items": self._clip_value(((value or {}).get("items") or [])[:3], 160) if isinstance(value, dict) else [],
                }
                for key, value in current.items()
            }
        return compact

    def _clip_value(self, value: Any, max_chars: int) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            text = " ".join(value.split())
            return text[:max_chars]
        if isinstance(value, list):
            return [self._clip_value(item, max_chars) for item in value[:5]]
        if isinstance(value, dict):
            return {str(key): self._clip_value(val, max_chars) for key, val in list(value.items())[:6]}
        return value

    def _mock(self, agent: str, payload: dict[str, Any]) -> dict[str, Any]:
        brief = str(payload.get("brief") or payload.get("normalized", {}).get("data", {}).get("brief") or "campaña")
        channels = payload.get("channels") or payload.get("normalized", {}).get("data", {}).get("channels") or ["instagram", "tiktok", "landing"]
        project = payload.get("project", {}) or {}
        brand = project.get("name") or "Marca"
        audience = project.get("audience") or "audiencia objetivo"
        base = {
            "title": agent.replace("_", " ").title(),
            "summary": f"Modo demo de {agent} para {brand}: {brief[:160]}",
            "items": [],
            "data": {},
        }
        if agent == "normalizer":
            base["items"] = ["Objetivo claro", "Canales definidos", "Restricciones incorporadas"]
            base["data"] = {"brief": brief, "channels": channels, "audience": audience, "brand": brand, "tone": payload.get("tone", "profesional")}
        elif agent == "research":
            base["items"] = ["El contenido útil supera al genérico", "Los hooks deben mostrar valor temprano", "La prueba social reduce fricción"]
            base["data"] = {"opportunities": ["microvideos", "landing con beneficio único", "email de activación"], "risks": ["claims exagerados", "promesas poco comprobables"]}
        elif agent == "strategy":
            base["items"] = ["Promesa principal: valor visible en menos tiempo", "Pilar 1: claridad", "Pilar 2: progreso", "Pilar 3: comunidad"]
            base["data"] = {"positioning": f"{brand} como solución directa para {audience}", "objectives": ["awareness", "conversion", "retention"], "funnel": {"top": "reels educativos", "middle": "landing", "bottom": "email"}}
        elif agent == "copy":
            base["items"] = ["Hook: deja de improvisar", "CTA: empieza hoy", "Subject: tu plan empieza en 3 minutos"]
            base["data"] = {channel: {"hook": f"Haz que {brand} sea imposible de ignorar", "body": f"Una propuesta clara para {audience}: {brief[:120]}", "cta": "Probar ahora"} for channel in channels}
        elif agent == "storyboard":
            base["items"] = ["0-2s problema", "2-6s transformación", "6-12s demostración", "12-15s CTA"]
            base["data"] = {"scenes": [{"time": "0-2s", "shot": "primer plano", "screen_text": "¿Sigues improvisando?", "audio": "golpe sonoro corto"}, {"time": "2-6s", "shot": "montaje rápido", "screen_text": "Plan claro. Progreso real.", "audio": "beat ascendente"}, {"time": "6-12s", "shot": "captura UI", "screen_text": "Así se ve tu próxima acción", "audio": "voz en off"}, {"time": "12-15s", "shot": "logo y CTA", "screen_text": "Empieza hoy", "audio": "cierre"}]}
        elif agent == "visual":
            base["items"] = ["Estética limpia y energética", "Contraste alto", "Composición centrada en acción"]
            base["data"] = {"palette": ["#0F172A", "#38BDF8", "#F8FAFC", "#A3E635"], "type": "sans bold", "prompts": [f"hero image para {brand}, estilo editorial, alto contraste", f"storyboard vertical para {audience}, energía y claridad"]}
        elif agent == "execution_plan":
            base["items"] = ["Semana 1: territorio creativo y assets base", "Semana 2: producción de piezas cortas", "Semana 3: lanzamiento y emails", "Semana 4: optimización por métricas"]
            base["data"] = {"timeline_weeks": [{"week": 1, "focus": "concepto y arte"}, {"week": 2, "focus": "producción"}, {"week": 3, "focus": "lanzamiento"}, {"week": 4, "focus": "optimización"}], "launch_checklist": ["brief aprobado", "copies finales", "assets exportados", "tracking activo"]}
        elif agent == "kpis":
            base["items"] = ["CTR de landing", "retención de video", "conversiones por canal", "crecimiento de newsletter"]
            base["data"] = {"north_star_metric": "conversiones calificadas", "tracking_events": ["view_content", "click_cta", "lead_submit", "purchase"], "targets": {"ctr": "2-4%", "landing_conversion": "3-8%"}, "dashboard_view": ["canal", "pieza", "costo", "conversión"]}
        elif agent == "brand_review":
            base["items"] = ["Tono consistente", "Claims moderados", "CTA claro"]
            base["data"] = {"risk_level": "low", "fixes": ["mantener promesas verificables", "evitar superlativos absolutos"]}
        elif agent == "reviser":
            base["items"] = ["Copy más específico", "CTA más directo", "Guion con resultado antes del segundo 3"]
            base["data"] = {"changes": ["beneficio reforzado", "ambigüedad reducida", "mejor ajuste a canal"]}
        elif agent == "evaluator":
            base["items"] = ["Claridad alta", "Ajuste multicanal sólido", "Riesgo bajo"]
            base["data"] = {"clarity": 88, "channel_fit": 86, "brand_alignment": 90, "risk": 92, "recommendation": "finish"}
        return base
