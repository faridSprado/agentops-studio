from __future__ import annotations

import io
import json
import textwrap
import zipfile
from typing import Any


SECTION_LABELS = {
    "research": "Investigación",
    "strategy": "Estrategia",
    "copy": "Copy multicanal",
    "storyboard": "Storyboard",
    "visual": "Dirección visual",
    "execution_plan": "Plan de ejecución",
    "kpis": "KPIs y medición",
    "brand_review": "Revisión de marca",
    "evaluation": "Evaluación",
}

SCORE_LABELS = {
    "clarity": "Claridad",
    "brand_alignment": "Ajuste a marca",
    "channel_fit": "Ajuste a canales",
    "creative_depth": "Profundidad creativa",
    "execution_readiness": "Preparación ejecutiva",
    "risk_control": "Control de riesgo",
    "overall": "Score final",
}


def campaign_markdown(output: dict[str, Any]) -> str:
    lines = [f"# {output.get('title', 'Campaña multimedia')}", "", output.get("summary", ""), ""]
    lines.extend(["## Estado técnico", "", f"- Provider: {output.get('provider', '')}", f"- Mock: {output.get('mock_mode', '')}", f"- Score: {output.get('score', '')}", ""])
    lines.extend(["## Resumen ejecutivo", ""])
    for item in output.get("executive", []) or []:
        lines.extend([f"### {item.get('label', '')}", "", item.get("summary", ""), ""])
        for bullet in item.get("items", []) or []:
            lines.append(f"- {bullet}")
        lines.append("")
    lines.extend(["## Brief", "", output.get("brief", ""), ""])
    lines.extend(["## Canales", "", ", ".join(output.get("channels", [])), ""])
    lines.extend(["## Evaluación", ""])
    for key, value in (output.get("score_breakdown") or {}).items():
        if key == "recommendation":
            continue
        lines.append(f"- {SCORE_LABELS.get(key, key)}: {value}")
    rationale = output.get("score_rationale") or {}
    if rationale:
        lines.extend(["", "### Justificación", ""])
        for value in rationale.values():
            lines.append(f"- {value}")
    lines.append("")
    sections = output.get("sections", {}) or {}
    for name, section in sections.items():
        label = SECTION_LABELS.get(name, name.replace("_", " ").title())
        lines.extend([f"## {label}", "", section.get("summary", "") if isinstance(section, dict) else str(section), ""])
        if isinstance(section, dict):
            for item in section.get("items", []):
                lines.append(f"- {item}")
            if section.get("data"):
                lines.extend(["", "```json", json.dumps(section["data"], ensure_ascii=False, indent=2), "```", ""])
    return "\n".join(lines).strip() + "\n"


def campaign_json(output: dict[str, Any]) -> bytes:
    return json.dumps(output, ensure_ascii=False, indent=2).encode("utf-8")


def campaign_pdf(output: dict[str, Any]) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception as exc:
        raise RuntimeError("Instala reportlab con: pip install reportlab") from exc

    buffer = io.BytesIO()
    page_width, page_height = A4
    pdf = canvas.Canvas(buffer, pagesize=A4)
    margin = 48
    y = page_height - margin

    def write(text: str, size: int = 10, bold: bool = False, gap: int = 14) -> None:
        nonlocal y
        font = "Helvetica-Bold" if bold else "Helvetica"
        pdf.setFont(font, size)
        for raw_line in str(text or "").splitlines() or [""]:
            for line in textwrap.wrap(raw_line, width=92) or [""]:
                if y < margin:
                    pdf.showPage()
                    y = page_height - margin
                    pdf.setFont(font, size)
                pdf.drawString(margin, y, line.encode("latin-1", "replace").decode("latin-1"))
                y -= gap

    write(output.get("title", "Campaña multimedia"), 18, True, 22)
    write(output.get("summary", ""), 10, False, 14)
    y -= 8
    write("Score y calidad", 13, True, 18)
    for key, value in (output.get("score_breakdown") or {}).items():
        if key != "recommendation":
            write(f"{SCORE_LABELS.get(key, key)}: {value}")
    for value in (output.get("score_rationale") or {}).values():
        write(f"- {value}")
    y -= 8
    write("Resumen ejecutivo", 13, True, 18)
    for item in output.get("executive", []) or []:
        write(item.get("label", ""), 11, True, 15)
        write(item.get("summary", ""), 10, False, 14)
        for bullet in item.get("items", []) or []:
            write(f"- {bullet}")
        y -= 4
    y -= 8
    write("Entregables por agente", 13, True, 18)
    for name, section in (output.get("sections") or {}).items():
        if not isinstance(section, dict):
            continue
        write(SECTION_LABELS.get(name, name), 11, True, 15)
        write(section.get("summary", ""), 10, False, 14)
        for bullet in (section.get("items") or [])[:8]:
            write(f"- {bullet}")
        y -= 4
    pdf.save()
    return buffer.getvalue()


def campaign_zip(output: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    sections = output.get("sections", {}) or {}
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("campaign.json", campaign_json(output))
        archive.writestr("campaign.md", campaign_markdown(output))
        archive.writestr("readme.txt", "Entregables generados por Multimedia AgentOps Studio. Abrir campaign.md para la version ejecutiva y campaign.json para la salida tecnica.\n")
        try:
            archive.writestr("campaign.pdf", campaign_pdf(output))
        except Exception:
            pass
        for key, section in sections.items():
            if section:
                safe = key.replace("_", "-")
                archive.writestr(f"sections/{safe}.json", json.dumps(section, ensure_ascii=False, indent=2))
    return buffer.getvalue()
