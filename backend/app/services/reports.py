from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import get_settings

settings = get_settings()


def build_sustainability_pdf(payload: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Smart Campus AI Report")
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Smart Campus AI", styles["Title"]),
        Paragraph("AI-Powered Energy, Water &amp; Sustainability Intelligence Platform", styles["Heading2"]),
        Paragraph(f"Campus: {payload.get('campus', settings.campus_name)}", styles["Normal"]),
        Paragraph(f"Period: {payload.get('period')} ({payload.get('start')} — {payload.get('end')})", styles["Normal"]),
        Paragraph(f"Generated: {payload.get('generated_at')}", styles["Normal"]),
        Paragraph(f"Data mode: {payload.get('data_mode', 'DEMO')} — simulated unless otherwise marked.", styles["Italic"]),
        Spacer(1, 12),
        Paragraph("Campus totals", styles["Heading2"]),
    ]
    totals = [
        ["Metric", "Value"],
        ["Energy (kWh)", str(payload.get("total_energy_kwh"))],
        ["Solar (kWh)", str(payload.get("total_solar_kwh"))],
        ["Water (L)", str(payload.get("total_water_litres"))],
        ["CO2 avoided (kg)", str(payload.get("co2_avoided_kg"))],
        ["Emission factor", f"{payload.get('co2_factor_kg_per_kwh')} kg/kWh"],
        ["Anomalies", str(payload.get("anomalies"))],
    ]
    table = Table(totals, colWidths=[220, 220])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f0fdfa")),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 14))
    story.append(Paragraph("Green Score ranking (normalized; not raw kWh)", styles["Heading2"]))
    ranks = [["Rank", "Dept", "Score", "kWh/student", "kWh/m²"]]
    for i, row in enumerate(payload.get("scores", []), start=1):
        ranks.append(
            [
                str(i),
                row.get("code"),
                str(row.get("total_score")),
                str(row.get("kwh_per_student")),
                str(row.get("kwh_per_sqm")),
            ]
        )
    rt = Table(ranks, colWidths=[60, 80, 80, 110, 110])
    rt.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#134e4a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ]
        )
    )
    story.append(rt)
    story.append(Spacer(1, 14))
    story.append(Paragraph("Open anomalies", styles["Heading2"]))
    for a in payload.get("anomaly_list", [])[:12]:
        story.append(
            Paragraph(
                f"<b>{a.get('department_code')}</b> {a.get('severity')}: {a.get('reason', '')[:280]}",
                styles["Normal"],
            )
        )
        story.append(Paragraph(f"Recommendation: {a.get('recommendation', '')[:280]}", styles["Normal"]))
        story.append(Spacer(1, 6))
    story.append(Paragraph("Forecast snapshot", styles["Heading2"]))
    for f in payload.get("forecast_list", [])[:8]:
        story.append(
            Paragraph(
                f"{f.get('department_code')} +{f.get('horizon_hours')}h: {f.get('predicted_kwh')} kWh "
                f"[{f.get('lower_bound')}–{f.get('upper_bound')}] ({f.get('model_name')})",
                styles["Normal"],
            )
        )
    story.append(Spacer(1, 12))
    story.append(Paragraph("Recommendations", styles["Heading2"]))
    for r in payload.get("recommendations", [])[:10]:
        story.append(Paragraph(f"<b>{r.get('title')}</b> — {r.get('recommendation')}", styles["Normal"]))
    doc.build(story)
    return buffer.getvalue()
