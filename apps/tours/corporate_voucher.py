import os
from io import BytesIO
from pathlib import Path
from django.conf import settings
from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def clean_ascii(text):
    """
    Sanitizes string for ReportLab default font rendering
    to avoid non-ASCII encoding errors while preserving readable content.
    """
    if not text:
        return ""
    return "".join(c if ord(c) < 128 else " " for c in str(text)).strip()


def generate_corporate_voucher_pdf(corporate_tour):
    """
    Generates an official, beautifully styled executive PDF voucher
    tailored for corporate clients and group tour organizers.
    Returns bytes of the generated PDF document.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0369a1'),
        alignment=TA_RIGHT
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_RIGHT
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#065f46'),
        alignment=TA_RIGHT
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0f172a')
    )

    cell_label = ParagraphStyle(
        'CellLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#475569')
    )

    cell_value = ParagraphStyle(
        'CellValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#0f172a')
    )

    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER
    )

    story = []

    # 1. Header with Brand Logo and Corporate Division Info
    logo_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'logo-horizontal.png'
    if not logo_path.exists():
        logo_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'official-logo.png'

    brand_cells = []
    if logo_path.exists():
        try:
            logo_img = Image(str(logo_path), width=130, height=46)
            brand_cells.append(logo_img)
        except Exception:
            brand_cells.append(Paragraph("<b>BHROMONGHURI</b>", title_style))
    else:
        brand_cells.append(Paragraph("<b>BHROMONGHURI</b>", title_style))

    company_info = (
        "<b>BhromonGhuri Travel & Tours — Corporate Events Division</b><br/>"
        "Govt. Registered Tour Operator & Corporate Travel Specialist<br/>"
        "Hotlines: +8801518919370, +8801855939459 | Email: corporate@bhromonghuri.com<br/>"
        "Head Office: Dhaka, Bangladesh | Web: https://bhromonghuri.com"
    )
    brand_cells.append(Spacer(1, 4))
    brand_cells.append(Paragraph(company_info, cell_value))

    voucher_info = [
        Paragraph("<b>OFFICIAL CORPORATE TRAVEL VOUCHER</b>", title_style),
        Paragraph(f"EVENT REF: <b>{corporate_tour.reference_code}</b>", subtitle_style),
        Paragraph(f"Issued On: {corporate_tour.created_at.strftime('%d %B %Y')}", subtitle_style),
        Paragraph(f"Status: <b>{corporate_tour.get_status_display().upper()}</b>", badge_style),
    ]

    header_table = Table([[brand_cells, voucher_info]], colWidths=[310, 213])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # Colored divider
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0284c7'), spaceAfter=10))

    # 2. Corporate Client Information
    story.append(Paragraph("<b>1. CLIENT ORGANIZATION & CONTACT DETAILS</b>", section_heading))
    story.append(Spacer(1, 4))

    client_data = [
        [
            Paragraph("Organization Name:", cell_label),
            Paragraph(f"<b>{clean_ascii(corporate_tour.company_name)}</b>", cell_value),
            Paragraph("Focal Person:", cell_label),
            Paragraph(f"<b>{clean_ascii(corporate_tour.contact_person)}</b>", cell_value)
        ],
        [
            Paragraph("Designation / Dept:", cell_label),
            Paragraph(clean_ascii(corporate_tour.designation) or "Corporate Admin", cell_value),
            Paragraph("Phone Number:", cell_label),
            Paragraph(clean_ascii(corporate_tour.phone), cell_value)
        ],
        [
            Paragraph("Official Email:", cell_label),
            Paragraph(clean_ascii(corporate_tour.email), cell_value),
            Paragraph("Office Address:", cell_label),
            Paragraph(clean_ascii(corporate_tour.office_address) or "Dhaka, Bangladesh", cell_value)
        ]
    ]

    t_client = Table(client_data, colWidths=[125, 140, 115, 143])
    t_client.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_client)
    story.append(Spacer(1, 10))

    # 3. Event Scope & Multi-Destination Schedule
    story.append(Paragraph("<b>2. EVENT SCOPE & MULTI-DESTINATION ROUTE</b>", section_heading))
    story.append(Spacer(1, 4))

    dests_display = clean_ascii(corporate_tour.get_destinations_display())
    dates_display = f"{corporate_tour.start_date.strftime('%d %b %Y')} to {corporate_tour.end_date.strftime('%d %b %Y')}"

    scope_data = [
        [
            Paragraph("Event Title:", cell_label),
            Paragraph(f"<b>{clean_ascii(corporate_tour.title)}</b>", cell_value),
            Paragraph("Destinations:", cell_label),
            Paragraph(f"<font color='#0369a1'><b>{dests_display}</b></font>", cell_value)
        ],
        [
            Paragraph("Event Duration:", cell_label),
            Paragraph(clean_ascii(corporate_tour.duration_text), cell_value),
            Paragraph("Tour Schedule:", cell_label),
            Paragraph(f"<b>{dates_display}</b>", cell_value)
        ],
        [
            Paragraph("Group Size:", cell_label),
            Paragraph(f"<b>{corporate_tour.num_participants} Participants</b>", cell_value),
            Paragraph("Route Summary:", cell_label),
            Paragraph(clean_ascii(corporate_tour.route_summary) or dests_display, cell_value)
        ]
    ]

    t_scope = Table(scope_data, colWidths=[125, 140, 115, 143])
    t_scope.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_scope)
    story.append(Spacer(1, 10))

    # 4. Logistics & Hospitality Breakdown
    story.append(Paragraph("<b>3. LOGISTICS, TRANSPORT & HOSPITALITY BREAKDOWN</b>", section_heading))
    story.append(Spacer(1, 4))

    transport_str = f"{corporate_tour.bus_count} Bus(es) — {clean_ascii(corporate_tour.bus_type)}"
    hotel_str = clean_ascii(corporate_tour.accommodation_details) or "Standard executive corporate room arrangements."
    food_str = clean_ascii(corporate_tour.catering_details) or "Full board breakfast, lunch, and dinner."

    logistics_data = [
        [
            Paragraph("Transport / Bus:", cell_label),
            Paragraph(f"<b>{transport_str}</b>", cell_value)
        ],
        [
            Paragraph("Resort & Rooms:", cell_label),
            Paragraph(hotel_str, cell_value)
        ],
        [
            Paragraph("Food & Catering:", cell_label),
            Paragraph(food_str, cell_value)
        ]
    ]
    if corporate_tour.special_requirements:
        logistics_data.append([
            Paragraph("Special Setups:", cell_label),
            Paragraph(clean_ascii(corporate_tour.special_requirements), cell_value)
        ])

    t_logistics = Table(logistics_data, colWidths=[125, 398])
    t_logistics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_logistics)
    story.append(Spacer(1, 10))

    # 5. Financial & Billing Summary
    story.append(Paragraph("<b>4. FINANCIAL SUMMARY & BILLING STATUS</b>", section_heading))
    story.append(Spacer(1, 4))

    total_str = f"BDT {corporate_tour.total_cost:,.2f}"
    advance_str = f"BDT {corporate_tour.advance_paid:,.2f}"
    due_str = f"BDT {corporate_tour.due_amount:,.2f}"
    pay_status_str = corporate_tour.get_payment_status_display().upper()

    billing_data = [
        [
            Paragraph("Contracted Budget:", cell_label),
            Paragraph(f"<b>{total_str}</b>", cell_value),
            Paragraph("Advance Received:", cell_label),
            Paragraph(f"<font color='#047857'><b>{advance_str}</b></font>", cell_value)
        ],
        [
            Paragraph("Balance Due:", cell_label),
            Paragraph(f"<font color='#b91c1c'><b>{due_str}</b></font>", cell_value),
            Paragraph("Payment Status:", cell_label),
            Paragraph(f"<b>{clean_ascii(pay_status_str)}</b>", cell_value)
        ]
    ]

    t_billing = Table(billing_data, colWidths=[125, 140, 115, 143])
    t_billing.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdf4')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#86efac')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bbf7d0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_billing)
    story.append(Spacer(1, 10))

    # 6. Custom Corporate Itinerary (if available)
    itineraries = list(corporate_tour.itineraries.all())
    if itineraries:
        story.append(Paragraph("<b>5. CUSTOM DAY-BY-DAY ITINERARY</b>", section_heading))
        story.append(Spacer(1, 4))

        itin_data = []
        for itin in itineraries:
            itin_data.append([
                Paragraph(f"<b>Day {itin.day_number}: {clean_ascii(itin.title)}</b>", cell_label),
                Paragraph(f"{clean_ascii(itin.description)}<br/><i>Stay: {clean_ascii(itin.stay_info) or 'Designated Resort'}</i>", cell_value)
            ])

        t_itin = Table(itin_data, colWidths=[140, 383])
        t_itin.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 7),
            ('RIGHTPADDING', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_itin)
        story.append(Spacer(1, 10))

    # 7. Terms & Corporate Helpline
    terms_html = (
        "• <b>Dedicated Tour Escort:</b> An executive tour lead will accompany the group for smooth on-ground logistics.<br/>"
        "• <b>Luggage & Safety:</b> Travelers are advised to carry original personal identification documents.<br/>"
        "• <b>24/7 Corporate Helpline:</b> For real-time coordinator support, call +8801518919370 or +8801855939459."
    )
    t_terms = Table([[Paragraph(terms_html, cell_value)]], colWidths=[523])
    t_terms.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_terms)
    story.append(Spacer(1, 10))

    # Footer note
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=6))
    story.append(Paragraph(
        "BhromonGhuri Travel & Tours — Official Corporate Event Voucher & Contract Document.<br/>"
        "This is an electronically verified corporate document. For billing inquiries, contact corporate@bhromonghuri.com.",
        footer_style
    ))

    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
