"""
PDF Report Generator
---------------------
Builds a professional, multi-page PDF version of the validation
report (replaces the old plain Markdown download). This reads
directly from the same structured state_dict every other agent
already produces - no LLM call, no new data, purely presentation -
so a founder can hand this PDF to a mentor or investor and it reads
like a real report: a cover page, section headings, real tables for
the score breakdown / competitors / MVP features / funding paths,
and a consistent visual style, instead of a wall of raw Markdown
text.

Usage:
    from tools.pdf_report_generator import generate_pdf_report
    pdf_bytes = generate_pdf_report(result)   # result = the pipeline's state_dict
    st.download_button(..., data=pdf_bytes, mime="application/pdf")
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, ListFlowable, ListItem, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ---------------------------------------------------------------------
# Brand palette - mirrors the app's dark purple / green theme so the
# PDF feels like it came from the same product, not a generic export.
# ---------------------------------------------------------------------
PURPLE = colors.HexColor("#6D28D9")
PURPLE_LIGHT = colors.HexColor("#EDE9FE")
GREEN = colors.HexColor("#059669")
GREEN_LIGHT = colors.HexColor("#D1FAE5")
DARK = colors.HexColor("#1F2937")
GRAY = colors.HexColor("#6B7280")
GRAY_LIGHT = colors.HexColor("#F3F4F6")
RED = colors.HexColor("#DC2626")


def _styles():
    base = getSampleStyleSheet()
    styles = {
        "CoverTitle": ParagraphStyle(
            "CoverTitle", parent=base["Title"], fontSize=28, leading=34,
            textColor=DARK, alignment=TA_CENTER, spaceAfter=6,
        ),
        "CoverSubtitle": ParagraphStyle(
            "CoverSubtitle", parent=base["Normal"], fontSize=14, leading=18,
            textColor=PURPLE, alignment=TA_CENTER, spaceAfter=4,
        ),
        "CoverMeta": ParagraphStyle(
            "CoverMeta", parent=base["Normal"], fontSize=10, leading=14,
            textColor=GRAY, alignment=TA_CENTER,
        ),
        "SectionHeading": ParagraphStyle(
            "SectionHeading", parent=base["Heading1"], fontSize=16, leading=20,
            textColor=colors.white, backColor=PURPLE, spaceBefore=14, spaceAfter=10,
            leftIndent=8, borderPadding=(6, 6, 6, 6),
        ),
        "SubHeading": ParagraphStyle(
            "SubHeading", parent=base["Heading2"], fontSize=12.5, leading=16,
            textColor=PURPLE, spaceBefore=10, spaceAfter=6,
        ),
        "Body": ParagraphStyle(
            "Body", parent=base["Normal"], fontSize=10.5, leading=15,
            textColor=DARK, alignment=TA_LEFT, spaceAfter=6,
        ),
        "BodyMuted": ParagraphStyle(
            "BodyMuted", parent=base["Normal"], fontSize=10, leading=14,
            textColor=GRAY, fontName="Helvetica-Oblique",
        ),
        "Bullet": ParagraphStyle(
            "Bullet", parent=base["Normal"], fontSize=10.5, leading=15,
            textColor=DARK,
        ),
        "ScoreBig": ParagraphStyle(
            "ScoreBig", parent=base["Normal"], fontSize=40, leading=44,
            textColor=PURPLE, alignment=TA_CENTER, fontName="Helvetica-Bold",
        ),
        "VerdictTag": ParagraphStyle(
            "VerdictTag", parent=base["Normal"], fontSize=12, leading=16,
            textColor=GREEN, alignment=TA_CENTER, fontName="Helvetica-Bold",
        ),
        "TableHeader": ParagraphStyle(
            "TableHeader", parent=base["Normal"], fontSize=9.5, leading=12,
            textColor=colors.white, fontName="Helvetica-Bold",
        ),
        "TableCell": ParagraphStyle(
            "TableCell", parent=base["Normal"], fontSize=9.5, leading=13,
            textColor=DARK,
        ),
    }
    return styles


def _section_header(text, styles):
    return Paragraph(text, styles["SectionHeading"])


def _bullets(items, styles, empty_text="Not yet determined"):
    items = [i for i in (items or []) if i]
    if not items:
        return Paragraph(empty_text, styles["BodyMuted"])
    return ListFlowable(
        [ListItem(Paragraph(str(i), styles["Bullet"]), leftIndent=6) for i in items],
        bulletType="bullet", start="circle", leftIndent=14, spaceBefore=2, spaceAfter=2,
    )


def _table(data, col_widths, styles, header_bg=PURPLE):
    """Builds a styled table; data[0] is treated as the header row."""
    wrapped = [[Paragraph(str(c), styles["TableHeader"]) for c in data[0]]]
    for row in data[1:]:
        wrapped.append([Paragraph(str(c) if c not in (None, "") else "-", styles["TableCell"]) for c in row])
    t = Table(wrapped, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRAY_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def _footer_header(canvas_obj, doc, idea_name):
    canvas_obj.saveState()
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(GRAY)
    canvas_obj.drawString(0.75 * inch, 0.5 * inch, f"AI Startup Idea Validator - {idea_name}")
    canvas_obj.drawRightString(LETTER[0] - 0.75 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas_obj.setStrokeColor(colors.HexColor("#E5E7EB"))
    canvas_obj.line(0.75 * inch, 0.62 * inch, LETTER[0] - 0.75 * inch, 0.62 * inch)
    canvas_obj.restoreState()


def generate_pdf_report(state_dict: dict) -> bytes:
    """
    Builds the full professional PDF report from the pipeline's
    state_dict and returns it as raw bytes, ready for
    st.download_button(..., mime="application/pdf").
    """
    styles = _styles()
    buffer = io.BytesIO()

    extracted = state_dict.get("extracted", {}) or {}
    viability = state_dict.get("viability_score", {}) or {}
    market = state_dict.get("market_analysis", {}) or {}
    competitors_data = state_dict.get("competitors", {}) or {}
    swot = state_dict.get("swot", {}) or {}
    mvp = state_dict.get("mvp", {}) or {}
    gtm = state_dict.get("gtm", {}) or {}
    elevator = state_dict.get("elevator_pitch", {}) or {}
    funding = state_dict.get("funding_suggestions", []) or []
    blind_spots = state_dict.get("blind_spots", []) or []
    log = state_dict.get("execution_log", []) or []

    idea_name = extracted.get("idea_name", "Untitled Idea")

    doc = SimpleDocTemplate(
        buffer, pagesize=LETTER,
        topMargin=0.85 * inch, bottomMargin=0.85 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        title=f"{idea_name} - Validation Report",
    )

    story = []

    # ---------------- Cover Page ----------------
    story.append(Spacer(1, 1.4 * inch))
    story.append(Paragraph("Startup Validation Report", styles["CoverTitle"]))
    story.append(Paragraph(idea_name, styles["CoverSubtitle"]))
    if elevator.get("tagline"):
        story.append(Paragraph(f"\u201c{elevator['tagline']}\u201d", styles["BodyMuted"]))
    story.append(Spacer(1, 0.4 * inch))

    score = viability.get("overall_score", "N/A")
    verdict = viability.get("verdict", "")
    story.append(Paragraph(f"{score}/100", styles["ScoreBig"]))
    if verdict:
        story.append(Paragraph(verdict.upper(), styles["VerdictTag"]))
    story.append(Spacer(1, 0.6 * inch))

    meta_lines = [
        f"Industry: {extracted.get('industry', 'N/A')}",
        f"Target Customer: {extracted.get('target_customer', 'N/A')}",
        f"Generated: {datetime.now().strftime('%B %d, %Y')}",
    ]
    for line in meta_lines:
        story.append(Paragraph(line, styles["CoverMeta"]))

    story.append(PageBreak())

    # ---------------- Executive Summary ----------------
    story.append(_section_header("Executive Summary", styles))
    honest_summary = state_dict.get("honest_summary", "") or "Not yet analyzed."
    story.append(Paragraph(honest_summary, styles["Body"]))
    story.append(Spacer(1, 8))

    # ---------------- Startup Idea ----------------
    story.append(_section_header("Startup Idea", styles))
    idea_rows = [
        ["Field", "Details"],
        ["Problem", extracted.get("problem", "N/A")],
        ["Solution", extracted.get("solution", "N/A")],
        ["Target Customer", extracted.get("target_customer", "N/A")],
        ["Industry", extracted.get("industry", "N/A")],
        ["Business Model", extracted.get("business_model", "N/A")],
    ]
    story.append(_table(idea_rows, [1.6 * inch, 4.4 * inch], styles))
    story.append(Spacer(1, 10))

    # ---------------- Viability Score ----------------
    story.append(_section_header("Viability Score Breakdown", styles))
    breakdown = viability.get("breakdown", {}) or {}
    score_rows = [["Dimension", "Score (out of 10)"]]
    label_map = {
        "idea_clarity": "Idea Clarity",
        "competition_density": "Competition Density",
        "market_analysis": "Market Analysis",
        "swot_risk": "SWOT / Risk",
    }
    for key, label in label_map.items():
        if key in breakdown:
            score_rows.append([label, breakdown[key]])
    if len(score_rows) > 1:
        story.append(_table(score_rows, [3 * inch, 3 * inch], styles))
    else:
        story.append(Paragraph("Score breakdown not available.", styles["BodyMuted"]))
    story.append(Spacer(1, 10))

    # ---------------- Market Analysis ----------------
    story.append(_section_header("Market Analysis", styles))
    story.append(Paragraph(f"<b>Market Size Score:</b> {market.get('market_size_score', 'N/A')}/10", styles["Body"]))
    story.append(Paragraph(f"<b>Growth Trend:</b> {market.get('growth_trend', 'Not yet analyzed')}", styles["Body"]))
    story.append(Paragraph("<b>Customer Segments:</b>", styles["Body"]))
    story.append(_bullets(market.get("customer_segments", []), styles))
    dq = market.get("data_quality", {}) or {}
    if dq:
        story.append(Paragraph(
            f"<i>Based on {dq.get('relevant_count', 0)} relevant result(s) out of {dq.get('total_count', 0)} retrieved.</i>",
            styles["BodyMuted"],
        ))
    story.append(Spacer(1, 10))

    # ---------------- Competitor Analysis ----------------
    story.append(_section_header("Competitor Analysis", styles))
    comp_list = competitors_data.get("competitors", [])
    story.append(Paragraph(f"<b>Competitive Intensity:</b> {competitors_data.get('competitive_intensity', 'unknown')}", styles["Body"]))
    story.append(Paragraph(f"<b>Market Gap:</b> {competitors_data.get('market_gap', 'Not yet analyzed')}", styles["Body"]))
    story.append(Spacer(1, 6))
    if comp_list:
        comp_rows = [["Competitor", "Strength", "Weakness"]]
        for c in comp_list:
            comp_rows.append([c.get("name", "N/A"), c.get("strength", "N/A"), c.get("weakness", "N/A")])
        story.append(_table(comp_rows, [1.5 * inch, 2.25 * inch, 2.25 * inch], styles))
    else:
        story.append(Paragraph("No specific competitors identified from retrieved data.", styles["BodyMuted"]))
    story.append(Spacer(1, 10))

    # ---------------- SWOT ----------------
    story.append(_section_header("SWOT Analysis", styles))
    swot_pairs = [
        ("Strengths", swot.get("strengths", []), GREEN),
        ("Weaknesses", swot.get("weaknesses", []), RED),
        ("Opportunities", swot.get("opportunities", []), PURPLE),
        ("Threats", swot.get("threats", []), RED),
    ]
    for label, items, color in swot_pairs:
        story.append(Paragraph(label, ParagraphStyle("SwotLabel", parent=styles["SubHeading"], textColor=color)))
        story.append(_bullets(items, styles))
    story.append(Paragraph(f"<b>Risk Score:</b> {swot.get('risk_score', 'N/A')}/10", styles["Body"]))
    story.append(Spacer(1, 10))

    # ---------------- MVP ----------------
    story.append(_section_header("MVP Recommendation (MoSCoW)", styles))
    mvp_features = mvp.get("mvp_features", [])
    if mvp_features:
        mvp_rows = [["Priority", "Feature"]]
        for f in mvp_features:
            mvp_rows.append([f.get("priority", "N/A"), f.get("feature", "N/A")])
        story.append(_table(mvp_rows, [1.3 * inch, 4.7 * inch], styles))
    else:
        story.append(Paragraph("No MVP features determined.", styles["BodyMuted"]))
    story.append(Paragraph(f"<b>Estimated Timeline:</b> {mvp.get('estimated_timeline', 'Not yet analyzed')}", styles["Body"]))
    story.append(Spacer(1, 10))

    # ---------------- GTM ----------------
    story.append(_section_header("Go-To-Market Strategy", styles))
    story.append(Paragraph(gtm.get("positioning_statement", "Not yet analyzed"), styles["Body"]))
    story.append(Paragraph("<b>Marketing Channels:</b>", styles["Body"]))
    story.append(_bullets(gtm.get("marketing_channels", []), styles))
    story.append(Paragraph(f"<b>Pricing Strategy:</b> {gtm.get('pricing_strategy', 'Not yet analyzed')}", styles["Body"]))
    story.append(Spacer(1, 10))

    # ---------------- Blind Spots ----------------
    story.append(_section_header("What You Might Be Missing", styles))
    story.append(_bullets(blind_spots, styles, empty_text="No blind spots flagged."))
    story.append(Spacer(1, 10))

    # ---------------- Elevator Pitch ----------------
    story.append(_section_header("Elevator Pitch", styles))
    story.append(Paragraph(elevator.get("elevator_pitch", "Not yet generated."), styles["Body"]))
    if elevator.get("tagline"):
        story.append(Paragraph(f"<i>\u201c{elevator['tagline']}\u201d</i>", styles["BodyMuted"]))
    story.append(Spacer(1, 10))

    # ---------------- Funding Paths ----------------
    story.append(_section_header("Suggested Funding Paths", styles))
    if funding:
        fund_rows = [["Funding Type", "Reason"]]
        for f in funding:
            fund_rows.append([f.get("funding_type", "N/A"), f.get("reason", "N/A")])
        story.append(_table(fund_rows, [1.8 * inch, 4.2 * inch], styles))
    else:
        story.append(Paragraph("No funding suggestions available.", styles["BodyMuted"]))
    story.append(Spacer(1, 10))

    # ---------------- Pipeline Execution Log ----------------
    if log:
        story.append(_section_header("Pipeline Execution Log", styles))
        log_rows = [["Step", "Status", "Note"]]
        for entry in log:
            status = "OK" if entry.get("is_valid") else "VALIDATION ISSUE"
            log_rows.append([entry.get("step", ""), status, entry.get("note", "") or "-"])
        story.append(_table(log_rows, [2 * inch, 1.4 * inch, 2.6 * inch], styles, header_bg=DARK))

    def _on_page(canvas_obj, doc_obj):
        _footer_header(canvas_obj, doc_obj, idea_name)

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    buffer.seek(0)
    return buffer.getvalue()
