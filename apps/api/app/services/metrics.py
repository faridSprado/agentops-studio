from __future__ import annotations

from typing import Any


METRIC_KEYS = ["clarity", "brand_alignment", "channel_fit", "creative_depth", "execution_readiness", "risk_control"]


def score_breakdown(state: dict[str, Any]) -> dict[str, int | str]:
    sections = {name: state.get(name) or {} for name in ["research", "strategy", "copy", "storyboard", "visual", "execution_plan", "kpis", "brand_review"]}
    channels = state.get("channels") or []
    copy_data = _data(sections["copy"])
    plan_data = _data(sections["execution_plan"])
    kpi_data = _data(sections["kpis"])
    brand_data = _data(sections["brand_review"])

    clarity = _metric(66, sections["strategy"], sections["copy"], max_bonus=24)
    brand_alignment = _metric(66, sections["strategy"], sections["visual"], sections["brand_review"], max_bonus=24)
    channel_fit = 64 + min(_channel_hits(channels, copy_data) * 5, 20) + min(len(channels), 5)
    creative_depth = _metric(62, sections["research"], sections["storyboard"], sections["visual"], max_bonus=26)
    execution_readiness = _metric(62, sections["copy"], sections["storyboard"], sections["execution_plan"], sections["kpis"], max_bonus=30)
    risk_control = 86

    if plan_data.get("launch_checklist"):
        execution_readiness += 3
    if kpi_data.get("tracking_events") or kpi_data.get("targets"):
        execution_readiness += 3
    if kpi_data.get("conversion_kpis"):
        channel_fit += 2

    risk = str(brand_data.get("risk_level") or brand_data.get("risk") or "low").lower()
    if "high" in risk or "alto" in risk:
        risk_control = 60
    elif "medium" in risk or "medio" in risk:
        risk_control = 74
    elif brand_data.get("approval_status") and "approve" not in str(brand_data.get("approval_status")).lower() and "aprob" not in str(brand_data.get("approval_status")).lower():
        risk_control = 78

    values = {
        "clarity": _cap(clarity),
        "brand_alignment": _cap(brand_alignment),
        "channel_fit": _cap(channel_fit),
        "creative_depth": _cap(creative_depth),
        "execution_readiness": _cap(execution_readiness),
        "risk_control": _cap(risk_control),
    }
    overall = round(sum(int(values[key]) for key in METRIC_KEYS) / len(METRIC_KEYS))
    values["overall"] = _cap(overall)
    values["recommendation"] = "revise" if int(values["overall"]) < 84 else "finish"
    return values


def score_rationale(values: dict[str, Any]) -> dict[str, str]:
    overall = int(values.get("overall") or 0)
    readiness = int(values.get("execution_readiness") or 0)
    depth = int(values.get("creative_depth") or 0)
    risk = int(values.get("risk_control") or 0)
    return {
        "summary": _overall_text(overall),
        "execution": "Lista para una primera ronda de producción." if readiness >= 86 else "Requiere aterrizar responsables, fechas o piezas finales antes de producir.",
        "creative_depth": "La idea creativa tiene suficiente diferenciación para demo." if depth >= 84 else "Conviene fortalecer insight, tensión o territorio visual.",
        "risk": "Riesgo bajo si se mantienen claims verificables." if risk >= 84 else "Revisar promesas, tono o cumplimiento antes de publicar.",
    }


def score_state(state: dict[str, Any]) -> int:
    return int(score_breakdown(state)["overall"])


def _metric(base: int, *sections: dict[str, Any], max_bonus: int) -> int:
    bonus = 0
    for section in sections:
        if not isinstance(section, dict):
            continue
        if section.get("summary"):
            bonus += 3
        items = section.get("items") or []
        data = section.get("data") or {}
        bonus += min(len(items), 5) * 2
        bonus += min(len(data.keys()), 7)
    return base + min(bonus, max_bonus)


def _channel_hits(channels: list[str], data: dict[str, Any]) -> int:
    text = " ".join([str(key).lower() for key in data.keys()] + [str(data).lower()])
    return sum(1 for channel in set(channels) if channel.lower() in text)


def _data(section: dict[str, Any]) -> dict[str, Any]:
    return section.get("data") or {} if isinstance(section, dict) else {}


def _overall_text(score: int) -> str:
    if score >= 90:
        return "Campaña sólida, diferenciada y preparada para presentarse como demo profesional."
    if score >= 84:
        return "Campaña viable para portfolio; requiere pulido menor antes de producción real."
    if score >= 76:
        return "Campaña prometedora, pero necesita revisión antes de mostrarse como entregable final."
    return "Campaña incompleta; requiere una iteración adicional."


def _cap(value: int | float) -> int:
    return max(0, min(96, int(round(value))))
