"""Generate a fictitious commercial invoice PDF for testing the analyzer.

Trade lane: Miami, FL (USA) exporter -> Santo Domingo, DR importer.
Goods: Aftermarket auto parts wholesale shipment (a representative DR import).

Output: docs/test-assets/commercial-invoice-miami-sdq-test.pdf
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
except ModuleNotFoundError as e:
    sys.stderr.write(
        f"\nERROR: this script requires reportlab ({e.name!r} is missing).\n"
        "Install it first:\n\n"
        "    pip install reportlab\n\n"
        "(reportlab is intentionally NOT in backend/requirements.txt — this\n"
        "generator is a developer tool, not a runtime dep.)\n"
    )
    raise SystemExit(1) from e


OUTPUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "test-assets"
    / "commercial-invoice-miami-sdq-test.pdf"
)


def money(value: float) -> str:
    return f"${value:,.2f}"


def build_line_items() -> tuple[list[list[str]], float]:
    items = [
        # (sku, description, hs_code, qty, unit, unit_price)
        ("BP-7842", "Ceramic brake pad set, front axle (Toyota Hilux 2016-2023)", "8708.30.50", 120, "set", 28.40),
        ("BP-7855", "Ceramic brake pad set, rear axle (Toyota Hilux 2016-2023)", "8708.30.50", 96, "set", 24.10),
        ("FL-2210", "Engine oil filter, spin-on (universal 3/4-16 UNF)", "8421.23.00", 480, "ea", 3.85),
        ("FL-2330", "Cabin air filter, activated carbon (Honda CR-V 2018-2024)", "8421.39.80", 240, "ea", 6.20),
        ("SP-5501", "Iridium spark plug, 14mm (NGK ILZKR7B11 cross-ref)", "8511.10.00", 600, "ea", 4.55),
        ("AL-9120", "Alternator, 12V 130A (remanufactured, Bosch core)", "8511.50.00", 24, "ea", 142.00),
        ("BT-4400", "AGM starter battery, Group 31, 950 CCA", "8507.10.00", 36, "ea", 168.50),
        ("TR-1280", "All-terrain tire, LT265/70R17 (load range E)", "4011.20.10", 48, "ea", 178.90),
        ("WP-3340", "Engine water pump w/ gasket (GM 5.3L V8 2014-2020)", "8413.30.90", 20, "ea", 64.75),
        ("HD-0012", "Hydraulic brake hose kit, DOT-approved (4-line set)", "8708.39.50", 60, "kit", 38.20),
    ]

    rows: list[list[str]] = [[
        "SKU",
        "Description",
        "HS Code",
        "Qty",
        "UoM",
        "Unit Price (USD)",
        "Line Total (USD)",
    ]]
    subtotal = 0.0
    for sku, desc, hs, qty, uom, price in items:
        line = qty * price
        subtotal += line
        rows.append([sku, desc, hs, str(qty), uom, money(price), money(line)])

    return rows, subtotal


def build_pdf() -> Path:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=LETTER,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title="Commercial Invoice — Test Fixture",
        author="Puente AI test asset (fictitious)",
        # ReportLab embeds CreationDate / ModDate / a random PDF ID by
        # default. invariant=1 freezes those, so re-running this script
        # against the same source produces byte-identical output. Required
        # for the PDF to be checked in alongside the script as a
        # regenerable test artifact (per Copilot + CodeRabbit review on
        # PR #49 — without invariant=1 the committed PDF drifts from the
        # script the moment anyone re-generates it).
        invariant=1,
    )

    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    body.fontSize = 9
    body.leading = 12
    h1 = ParagraphStyle(
        "InvHeader",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        alignment=2,
        spaceAfter=2,
        textColor=colors.HexColor("#0b3d91"),
    )
    h2 = ParagraphStyle(
        "InvSub",
        parent=styles["Heading2"],
        fontSize=10,
        leading=12,
        alignment=2,
        spaceAfter=8,
        textColor=colors.grey,
    )
    label = ParagraphStyle(
        "Label",
        parent=body,
        fontSize=8,
        textColor=colors.HexColor("#0b3d91"),
        spaceAfter=1,
        leading=10,
    )
    small = ParagraphStyle("small", parent=body, fontSize=8, leading=10)

    story = []

    header_left = Paragraph(
        "<b>Coral Gables Auto Parts Wholesale, LLC</b><br/>"
        "2150 NW 22nd Street, Suite 400<br/>"
        "Miami, FL 33142, USA<br/>"
        "Tel: +1 (305) 555-0142 &nbsp;&nbsp; EIN: 47-3829104<br/>"
        "FDA / CBP Filer Code: ABI-7842",
        small,
    )
    header_right = Paragraph(
        "COMMERCIAL INVOICE<br/>"
        "<font size=9 color='grey'>Factura Comercial</font>",
        h1,
    )

    story.append(
        Table(
            [[header_left, header_right]],
            colWidths=[3.6 * inch, 3.8 * inch],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            ),
        )
    )
    story.append(Spacer(1, 6))

    meta_table = Table(
        [
            [
                Paragraph("INVOICE NO.", label),
                Paragraph("INVOICE DATE", label),
                Paragraph("PO REFERENCE", label),
                Paragraph("INCOTERMS 2020", label),
                Paragraph("CURRENCY", label),
            ],
            [
                Paragraph("<b>CGAP-2026-04127</b>", body),
                Paragraph("<b>Apr 28, 2026</b>", body),
                Paragraph("<b>RAS-PO-9981</b>", body),
                Paragraph("<b>CIF Santo Domingo</b>", body),
                Paragraph("<b>USD</b>", body),
            ],
        ],
        colWidths=[1.45 * inch] * 5,
        style=TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#0b3d91")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cfd8e6")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2fa")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        ),
    )
    story.append(meta_table)
    story.append(Spacer(1, 10))

    seller_buyer = Table(
        [
            [
                Paragraph("SELLER / EXPORTER", label),
                Paragraph("BUYER / IMPORTER", label),
            ],
            [
                Paragraph(
                    "<b>Coral Gables Auto Parts Wholesale, LLC</b><br/>"
                    "2150 NW 22nd Street, Suite 400<br/>"
                    "Miami, FL 33142, USA<br/>"
                    "Attn: Export Operations &mdash; Sandra Restrepo<br/>"
                    "Tel: +1 (305) 555-0142<br/>"
                    "Email: exports@cgapwholesale.com<br/>"
                    "Tax ID (EIN): 47-3829104",
                    body,
                ),
                Paragraph(
                    "<b>Repuestos del Atl&aacute;ntico, S.R.L.</b><br/>"
                    "Av. John F. Kennedy, Km. 7&frac12;, No. 215<br/>"
                    "Ensanche Quisqueya<br/>"
                    "Santo Domingo, D.N. 10205<br/>"
                    "Rep&uacute;blica Dominicana<br/>"
                    "Attn: Compras &mdash; Luis F. Pe&ntilde;a Mart&iacute;nez<br/>"
                    "Tel: +1 (809) 555-0188<br/>"
                    "Email: compras@repuestosatlantico.do<br/>"
                    "RNC: 1-30-87421-5",
                    body,
                ),
            ],
        ],
        colWidths=[3.65 * inch, 3.65 * inch],
        style=TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#0b3d91")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cfd8e6")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2fa")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        ),
    )
    story.append(seller_buyer)
    story.append(Spacer(1, 10))

    shipping = Table(
        [
            [
                Paragraph("SHIP FROM (Port of Loading)", label),
                Paragraph("SHIP TO (Port of Discharge)", label),
                Paragraph("MODE / VESSEL", label),
            ],
            [
                Paragraph(
                    "<b>PortMiami</b><br/>"
                    "Terminal: South Florida Container Terminal<br/>"
                    "1100 Port Blvd., Miami, FL 33132<br/>"
                    "UN/LOCODE: USMIA",
                    body,
                ),
                Paragraph(
                    "<b>Puerto de Haina Oriental</b><br/>"
                    "Haina, Prov. San Crist&oacute;bal<br/>"
                    "Rep&uacute;blica Dominicana<br/>"
                    "UN/LOCODE: DOHAI &nbsp; (final delivery: Santo Domingo, DOSDQ)",
                    body,
                ),
                Paragraph(
                    "<b>Ocean &mdash; FCL</b><br/>"
                    "Carrier: Crowley Liner Services<br/>"
                    "Vessel/Voy: M/V Caribe Express &mdash; V.214N<br/>"
                    "ETD Miami: May 02, 2026<br/>"
                    "ETA Haina: May 05, 2026<br/>"
                    "Container: CRLU-7843921 (40' HC) &mdash; Seal: 09814372<br/>"
                    "B/L No.: CRWY-MIA-26-09812",
                    body,
                ),
            ],
        ],
        colWidths=[2.45 * inch, 2.45 * inch, 2.45 * inch],
        style=TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#0b3d91")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cfd8e6")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2fa")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        ),
    )
    story.append(shipping)
    story.append(Spacer(1, 12))

    rows, subtotal = build_line_items()
    line_table = Table(
        rows,
        colWidths=[
            0.75 * inch,
            2.65 * inch,
            0.85 * inch,
            0.45 * inch,
            0.45 * inch,
            1.0 * inch,
            1.15 * inch,
        ],
        repeatRows=1,
    )
    line_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d91")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8.5),
                ("FONTSIZE", (0, 1), (-1, -1), 8.5),
                ("ALIGN", (3, 1), (3, -1), "CENTER"),
                ("ALIGN", (4, 1), (4, -1), "CENTER"),
                ("ALIGN", (5, 1), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fb")]),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cfd8e6")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#0b3d91")),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(line_table)
    story.append(Spacer(1, 8))

    insurance = round(subtotal * 0.012, 2)
    freight = 2_485.00
    handling = 320.00
    total = subtotal + insurance + freight + handling

    totals = Table(
        [
            ["", "Merchandise subtotal (FOB Miami)", money(subtotal)],
            ["", "International ocean freight", money(freight)],
            ["", "Marine cargo insurance (1.2% of FOB)", money(insurance)],
            ["", "Export documentation & handling", money(handling)],
            ["", "TOTAL CIF SANTO DOMINGO (USD)", money(total)],
        ],
        colWidths=[3.85 * inch, 2.4 * inch, 1.05 * inch],
        style=TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("LINEABOVE", (1, -1), (-1, -1), 1.0, colors.HexColor("#0b3d91")),
                ("FONTNAME", (1, -1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (1, -1), (-1, -1), colors.HexColor("#eef2fa")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        ),
    )
    story.append(totals)
    story.append(Spacer(1, 10))

    payment = Table(
        [
            [
                Paragraph("PAYMENT TERMS", label),
                Paragraph("BANKING INSTRUCTIONS", label),
            ],
            [
                Paragraph(
                    "<b>Net 60 days from B/L date</b><br/>"
                    "Method: Wire transfer (USD) only.<br/>"
                    "Late payments accrue 1.5% per month.<br/>"
                    "Past-due balance over 90 days subject to collections.<br/>"
                    "Buyer responsible for all DR import duties, ITBIS,<br/>"
                    "and customs broker fees at Aduanas DR.",
                    body,
                ),
                Paragraph(
                    "<b>Beneficiary:</b> Coral Gables Auto Parts Wholesale, LLC<br/>"
                    "<b>Bank:</b> Truist Bank, 200 S Biscayne Blvd, Miami, FL 33131<br/>"
                    "<b>ABA / Routing:</b> 061000104<br/>"
                    "<b>Account:</b> 1000 2847 3921<br/>"
                    "<b>SWIFT/BIC:</b> SNTRUS3A<br/>"
                    "<b>Reference:</b> Invoice CGAP-2026-04127",
                    body,
                ),
            ],
        ],
        colWidths=[3.65 * inch, 3.65 * inch],
        style=TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#0b3d91")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cfd8e6")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2fa")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        ),
    )
    story.append(payment)
    story.append(Spacer(1, 10))

    declarations = Paragraph(
        "<b>Country of Origin:</b> United States of America (USA) &mdash; "
        "all goods qualify for preferential treatment under the "
        "Dominican Republic&ndash;Central America&ndash;United States Free Trade Agreement "
        "(<b>DR-CAFTA</b>). Certificate of Origin attached.<br/><br/>"
        "<b>Total packages:</b> 38 cartons on 6 standard pallets &nbsp;|&nbsp; "
        "<b>Gross weight:</b> 4,820 lbs / 2,186 kg &nbsp;|&nbsp; "
        "<b>Net weight:</b> 4,310 lbs / 1,955 kg &nbsp;|&nbsp; "
        "<b>Cubic volume:</b> 28.4 m&sup3;<br/><br/>"
        "<b>Exporter declaration:</b> I, the undersigned, hereby certify that the "
        "information on this invoice is true and correct, that the contents and value "
        "of this shipment are as stated above, and that the goods described are of "
        "U.S. origin and were not manufactured in any sanctioned jurisdiction. "
        "These commodities, technology, or software were exported from the United "
        "States in accordance with the Export Administration Regulations. Diversion "
        "contrary to U.S. law is prohibited.<br/><br/>"
        "Signed: <i>Sandra Restrepo, VP Export Operations</i> &nbsp;&nbsp; "
        "Date: Apr 28, 2026 &nbsp;&nbsp; Place: Miami, FL",
        small,
    )
    story.append(declarations)
    story.append(Spacer(1, 8))

    footer = Paragraph(
        "<font size=7 color='grey'>"
        "FICTITIOUS DOCUMENT &mdash; FOR SOFTWARE TESTING ONLY. "
        "Generated for Puente AI invoice analyzer fixture. "
        "Companies, persons, addresses, tax IDs, bank accounts, vessel and "
        "container numbers shown above are not real and any resemblance to "
        "actual entities is coincidental."
        "</font>",
        small,
    )
    story.append(footer)

    doc.build(story)
    return OUTPUT_PATH


if __name__ == "__main__":
    out = build_pdf()
    print(f"Wrote {out}")
