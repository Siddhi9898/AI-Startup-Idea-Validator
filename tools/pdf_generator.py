"""
tools/pdf_generator.py
--------------------------
Renders the validation report as an ACTUAL PDF file (fixes: "report
should be in PDF, not md, for better reference"). Previously the
"Download Report" buttons just handed back the raw Markdown string
with a .md extension - this module turns that same structured data
into a real, nicely formatted .pdf using reportlab.

Deterministic, no LLM involved: this is pure formatting of data that
every other agent has already produced.
"""

import io
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle, HRFlowable,
)
from reportlab.lib.enums import TA_LEFT


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", fontSize=20, leading=24, spaceAfter=6,
        textColor=colors.HexColor("#4C1D95"), fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading", fontSize=14, leading=18, spaceBefore=16, spaceAfter=8,
        textColor=colors.HexColor("#6D28D9"), fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="ReportBody", fontSize=10.5, leading=15, spaceAfter=6,
        alignment=TA_LEFT, fontName="Helvetica",
    ))
    styles.add(ParagraphStyle(
        name="ReportBullet", fontSize=10.5, leading=14, fontName="Helvetica",
    ))
    styles.add(ParagraphStyle(
        name="Caption", fontSize=9, leading=12, textColor=colors.grey, fontName="Helvetica-Oblique",
    ))
    return styles


