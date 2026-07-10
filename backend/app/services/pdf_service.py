import io
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

PINE = HexColor("#1A5B4A")
BRASS = HexColor("#B8915A")
CHARCOAL = HexColor("#2C2420")
STONE = HexColor("#8B7E74")
CREAM = HexColor("#FCF8F3")
WHITE = colors.white


async def generate_assessment_pdf(report: dict, user_profile: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        textColor=PINE,
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=STONE,
        spaceAfter=20,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=CHARCOAL,
        spaceBefore=16,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=CHARCOAL,
        leading=16,
        spaceAfter=6,
    )
    label_style = ParagraphStyle(
        "LabelStyle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=STONE,
        spaceAfter=2,
    )
    value_style = ParagraphStyle(
        "ValueStyle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=CHARCOAL,
        fontName="Helvetica-Bold",
        spaceAfter=10,
    )

    elements = []

    elements.append(Paragraph("MindGuard", title_style))
    elements.append(Paragraph("AI-Powered Mental Wellness Report", subtitle_style))

    # Divider
    divider_data = [[""]]
    divider_table = Table(divider_data, colWidths=[16 * cm])
    divider_table.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 1, BRASS),
    ]))
    elements.append(divider_table)
    elements.append(Spacer(1, 12))

    # Meta info
    elements.append(Paragraph(f"Report ID: <b>{report.get('id', 'N/A')[:8]}...</b>", body_style))
    user_name = user_profile.get("full_name", user_profile.get("email", "User"))
    elements.append(Paragraph(f"Patient: <b>{user_name}</b>", body_style))
    elements.append(Paragraph(f"Assessment: <b>{report.get('type', 'N/A').upper()}</b>", body_style))
    elements.append(Paragraph(f"Date: <b>{datetime.now().strftime('%B %d, %Y')}</b>", body_style))
    elements.append(Spacer(1, 16))

    # Score & Risk
    elements.append(Paragraph("Assessment Results", heading_style))

    score = report.get("score", 0)
    risk_cat = report.get("risk_category", "Unknown")
    risk_color = "green" if risk_cat == "Low" else "orange" if risk_cat == "Medium" else "red"

    score_data = [
        ["Calculated Score", f"{score}/27"],
        ["Risk Category", f'<font color="{risk_color}"><b>{risk_cat}</b></font>'],
        ["Confidence", f'{report.get("confidence_score", 0) * 100:.0f}%'],
        ["Predicted State", report.get("predicted_state", "N/A")],
    ]
    score_table = Table(score_data, colWidths=[6 * cm, 10 * cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F5EDE3")),
        ("TEXTCOLOR", (0, 0), (-1, -1), CHARCOAL),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#E8E4DF")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 16))

    # AI Summary
    elements.append(Paragraph("AI Summary", heading_style))
    ai_summary = report.get("ai_summary", "No AI summary available.")
    elements.append(Paragraph(ai_summary, body_style))
    elements.append(Spacer(1, 12))

    # Emotions & Topics
    emotions = report.get("emotions_detected", [])
    topics = report.get("topics_detected", [])
    if emotions:
        elements.append(Paragraph("Detected Emotions: <b>" + ", ".join(emotions) + "</b>", body_style))
    if topics:
        elements.append(Paragraph("Detected Topics: <b>" + ", ".join(topics) + "</b>", body_style))
    elements.append(Spacer(1, 12))

    # Recommendations
    recommendations = report.get("recommendations", [])
    if recommendations:
        elements.append(Paragraph("Personalized Recommendations", heading_style))
        for i, rec in enumerate(recommendations[:5], 1):
            elements.append(Paragraph(f"{i}. {rec}", body_style))
        elements.append(Spacer(1, 12))

    # Suggested Activities
    activities = report.get("suggested_activities", [])
    if activities:
        elements.append(Paragraph("Suggested Activities", heading_style))
        for act in activities:
            elements.append(Paragraph(f"• {act}", body_style))

    # Suggested Breathing
    breathing = report.get("suggested_breathing")
    if breathing:
        elements.append(Paragraph(f"Breathing Exercise: <b>{breathing}</b>", body_style))

    # Breathing guide
    if breathing:
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(
            "Try this: Find a comfortable position. Inhale deeply through your nose for 4 counts. "
            "Hold your breath for 7 counts. Exhale slowly through your mouth for 8 counts. Repeat 4 times.",
            body_style,
        ))

    # Journal Prompt
    journal_prompt = report.get("suggested_journal_prompt")
    if journal_prompt:
        elements.append(Paragraph(f"Journal Prompt: <i>{journal_prompt}</i>", body_style))

    # Goals
    goals = report.get("suggested_goals", [])
    if goals:
        elements.append(Paragraph("Suggested Goals", heading_style))
        for goal in goals:
            elements.append(Paragraph(f"☐ {goal}", body_style))

    # Divider
    elements.append(Spacer(1, 20))
    divider_data2 = [[""]]
    divider_table2 = Table(divider_data2, colWidths=[16 * cm])
    divider_table2.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, HexColor("#E8E4DF")),
    ]))
    elements.append(divider_table2)
    elements.append(Spacer(1, 12))

    # Disclaimer
    elements.append(Paragraph(
        "<i>This report is generated by AI for wellness support and educational purposes. "
        "It does not provide medical diagnosis or replace consultation with licensed mental health professionals. "
        "If you are in crisis, please contact your local emergency services or crisis hotline.</i>",
        ParagraphStyle("Disclaimer", parent=body_style, fontSize=8, textColor=STONE),
    ))

    # QR Code
    try:
        qr = qrcode.QRCode(box_size=3, border=1)
        qr.add_data(f"https://mindguard.ai/report/{report.get('id', '')}")
        qr_img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        qr_table = Table(
            [[Image(img_buffer, width=2 * cm, height=2 * cm), Paragraph("Scan to view digital report", paragraph_style)]],
            colWidths=[3 * cm, 13 * cm],
        )
        qr_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(Spacer(1, 12))
        elements.append(qr_table)
    except Exception:
        pass

    # Footer
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} &nbsp;|&nbsp; MindGuard v1.0",
        ParagraphStyle("Footer", parent=body_style, fontSize=8, textColor=STONE, alignment=TA_CENTER),
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
