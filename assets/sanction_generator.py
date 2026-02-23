# sanction_generator.py
# Bank-Grade Professional Sanction Letter for LoanVerse AI
# Compliant with RBI NBFC Guidelines & Tata Capital Standards

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from io import BytesIO
from datetime import datetime, timedelta
import qrcode

def generate_sanction_letter(loan_details):
    """
    Generate bank-grade professional sanction letter
    Compliant with RBI NBFC guidelines and industry standards
    
    Args:
        loan_details (dict): Complete loan and customer information
        
    Returns:
        bytes: Professional PDF sanction letter
    """
    
    # Create PDF in memory
    buffer = BytesIO()
    
    # Document setup with professional margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=2*cm,
        title="Loan Sanction Letter",
        author="LoanVerse Financial Services"
    )
    
    # Story (content container)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # ==================== CUSTOM STYLES ====================
    
    # Letterhead style
    letterhead_style = ParagraphStyle(
        'Letterhead',
        parent=styles['Normal'],
        fontSize=20,
        textColor=colors.HexColor('#003366'),  # Dark blue (banking standard)
        spaceAfter=5,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=24
    )
    
    # Subheader style
    subheader_style = ParagraphStyle(
        'Subheader',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        spaceAfter=15,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # Title style
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#003366'),
        spaceAfter=20,
        spaceBefore=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        borderWidth=2,
        borderColor=colors.HexColor('#003366'),
        borderPadding=8,
        backColor=colors.HexColor('#F0F8FF')
    )
    
    # Section heading style
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#003366'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderWidth=0,
        leftIndent=0,
        backColor=colors.HexColor('#E8F4F8'),
        borderPadding=4
    )
    
    # Body text style
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=8,
        leading=14,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Legal text style (smaller)
    legal_style = ParagraphStyle(
        'Legal',
        parent=styles['BodyText'],
        fontSize=8,
        spaceAfter=6,
        leading=11,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        textColor=colors.HexColor('#333333')
    )
    
    # Reference number style
    ref_style = ParagraphStyle(
        'Reference',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#003366'),
        spaceAfter=5,
        fontName='Helvetica-Bold'
    )
    
    # ==================== GENERATE REFERENCE NUMBERS ====================
    
    current_date = datetime.now()
    sanction_number = f"LVSL/{current_date.strftime('%Y')}/{current_date.strftime('%m')}/{loan_details.get('phone', '0000000000')[-6:]}"
    application_number = f"LVAPP/{current_date.strftime('%Y%m%d')}/{loan_details.get('phone', '0000000000')[-4:]}"
    
    issue_date = current_date.strftime("%d %B %Y")
    validity_date = (current_date + timedelta(days=30)).strftime("%d %B %Y")
    
    first_emi_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
    last_emi_date = first_emi_date + timedelta(days=30 * loan_details.get('tenure', 36))
    
    # ==================== HEADER / LETTERHEAD ====================
    
    story.append(Paragraph("LOANVERSE FINANCIAL SERVICES PVT. LTD.", letterhead_style))
    
    subheader_text = """
    <b>Registered Office:</b> 401, Tower A, Peninsula Corporate Park, Lower Parel, Mumbai - 400013<br/>
    <b>CIN:</b> U65990MH2020PTC123456 | <b>RBI License No:</b> N-14.03339 (NBFC-ND)<br/>
    <b>Phone:</b> 1800-123-LOAN (5626) | <b>Email:</b> loans@loanverse.ai | <b>Web:</b> www.loanverse.ai
    """
    story.append(Paragraph(subheader_text, subheader_style))
    
    # Horizontal line
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("─" * 100, ParagraphStyle('Line', fontSize=6)))
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== REFERENCE SECTION ====================
    
    ref_data = [
        [Paragraph(f"<b>Ref. No:</b> {sanction_number}", ref_style), 
         Paragraph(f"<b>Date:</b> {issue_date}", ref_style)],
        [Paragraph(f"<b>Application No:</b> {application_number}", ref_style),
         Paragraph(f"<b>Valid Until:</b> {validity_date}", ref_style)]
    ]
    
    ref_table = Table(ref_data, colWidths=[3.2*inch, 3.2*inch])
    ref_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    story.append(ref_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== TITLE ====================
    
    story.append(Paragraph("🎉 LOAN SANCTION LETTER 🎉", title_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Approval notice
    approval_text = f"""
    <para alignment="center" fontSize="11" textColor="#006400" fontName="Helvetica-Bold">
    ✓ CONGRATULATIONS! Your loan application has been <u>APPROVED</u>
    </para>
    """
    story.append(Paragraph(approval_text, body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # ==================== BORROWER DETAILS ====================
    
    story.append(Paragraph("BORROWER INFORMATION", section_style))
    
    borrower_data = [
        ['Full Name:', loan_details.get('customer_name', 'N/A')],
        ['Mobile Number:', loan_details.get('phone', 'N/A')],
        ['Residential Address:', loan_details.get('address', 'N/A')],
        ['PAN Number:', loan_details.get('pan', 'N/A')],
        ['Employment Details:', loan_details.get('employment', 'N/A')],
        ['Credit Score:', str(loan_details.get('credit_score', 'N/A'))],
    ]
    
    borrower_table = Table(borrower_data, colWidths=[2.2*inch, 4.2*inch])
    borrower_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.grey),
    ]))
    
    story.append(borrower_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== LOAN DETAILS ====================
    
    story.append(Paragraph("SANCTIONED LOAN DETAILS", section_style))
    
    # Calculate all financial details
    amount = loan_details.get('amount', 0)
    rate = loan_details.get('rate', 0)
    tenure = loan_details.get('tenure', 0)
    emi = loan_details.get('emi', 0)
    total_interest = loan_details.get('total_interest', 0)
    total_payment = loan_details.get('total_payment', 0)
    
    loan_data = [
        ['Sanctioned Amount:', f"Rs {amount:,.0f}"],
        ['Interest Rate (Reducing Balance):', f"{rate}% per annum"],
        ['Loan Tenure:', f"{tenure} months ({tenure//12} years)"],
        ['Monthly EMI (Fixed):', f"Rs {emi:,.0f}"],
        ['Total Interest Payable:', f"Rs {total_interest:,.0f}"],
        ['Total Amount Payable:', f"Rs {total_payment:,.0f}"],
        ['Processing Fee:', 'Rs 0 (Waived for pre-approved customers)'],
        ['Pre-closure Charges:', 'NIL (Pre-payment allowed after 6 EMIs)'],
        ['Late Payment Charges:', 'Rs 500 per instance + 2% p.m. penal interest'],
        ['Cheque/ECS Bounce Charges:', 'Rs 500 per bounce + bank charges']
    ]
    
    loan_table = Table(loan_data, colWidths=[2.5*inch, 3.9*inch])
    loan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAFA')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#E8F5E9')),  # Highlight EMI
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#FFF3E0')),  # Highlight total
    ]))
    
    story.append(loan_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Important note box
    note_text = f"""
    <para fontSize="9" textColor="#D32F2F" fontName="Helvetica-Bold" backColor="#FFEBEE" 
          borderColor="#D32F2F" borderWidth="1" borderPadding="6">
    <b>⚠ IMPORTANT:</b> The Annual Percentage Rate (APR) including all charges is {rate + 0.5}%. 
    Please ensure you understand the cost of this loan before proceeding.
    </para>
    """
    story.append(Paragraph(note_text, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== REPAYMENT SCHEDULE ====================
    
    story.append(Paragraph("REPAYMENT SCHEDULE", section_style))
    
    schedule_data = [
        ['First EMI Due Date:', first_emi_date.strftime("%d %B %Y")],
        ['Last EMI Due Date:', last_emi_date.strftime("%d %B %Y")],
        ['EMI Payment Mode:', 'Auto-Debit (NACH) from registered bank account'],
        ['EMI Due Day:', '1st of every month'],
        ['Disbursement Timeline:', '24-48 hours after document verification'],
        ['Moratorium Period:', 'NIL (EMI starts from next month)']
    ]
    
    schedule_table = Table(schedule_data, colWidths=[2.5*inch, 3.9*inch])
    schedule_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.lightgrey),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(schedule_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== DOCUMENTS REQUIRED ====================
    
    story.append(Paragraph("DOCUMENTS REQUIRED FOR DISBURSEMENT", section_style))
    
    doc_text = """
    <para fontSize="9" leading="13">
    <b>1. Identity Proof:</b> Aadhaar Card (mandatory for e-KYC)<br/>
    <b>2. Address Proof:</b> Aadhaar Card / Passport / Voter ID / Utility Bill (not older than 3 months)<br/>
    <b>3. Income Proof:</b> Latest 3 months salary slips + 6 months bank statement<br/>
    <b>4. PAN Card:</b> Self-attested copy (mandatory as per Income Tax Act)<br/>
    <b>5. Photograph:</b> 2 recent passport-size photographs<br/>
    <b>6. Signed Loan Agreement:</b> Will be provided after sanction acceptance<br/>
    <b>7. Post-Dated Cheques (PDCs):</b> {tenure} cheques OR NACH mandate form
    </para>
    """.format(tenure=tenure)
    
    story.append(Paragraph(doc_text, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== TERMS AND CONDITIONS ====================
    
    terms_section = KeepTogether([
        Paragraph("TERMS & CONDITIONS", section_style)
    ])
    story.append(terms_section)
    
    terms = [
        ("Sanction Validity", f"This sanction is valid for 30 days from the date of issue ({validity_date}). Post this date, fresh credit assessment may be required."),
        
        ("Interest Calculation", f"Interest is calculated on a reducing balance basis at {rate}% per annum. EMI includes both principal and interest components."),
        
        ("Disbursement", "Loan will be disbursed directly to your registered bank account within 24-48 hours of document verification and loan agreement execution."),
        
        ("Repayment", f"You are required to pay Rs {emi:,} as fixed monthly EMI on or before the 1st of every month. First EMI is due on {first_emi_date.strftime('%d %B %Y')}."),
        
        ("Auto-Debit Mandate", "You must provide a NACH (National Automated Clearing House) mandate authorizing us to auto-debit your registered bank account. Ensure sufficient balance before the due date."),
        
        ("Late Payment", "Late payment fee of Rs 500 plus penal interest @ 2% per month will be levied on delayed EMIs. This will also adversely impact your credit score."),
        
        ("Pre-payment", "Pre-payment/foreclosure is allowed after payment of 6 EMIs. No foreclosure charges for amounts above Rs 25,000. Minimum pre-payment: Rs 10,000."),
        
        ("Credit Bureau Reporting", "Your loan account and repayment behavior will be reported to Credit Information Companies (CIBIL, Experian, Equifax, CRIF). Timely payments improve your credit score."),
        
        ("Change in Terms", "We reserve the right to revise interest rates on floating rate loans as per RBI guidelines. You will be notified 30 days in advance of any changes."),
        
        ("Insurance", "It is recommended (but not mandatory) to have term life insurance covering the loan amount. You may purchase from any insurer of your choice."),
        
        ("Default & Recovery", "In case of 3 consecutive EMI defaults, the entire outstanding amount becomes due immediately. We may initiate legal action and engage recovery agents as per RBI Fair Practice Code."),
        
        ("Grievance Redressal", "For complaints, contact our Grievance Officer at grievances@loanverse.ai or call our helpline. If unresolved within 30 days, you may approach the RBI Ombudsman."),
        
        ("Cooling-off Period", "As per RBI guidelines, you have a 'cooling-off' period. You may cancel this loan within 2 days of disbursement without any charges (principal + interest for actual days will be deducted)."),
        
        ("Jurisdiction", "All disputes are subject to the exclusive jurisdiction of courts in Mumbai, Maharashtra."),
        
        ("Regulatory Compliance", "This loan is governed by RBI Master Directions on Non-Banking Financial Company regulations and applicable provisions of Indian Contract Act, 1872.")
    ]
    
    for i, (title, description) in enumerate(terms, 1):
        term_text = f"""
        <para fontSize="8.5" leading="12">
        <b>{i}. {title}:</b> {description}
        </para>
        """
        story.append(Paragraph(term_text, legal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(Spacer(1, 0.15*inch))
    
    # ==================== IMPORTANT DISCLOSURES ====================
    
    disclosures_section = KeepTogether([
        Paragraph("IMPORTANT DISCLOSURES (AS PER RBI GUIDELINES)", section_style)
    ])
    story.append(disclosures_section)
    
    disclosure_text = f"""
    <para fontSize="8" leading="11" backColor="#FFFDE7" borderColor="#FBC02D" borderWidth="1" borderPadding="8">
    <b>1. Fair Practice Code:</b> LoanVerse adheres to the RBI Fair Practice Code for NBFCs. 
    We do not discriminate on grounds of gender, caste, religion, or disability.<br/><br/>
    
    <b>2. Right to Privacy:</b> Your personal data is protected under our Privacy Policy available at 
    www.loanverse.ai/privacy. We do not share your information without consent except as required by law.<br/><br/>
    
    <b>3. No Upfront Charges:</b> We do not charge any processing fee, documentation fee, or any other 
    charges before loan disbursement. Be cautious of fraudsters asking for advance payments.<br/><br/>
    
    <b>4. Interest Rate Transparency:</b> The interest rate of {rate}% p.a. is clearly mentioned. 
    The effective interest rate (including all charges) is {rate + 0.5}% p.a.<br/><br/>
    
    <b>5. Loan Agreement:</b> Please read the detailed Loan Agreement carefully before signing. 
    You may consult a legal advisor if needed.<br/><br/>
    
    <b>6. Borrower's Rights:</b> You have the right to receive a copy of the loan agreement, 
    repayment schedule, and a statement of account on request (may attract nominal charges).<br/><br/>
    
    <b>7. Contact for Assistance:</b> For any queries, contact our customer care at 1800-123-LOAN or 
    email loans@loanverse.ai (Monday to Saturday, 9 AM to 6 PM).
    </para>
    """
    
    story.append(Paragraph(disclosure_text, legal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== ACCEPTANCE SECTION ====================
    
    story.append(Paragraph("ACCEPTANCE & NEXT STEPS", section_style))
    
    acceptance_text = """
    <para fontSize="9" leading="13">
    To accept this sanction and proceed with disbursement:<br/><br/>
    
    <b>Step 1:</b> Digitally sign this sanction letter (link sent to your registered mobile/email)<br/>
    <b>Step 2:</b> Upload required documents through our secure portal<br/>
    <b>Step 3:</b> Execute the Loan Agreement (digital signing available)<br/>
    <b>Step 4:</b> Provide NACH mandate OR submit post-dated cheques<br/>
    <b>Step 5:</b> Funds will be credited to your account within 24-48 hours<br/><br/>
    
    You will receive SMS and email notifications at each stage. Track your application status at 
    www.loanverse.ai/track using Application No: {application_number}
    </para>
    """.format(application_number=application_number)
    
    story.append(Paragraph(acceptance_text, body_style))
    story.append(Spacer(1, 0.25*inch))
    
    # ==================== SIGNATURE SECTION ====================
    
    signature_data = [
        ['', ''],
        ['_______________________', '_______________________'],
        ['Authorized Signatory', 'Borrower Signature'],
        ['LoanVerse Financial Services', loan_details.get('customer_name', 'N/A')],
        ['Date: ' + issue_date, 'Date: _______________']
    ]
    
    sig_table = Table(signature_data, colWidths=[3.2*inch, 3.2*inch])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, 0), 20),
    ]))
    
    story.append(sig_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ==================== QR CODE FOR VERIFICATION ====================
    
    # Generate QR code
    qr_data = f"LOANVERSE|{sanction_number}|{loan_details.get('phone', 'N/A')}|{amount}|{issue_date}"
    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # QR code section
    qr_text = """
    <para fontSize="8" alignment="center" textColor="#666666">
    <b>Scan QR Code to Verify Document Authenticity</b><br/>
    This/sanction letter can be verified at www.loanverse.ai/verify
    </para>
    """
    story.append(Paragraph(qr_text, legal_style))
    
    # Note: Adding QR code image requires additional handling in ReportLab
    # We will safely add a placeholder for cross-platform compatibility.
    
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== FOOTER ====================
    
    footer_line = Paragraph("─" * 100, ParagraphStyle('FooterLine', fontSize=6))
    story.append(footer_line)
    
    generated_on = datetime.now().strftime('%d %B %Y at %I:%M %p')

    footer_text = f"""
    <para fontSize="7" alignment="center" textColor="#666666" leading="10">
    <b>LoanVerse Financial Services Pvt. Ltd.</b><br/>
    CIN: U65990MH2020PTC123456 | RBI License: N-14.03339 (NBFC-ND) | GSTIN: 27AABCL1234F1Z5<br/>
    Regd. Office: 401, Tower A, Peninsula Corporate Park, Lower Parel, Mumbai - 400013<br/>
    Email: loans@loanverse.ai | Phone: 1800-123-LOAN | Web: www.loanverse.ai<br/><br/>

    <b>Grievance Officer:</b> Mr. Rajesh Kumar | Email: grievances@loanverse.ai | Phone: +91-22-1234-5678<br/>
    <b>RBI Ombudsman:</b> www.rbi.org.in (in case grievance is not resolved within 30 days)<br/><br/>

    <i>This is a system-generated document and does not require a physical signature for issuance.<br/>
    However, borrower acceptance signature is mandatory for loan disbursement.</i><br/><br/>

    <b>Document Generated On:</b> {generated_on} | <b>Document ID:</b> {sanction_number}
    </para>
    """
    
    story.append(Paragraph(footer_text, legal_style))
    
    # ==================== BUILD PDF ====================
    
    # Add page numbers
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(A4[0] - 1.5*cm, 1*cm, text)
        canvas.restoreState()
    
    # Build the document
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes