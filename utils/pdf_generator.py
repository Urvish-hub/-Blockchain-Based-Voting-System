from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io

def generate_vote_receipt(receipt_data):
    """Generate PDF receipt for vote"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#334155'),
        spaceAfter=12,
        alignment=TA_LEFT
    )
    
    # Title
    title = Paragraph("🗳️ VOTING RECEIPT", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Receipt Number
    receipt_number = Paragraph(
        f"<b>Receipt Number:</b> VOTE-{receipt_data['vote_id']:06d}",
        normal_style
    )
    elements.append(receipt_number)
    elements.append(Spacer(1, 0.2*inch))
    
    # Date and Time
    vote_date = receipt_data['voted_at']
    if isinstance(vote_date, str):
        try:
            # Try different datetime formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d']:
                try:
                    vote_date = datetime.strptime(vote_date, fmt)
                    break
                except ValueError:
                    continue
        except:
            vote_date = datetime.now()
    elif not isinstance(vote_date, datetime):
        vote_date = datetime.now()
    
    date_str = vote_date.strftime('%B %d, %Y at %I:%M %p')
    date_para = Paragraph(
        f"<b>Date & Time:</b> {date_str}",
        normal_style
    )
    elements.append(date_para)
    elements.append(Spacer(1, 0.4*inch))
    
    # Voter Information Section
    voter_heading = Paragraph("VOTER INFORMATION", heading_style)
    elements.append(voter_heading)
    
    voter_data = [
        ['Full Name:', receipt_data['full_name']],
        ['Username:', receipt_data['username']],
        ['Email:', receipt_data['email']],
        ['Voter ID:', f"V{receipt_data['voter_id']:06d}"]
    ]
    
    voter_table = Table(voter_data, colWidths=[2*inch, 4*inch])
    voter_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(voter_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Candidate Information Section
    candidate_heading = Paragraph("CANDIDATE SELECTED", heading_style)
    elements.append(candidate_heading)
    
    candidate_data = [
        ['Candidate Name:', receipt_data['candidate_name']],
        ['Party/Organization:', receipt_data['party'] or 'Independent'],
        ['Position:', receipt_data['position']]
    ]
    
    candidate_table = Table(candidate_data, colWidths=[2*inch, 4*inch])
    candidate_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eef2ff')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c7d2fe')),
    ]))
    elements.append(candidate_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Important Notice
    notice_style = ParagraphStyle(
        'Notice',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        backColor=colors.HexColor('#f1f5f9'),
        borderPadding=15
    )
    
    notice = Paragraph(
        "<b>IMPORTANT:</b> This receipt serves as proof of your vote. "
        "Please keep this document safe. Your vote has been recorded securely and anonymously.",
        notice_style
    )
    elements.append(notice)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER,
        spaceBefore=20
    )
    
    footer = Paragraph(
        "This is an official voting receipt generated by the Online Voting System.<br/>"
        "For any queries, please contact the election administration.",
        footer_style
    )
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    buffer.seek(0)
    return buffer