def _sanitize_text(text: str) -> str:
    """
    Fixes: "the PDF should be clear and understandable, no dark spots."
    Those dark spots are "tofu" boxes - the base PDF font (Helvetica,
    WinAnsi-encoded) has no glyph for characters outside the
    Windows-1252 codepage, so any emoji or exotic symbol an LLM
    happens to add (checkmarks, arrows, stars, etc.) renders as a
    solid black rectangle instead of the intended character. This
    strips anything the font can't actually display, so nothing ever
    renders as a dark box - readable plain text only.
    """
    if not text:
        return ""
    # A few common LLM-added symbols get a readable plain-text
    # substitute instead of being silently dropped.
    replacements = {
        "\u2192": "->", "\u2190": "<-", "\u2794": "->",
        "\u2705": "", "\u2714": "", "\u274c": "", "\u2716": "",
        "\u2b50": "", "\u2b50\ufe0f": "",
        "\U0001F680": "", "\U0001F4A1": "", "\U0001F525": "",
        "\u26a0\ufe0f": "Warning: ", "\u26a0": "Warning: ",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    # Final safety net: drop any character the PDF's base font truly
    # cannot represent (WinAnsi/cp1252), rather than let it render as
    # a black box. cp1252 already covers standard punctuation,
    # accented Latin letters, em/en dashes, curly quotes, bullets.
    return text.encode("cp1252", errors="ignore").decode("cp1252")


def _escape(text: str) -> str:
    text = _sanitize_text(text or "")
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _score_color(score) -> colors.Color:
    try:
        score = float(score)
    except (TypeError, ValueError):
        return colors.grey
    if score >= 75:
        return colors.HexColor("#15803D")
    if score >= 55:
        return colors.HexColor("#B45309")
    return colors.HexColor("#B91C1C")


def build_report_pdf(state_dict: dict, qa_history: list = None) -> bytes:
    """
    Builds a polished, multi-section PDF directly from the shared
    pipeline state dict (same data the Markdown report and every
    Streamlit tab already use) - so the PDF and the on-screen report
    can never drift out of sync with each other.

    qa_history: optional list of {"role": "user"/"assistant",
    "content": str} - the advisor chat for this idea (fixes: "save
    the chat history in the PDF under the title Q & A"). Pass None
    or [] to omit the section entirely.
    """
    extracted = state_dict.get("extracted", {})
    viability = state_dict.get("viability_score", {})
    market = state_dict.get("market_analysis", {})
    competitors = state_dict.get("competitors", {})
    swot = state_dict.get("swot", {})
    mvp = state_dict.get("mvp", {})
    gtm = state_dict.get("gtm", {})
    pitch = state_dict.get("elevator_pitch", {})
    funding = state_dict.get("funding_suggestions", [])
    blind_spots = state_dict.get("blind_spots", [])
    improvement_suggestions = state_dict.get("improvement_suggestions", [])
    log = state_dict.get("execution_log", [])

    styles = _styles()
    story = []

    idea_name = extracted.get("idea_name", "Untitled Idea") or "Untitled Idea"
    story.append(Paragraph("Startup Validation Report", styles["ReportTitle"]))
    story.append(Paragraph(_escape(idea_name), styles["Caption"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#D8B4FE"), spaceAfter=10))

    # Quick Summary
    story.append(Paragraph("Quick Summary", styles["SectionHeading"]))
    story.append(Paragraph(_escape(state_dict.get("quick_summary", "")), styles["ReportBody"]))

    # Suggestions to improve
    if improvement_suggestions:
        story.append(Paragraph("Suggestions to Improve This Idea", styles["SectionHeading"]))
        story.append(ListFlowable(
            [ListItem(Paragraph(_escape(s), styles["ReportBullet"])) for s in improvement_suggestions],
            bulletType="bullet",
        ))

    # Executive Summary / honest take
    story.append(Paragraph("Executive Summary", styles["SectionHeading"]))
    story.append(Paragraph(_escape(state_dict.get("honest_summary", "")), styles["ReportBody"]))

    # Idea
    story.append(Paragraph("Startup Idea", styles["SectionHeading"]))
    idea_rows = [
        ["Name", extracted.get("idea_name", "")],
        ["Problem", extracted.get("problem", "")],
        ["Solution", extracted.get("solution", "")],
        ["Target Customer", extracted.get("target_customer", "")],
        ["Industry", extracted.get("industry", "")],
        ["Business Model", extracted.get("business_model", "")],
        ["Location", extracted.get("location", "")],
    ]
    idea_table = Table(
        [[Paragraph(f"<b>{_escape(k)}</b>", styles["ReportBody"]), Paragraph(_escape(str(v)), styles["ReportBody"])]
         for k, v in idea_rows],
        colWidths=[1.4 * inch, 4.6 * inch],
    )
    idea_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F5F3FF")),
    ]))
    story.append(idea_table)

    # Viability
    story.append(Paragraph("Viability Score", styles["SectionHeading"]))
    score = viability.get("overall_score", "N/A")
    score_style = ParagraphStyle(
        "ScoreLine", parent=styles["ReportBody"], fontSize=16, fontName="Helvetica-Bold",
        textColor=_score_color(score),
    )
    story.append(Paragraph(f"{score}/100 &mdash; {_escape(viability.get('verdict', ''))}", score_style))
    breakdown = viability.get("breakdown", {})
    if breakdown:
        bd_items = [f"{k.replace('_', ' ').title()}: {v}/10" for k, v in breakdown.items()]
        story.append(ListFlowable(
            [ListItem(Paragraph(_escape(item), styles["ReportBullet"])) for item in bd_items],
            bulletType="bullet",
        ))

    # Market Analysis
    story.append(Paragraph("Market Analysis", styles["SectionHeading"]))
    story.append(Paragraph(f"<b>Growth Trend:</b> {_escape(market.get('growth_trend', 'Not yet analyzed'))}", styles["ReportBody"]))
    segments = ", ".join(market.get("customer_segments", [])) or "Not yet analyzed"
    story.append(Paragraph(f"<b>Customer Segments:</b> {_escape(segments)}", styles["ReportBody"]))
    dq = market.get("data_quality", {})
    if dq:
        story.append(Paragraph(
            f"<b>Data Quality:</b> {dq.get('relevant_count', 0)} relevant result(s) of {dq.get('total_count', 0)} retrieved",
            styles["ReportBody"],
        ))

    # Competitors
    story.append(Paragraph("Competitor Analysis", styles["SectionHeading"]))
    comp_list = competitors.get("competitors", [])
    if comp_list:
        story.append(ListFlowable(
            [ListItem(Paragraph(
                f"<b>{_escape(c.get('name', ''))}</b> &mdash; Strength: {_escape(c.get('strength', ''))} | "
                f"Weakness: {_escape(c.get('weakness', ''))}", styles["ReportBullet"]
            )) for c in comp_list],
            bulletType="bullet",
        ))
    story.append(Paragraph(f"<b>Market Gap:</b> {_escape(competitors.get('market_gap', 'Not yet analyzed'))}", styles["ReportBody"]))

    # SWOT
    story.append(Paragraph("SWOT &amp; Risk Analysis", styles["SectionHeading"]))
    for label, key in [("Strengths", "strengths"), ("Weaknesses", "weaknesses"),
                        ("Opportunities", "opportunities"), ("Threats", "threats")]:
        items = swot.get(key, [])
        story.append(Paragraph(f"<b>{label}:</b>", styles["ReportBody"]))
        if items:
            story.append(ListFlowable(
                [ListItem(Paragraph(_escape(i), styles["ReportBullet"])) for i in items],
                bulletType="bullet",
            ))
        else:
            story.append(Paragraph("Not yet analyzed", styles["ReportBody"]))
    story.append(Paragraph(f"<b>Risk Score:</b> {swot.get('risk_score', 'N/A')}/10", styles["ReportBody"]))

    # MVP
    story.append(Paragraph("MVP Recommendation (MoSCoW)", styles["SectionHeading"]))
    mvp_features = mvp.get("mvp_features", [])
    if mvp_features:
        story.append(ListFlowable(
            [ListItem(Paragraph(f"[{_escape(f.get('priority', ''))}] {_escape(f.get('feature', ''))}", styles["ReportBullet"]))
             for f in mvp_features],
            bulletType="bullet",
        ))
    story.append(Paragraph(f"<b>Timeline:</b> {_escape(mvp.get('estimated_timeline', 'Not yet analyzed'))}", styles["ReportBody"]))

    # GTM
    story.append(Paragraph("Go-To-Market Strategy", styles["SectionHeading"]))
    story.append(Paragraph(_escape(gtm.get("positioning_statement", "Not yet analyzed")), styles["ReportBody"]))
    story.append(Paragraph(f"<b>Channels:</b> {_escape(', '.join(gtm.get('marketing_channels', [])))}", styles["ReportBody"]))
    story.append(Paragraph(f"<b>Pricing:</b> {_escape(gtm.get('pricing_strategy', ''))}", styles["ReportBody"]))

    # Blind spots
    story.append(Paragraph("Blind Spots to Consider", styles["SectionHeading"]))
    if blind_spots:
        story.append(ListFlowable(
            [ListItem(Paragraph(_escape(q), styles["ReportBullet"])) for q in blind_spots],
            bulletType="bullet",
        ))

    # Elevator pitch
    story.append(Paragraph("Elevator Pitch", styles["SectionHeading"]))
    story.append(Paragraph(_escape(pitch.get("elevator_pitch", "")), styles["ReportBody"]))
    if pitch.get("tagline"):
        story.append(Paragraph(f"<i>{_escape(pitch.get('tagline', ''))}</i>", styles["ReportBody"]))

    # Funding
    story.append(Paragraph("Suggested Funding Paths", styles["SectionHeading"]))
    if funding:
        story.append(ListFlowable(
            [ListItem(Paragraph(
                f"<b>{_escape(f.get('funding_type', ''))}:</b> {_escape(f.get('reason', ''))}", styles["ReportBullet"]
            )) for f in funding],
            bulletType="bullet",
        ))

    # Q & A (advisor chat history)
    if qa_history:
        story.append(Paragraph("Q &amp; A", styles["SectionHeading"]))
        for msg in qa_history:
            if msg.get("role") not in ("user", "assistant"):
                continue
            label = "Q" if msg["role"] == "user" else "A"
            story.append(Paragraph(f"<b>{label}:</b> {_escape(msg.get('content', ''))}", styles["ReportBody"]))

    # Execution log
    if log:
        story.append(Paragraph("Pipeline Execution Log", styles["SectionHeading"]))
        log_lines = [
            f"{entry['step']}: {'OK' if entry['is_valid'] else 'VALIDATION ISSUE'}"
            + (f" ({entry['note']})" if entry.get("note") else "")
            for entry in log
        ]
        story.append(ListFlowable(
            [ListItem(Paragraph(_escape(line), styles["ReportBullet"])) for line in log_lines],
            bulletType="bullet",
        ))

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Generated by AI Startup Idea Validator", styles["Caption"]))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=LETTER,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        title=f"Validation Report - {idea_name}",
    )
    doc.build(story)
    return buffer.getvalue()
