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
    # Keep ASCII printable characters, map known symbols
    return "".join(c if ord(c) < 128 else " " for c in str(text)).strip()


def draw_voucher_watermark(canvas, doc):
    """
    Applies the company logo as a subtle, faint watermark background across
    the center of the page without obstructing readability.
    """
    canvas.saveState()
    logo_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'official-logo-transparent.png'
    if not logo_path.exists():
        logo_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'logo-transparent.png'
    if not logo_path.exists():
        logo_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'official-logo.png'

    if logo_path.exists():
        try:
            canvas.setFillAlpha(0.06)
            page_w, page_h = doc.pagesize
            wm_size = 360
            x = (page_w - wm_size) / 2
            y = (page_h - wm_size) / 2
            canvas.drawImage(
                str(logo_path),
                x, y,
                width=wm_size,
                height=wm_size,
                preserveAspectRatio=True,
                mask='auto'
            )
        except Exception:
            pass
    canvas.restoreState()


def generate_booking_voucher_pdf(booking):
    """
    Generates an official, beautifully styled PDF voucher for a booking.
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

    # Custom typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0369a1'),
        alignment=TA_RIGHT
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
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
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0f172a')
    )

    cell_label = ParagraphStyle(
        'CellLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569')
    )

    cell_value = ParagraphStyle(
        'CellValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
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

    # 1. Header Section with Brand Logo and Confirmation Info
    logo_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'logo-horizontal.png'
    if not logo_path.exists():
        logo_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'official-logo.png'

    brand_cells = []
    if logo_path.exists():
        try:
            # 130 pt width, 46 pt height
            logo_img = Image(str(logo_path), width=130, height=46)
            brand_cells.append(logo_img)
        except Exception:
            brand_cells.append(Paragraph("<b>BHROMONGHURI</b>", title_style))
    else:
        brand_cells.append(Paragraph("<b>BHROMONGHURI</b>", title_style))

    company_info = (
        "<b>BhromonGhuri Travel & Tours</b><br/>"
        "Govt. Registered Tour Operator & Travel Agency<br/>"
        "Dhaka, Bangladesh | Hotlines: +8801518919370, +8801855939459<br/>"
        "Email: bhromonghuri@gmail.com | Web: https://bhromonghuri.com"
    )
    brand_cells.append(Spacer(1, 4))
    brand_cells.append(Paragraph(company_info, cell_value))

    is_offline = getattr(booking, 'booking_source', '') == 'OFFLINE'
    source_title = "OFFLINE BOOKING VOUCHER" if is_offline else "OFFICIAL BOOKING VOUCHER"
    source_badge_text = "OFFLINE / WALK-IN" if is_offline else "ONLINE CONFIRMED"
    source_badge_color = "#6366f1" if is_offline else "#065f46"

    source_badge_style = ParagraphStyle(
        'SourceBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor(source_badge_color),
        alignment=TA_RIGHT
    )

    voucher_info = [
        Paragraph(f"<b>{source_title}</b>", title_style),
        Paragraph(f"VOUCHER REF: <b>{booking.booking_reference}</b>", subtitle_style),
        Paragraph(f"Type: <b>{source_badge_text}</b>", source_badge_style),
        Paragraph(f"Issued On: {booking.created_at.strftime('%d %B %Y')}", subtitle_style),
        Paragraph(f"Status: <b>{booking.get_status_display().upper()}</b>", badge_style),
    ]

    header_table = Table(
        [[brand_cells, voucher_info]],
        colWidths=[310, 213]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # Decorative colored divider
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0284c7'), spaceAfter=12))

    # 2. Traveler / Customer Details Section
    story.append(Paragraph("<b>1. TRAVELER & RESERVATION DETAILS</b>", section_heading))
    story.append(Spacer(1, 4))

    id_label = booking.get_identification_type_display() if hasattr(booking, 'get_identification_type_display') else "ID Doc"
    if booking.identification_number:
        id_val_text = f"{id_label}: {booking.identification_number}"
    elif booking.identification_document:
        id_val_text = f"{id_label}: Uploaded"
    else:
        id_val_text = "Pending / Carry Original"

    traveler_data = [
        [
            Paragraph("Lead Customer Name:", cell_label),
            Paragraph(clean_ascii(booking.customer_name), cell_value),
            Paragraph("Contact Phone:", cell_label),
            Paragraph(clean_ascii(booking.customer_phone), cell_value)
        ],
        [
            Paragraph("Email Address:", cell_label),
            Paragraph(clean_ascii(booking.customer_email), cell_value),
            Paragraph("Total Travelers:", cell_label),
            Paragraph(f"<b>{booking.num_travelers} Person(s)</b>", cell_value)
        ],
        [
            Paragraph("Traveler ID / Document:", cell_label),
            Paragraph(clean_ascii(id_val_text), cell_value),
            Paragraph("Special Requests:", cell_label),
            Paragraph(clean_ascii(booking.special_requests) or "None", cell_value)
        ]
    ]

    t_traveler = Table(traveler_data, colWidths=[130, 135, 120, 138])
    t_traveler.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_traveler)
    story.append(Spacer(1, 12))

    # 3. Tour Package & Itinerary Details
    story.append(Paragraph("<b>2. TOUR PACKAGE & DEPARTURE SCHEDULE</b>", section_heading))
    story.append(Spacer(1, 4))

    tour = booking.tour
    tour_date = booking.tour_date

    travel_date_str = "Flexible / Open Departure"
    if tour_date:
        travel_date_str = f"{tour_date.start_date.strftime('%d %b %Y')} to {tour_date.end_date.strftime('%d %b %Y')}"

    dest_str = clean_ascii(tour.destination.name) if tour.destination else "Bangladesh"

    seats_str = clean_ascii(booking.selected_seats) if booking.selected_seats else "Assigned upon departure"
    bus_name = clean_ascii(booking.assigned_bus.bus_name) if booking.assigned_bus else "Reserved AC Coach"
    if booking.tour.has_bus_seat_selection or booking.selected_seats:
        bus_seat_display = f"<b>{seats_str}</b> ({bus_name})"
    else:
        bus_seat_display = "Standard Tour Coach"

    tour_data = [
        [
            Paragraph("Tour Package:", cell_label),
            Paragraph(f"<b>{clean_ascii(tour.title)}</b>", cell_value),
            Paragraph("Destination:", cell_label),
            Paragraph(dest_str, cell_value)
        ],
        [
            Paragraph("Duration:", cell_label),
            Paragraph(clean_ascii(tour.duration), cell_value),
            Paragraph("Travel Schedule / Batch:", cell_label),
            Paragraph(f"<b>{travel_date_str}</b>", cell_value)
        ],
        [
            Paragraph("Assigned Bus & Seats:", cell_label),
            Paragraph(f"<font color='#0369a1'>{bus_seat_display}</font>", cell_value),
            Paragraph("Departure Reporting:", cell_label),
            Paragraph("<b>30 mins before travel</b>", cell_value)
        ]
    ]

    t_tour = Table(tour_data, colWidths=[130, 135, 120, 138])
    t_tour.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_tour)
    story.append(Spacer(1, 12))

    # 4. Payment & Billing Verification Record
    story.append(Paragraph("<b>3. PAYMENT SUMMARY & TRANSACTION VERIFICATION</b>", section_heading))
    story.append(Spacer(1, 4))

    payment = booking.payments.filter(status='SUCCESS').first()
    if not payment:
        payment = booking.payments.first()

    method_str = payment.get_payment_method_display() if payment else "bKash / Nagad"
    trx_str = payment.transaction_id if payment else "Pending Verification"
    sender_str = (payment.sender_number if payment and payment.sender_number else booking.customer_phone)
    pay_status = payment.get_status_display() if payment else booking.get_status_display()

    billing_data = [
        [
            Paragraph("Package Rate / Person:", cell_label),
            Paragraph(f"BDT {booking.unit_price:,.2f}", cell_value),
            Paragraph("Payment Method:", cell_label),
            Paragraph(f"<b>{method_str}</b>", cell_value)
        ],
        [
            Paragraph("Number of Travelers:", cell_label),
            Paragraph(f"{booking.num_travelers} Person(s)", cell_value),
            Paragraph("Transaction ID (TrxID):", cell_label),
            Paragraph(f"<b>{trx_str}</b>", cell_value)
        ],
        [
            Paragraph("Total Amount Paid:", cell_label),
            Paragraph(f"<b>BDT {booking.total_amount:,.2f}</b>", cell_value),
            Paragraph("Sender Mobile / Account:", cell_label),
            Paragraph(sender_str, cell_value)
        ],
        [
            Paragraph("Payment Status:", cell_label),
            Paragraph(f"<font color='#047857'><b>{pay_status.upper()}</b></font>", cell_value),
            Paragraph("Verification Date:", cell_label),
            Paragraph(payment.verified_at.strftime('%d %b %Y %I:%M %p') if payment and payment.verified_at else timezone.now().strftime('%d %b %Y'), cell_value)
        ]
    ]

    t_billing = Table(billing_data, colWidths=[130, 135, 120, 138])
    t_billing.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdf4')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#86efac')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bbf7d0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_billing)
    story.append(Spacer(1, 12))

    # 5. Package Inclusions & Important Instructions
    story.append(Paragraph("<b>4. ESSENTIAL TRAVEL GUIDELINES & HELPLINE</b>", section_heading))
    story.append(Spacer(1, 4))

    guidelines_html = (
        "• <b>Mandatory Travel Voucher:</b> Travelers must bring a printed or digital copy of this voucher on the day of the tour.<br/>"
        "• <b>Reporting Time:</b> Please report to the departure station at least 30 minutes before departure.<br/>"
        "• <b>Identity Verification:</b> Travelers must carry a valid National ID Card / Passport and this voucher.<br/>"
        "• <b>Luggage Policy:</b> Maximum one standard backpack / luggage per traveler for smooth transit.<br/>"
        "• <b>24/7 Helpline & Support:</b> For emergency updates, call +8801518919370 or +8801855939459.<br/>"
        "• <b>Refund / Reschedule:</b> All cancellations are subject to BhromonGhuri standard booking policies."
    )
    guidelines_cell = Paragraph(guidelines_html, cell_value)

    t_guide = Table([[guidelines_cell]], colWidths=[523])
    t_guide.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_guide)
    story.append(Spacer(1, 14))

    # Footer note & security stamp
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=8))
    story.append(Paragraph(
        "Thank you for traveling with BhromonGhuri! | Explore • Experience • Discover<br/>"
        "This is an electronically generated and verified document. No physical signature is required.",
        footer_style
    ))

    # Build document with faint branded watermark background
    doc.build(story, onFirstPage=draw_voucher_watermark, onLaterPages=draw_voucher_watermark)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
