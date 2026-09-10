import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 800, "Campus Resource Booking System (CRBS) — Technical Project Report")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 792, 540, 792)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(540, 36, page_text)
        self.drawString(54, 36, "Confidential & Proprietary — Campus Resource Booking System")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 540, 48)
        self.restoreState()

def create_report(output_filename="PROJECT_REPORT.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    primary_color = colors.HexColor("#1e3a8a")     # Deep blue
    secondary_color = colors.HexColor("#2563eb")   # Bright blue
    text_dark = colors.HexColor("#0f172a")         # Slate 900
    text_muted = colors.HexColor("#475569")        # Slate 600
    bg_light = colors.HexColor("#f8fafc")          # Slate 50
    border_color = colors.HexColor("#cbd5e1")      # Slate 300

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=text_muted,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=secondary_color,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=text_dark,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'Body_Bold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    code_block_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#1e293b")
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=text_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    story = []

    # ==========================================
    # COVER HEADER BLOCK
    # ==========================================
    story.append(Paragraph("CAMPUS RESOURCE BOOKING SYSTEM", title_style))
    story.append(Paragraph("Comprehensive Technical & Architectural Project Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=12))

    # Meta Table
    meta_data = [
        [Paragraph("Author:", table_cell_bold), Paragraph("Mugunth", table_cell_style),
         Paragraph("System Version:", table_cell_bold), Paragraph("1.0.0 (Production Release)", table_cell_style)],
        [Paragraph("Live URL:", table_cell_bold), Paragraph("<font color='#2563eb'><u>https://campus-resource-booking-cqt7.onrender.com</u></font>", table_cell_style),
         Paragraph("Platform:", table_cell_bold), Paragraph("Render Cloud (Docker Web Service)", table_cell_style)],
        [Paragraph("Repository:", table_cell_bold), Paragraph("<font color='#2563eb'><u>github.com/Mugu1825/Campus-Resource-Booking</u></font>", table_cell_style),
         Paragraph("Database:", table_cell_bold), Paragraph("MongoDB Atlas (M0 ReplicaSet)", table_cell_style)],
        [Paragraph("Core Stack:", table_cell_bold), Paragraph("Flask 3.0, Nginx, Gunicorn, PyMongo, HTML5/CSS3/JS", table_cell_style),
         Paragraph("Audit Status:", table_cell_bold), Paragraph("<font color='#16a34a'><b>31 / 31 Tests Passed (100%)</b></font>", table_cell_style)]
    ]
    meta_table = Table(meta_data, colWidths=[80, 180, 90, 136])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # ==========================================
    # SECTION 1: EXECUTIVE SUMMARY
    # ==========================================
    story.append(Paragraph("1. Executive Summary & Problem Analysis", h1_style))
    story.append(Paragraph(
        "Modern educational campuses maintain dozens of shared academic assets—including machine learning computing laboratories, specialized engineering workshops, smart conference halls, and central auditoriums. In the absence of an automated system, scheduling these resources relies on manual paper logs, informal faculty requests, and disparate chat groups.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Key Operational Deficiencies in Legacy Systems:</b><br/>"
        "• <b>Resource Collision & Double Booking:</b> Concurrent requests submitted via different channels result in scheduling conflicts on the day of occupancy.<br/>"
        "• <b>Absence of Format Verification:</b> Traditional forms allow students to submit unverified roll numbers or misspell department codes, corrupting academic records.<br/>"
        "• <b>Unbalanced Governance:</b> Administrators are overburdened with routine classroom requests, while high-value assets (such as GPU clusters) lack strict scrutiny.<br/>"
        "• <b>Hackathon Incompatibility:</b> Standard tools cannot distinguish between a 1-hour study group and an intensive 48-hour departmental hackathon.",
        body_style
    ))
    story.append(Paragraph(
        "The <b>Campus Resource Booking System (CRBS)</b> addresses these issues through a cloud-native, containerized architecture. It enforces strict academic register number formatting, 3-tier Role-Based Access Control (RBAC), algorithmic collision detection, dynamic hourly slot availability calculation, and hierarchical approval workflows.",
        body_style
    ))

    # ==========================================
    # SECTION 2: OBJECTIVES & FUNCTIONAL SCOPE
    # ==========================================
    story.append(Paragraph("2. Objectives & Functional Scope", h1_style))
    
    scope_data = [
        [Paragraph("Role / Feature", table_header_style), Paragraph("Functional Permissions & Responsibilities", table_header_style), Paragraph("Time Restrictions", table_header_style)],
        [
            Paragraph("<b>Student</b>", table_cell_style),
            Paragraph("• Self-registration with strict roll number regex validation.<br/>• Automatic department code extraction.<br/>• Dynamic hourly slot grid inspection.<br/>• Booking submission with conflict checks.<br/>• Cancellation of self-initiated pending requests.", table_cell_style),
            Paragraph("• Regular: Max 4 hours (same-day).<br/>• Hackathon: Max 48 hours (multi-day, event name required).", table_cell_style)
        ],
        [
            Paragraph("<b>Staff</b>", table_cell_style),
            Paragraph("• Self-registration in <code>pending</code> status (admin approval required).<br/>• Standard resource management (Add/Edit/Delete/Availability Toggle).<br/>• Booking queue review & approval for <b>standard</b> tier resources.", table_cell_style),
            Paragraph("• Restricted to standard tier resources only.<br/>• Forbidden from approving premium or hackathon bookings.", table_cell_style)
        ],
        [
            Paragraph("<b>Admin</b>", table_cell_style),
            Paragraph("• System-wide master oversight.<br/>• Staff account review, activation, and rejection.<br/>• Universal resource management (Standard and Premium tiers).<br/>• Sole approval authority for Premium bookings & Hackathons.<br/>• Global user role management & real-time metric analytics.", table_cell_style),
            Paragraph("• Unrestricted administrative authority.", table_cell_style)
        ]
    ]
    scope_table = Table(scope_data, colWidths=[70, 276, 140])
    scope_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(scope_table)

    # ==========================================
    # SECTION 3: SYSTEM ARCHITECTURE
    # ==========================================
    story.append(Paragraph("3. System Architecture & Containerization", h1_style))
    story.append(Paragraph(
        "CRBS implements a <b>Single-Container Micro-Architecture</b> that houses both the web server/reverse proxy and the application WSGI server inside a single Docker image.",
        body_style
    ))

    arch_diagram = """
+-----------------------------------------------------------------------------------+
|                            CLIENT BROWSER (HTTPS)                                 |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
|                     DOCKER CONTAINER (Render Cloud Web Service)                   |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                   NGINX REVERSE PROXY (:80 or Render's $PORT)                |  |
|  +-----------------------------------------------------------------------------+  |
|          |                                                    |                   |
|          |  [Static Routes: /*, /css/*, /js/*]                |  [API: /api/*]    |
|          v                                                    v                   |
|  +---------------------------+        +----------------------------------------+  |
|  |  FRONTEND STATIC ASSETS   |        |  GUNICORN WSGI ENGINE (127.0.0.1:5000) |  |
|  |  HTML5, CSS3, Vanilla JS  |        |  Flask Application Blueprints          |  |
|  +---------------------------+        +----------------------------------------+  |
+-----------------------------------------------------------------------------------+
                                       |
                                       v  [Encrypted TLS 1.3 / Port 27017]
+-----------------------------------------------------------------------------------+
|                        MONGODB ATLAS CLOUD REPLICASET                             |
|               Collections: users | resources | bookings                           |
+-----------------------------------------------------------------------------------+
"""
    diag_table = Table([[Paragraph(f"<pre>{arch_diagram.strip()}</pre>", code_block_style)]], colWidths=[486])
    diag_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>Architectural Highlights:</b><br/>"
        "• <b>Zero-CORS Domain Unification:</b> Nginx routes both frontend web assets and <code>/api/*</code> on the exact same origin, eliminating browser pre-flight delays.<br/>"
        "• <b>Dynamic Port Adaptation:</b> At boot, <code>entrypoint.sh</code> reads Render's dynamic <code>$PORT</code> variable (defaulting to 80 locally) and injects it into Nginx.<br/>"
        "• <b>Isolated Flask Loopback:</b> Gunicorn runs securely on <code>127.0.0.1:5000</code> shielded from direct public exposure.",
        body_style
    ))

    # ==========================================
    # SECTION 4: DATABASE ARCHITECTURE
    # ==========================================
    story.append(Paragraph("4. Database Architecture & Data Models", h1_style))
    story.append(Paragraph(
        "MongoDB Atlas was selected for its schema flexibility, native replica set high availability, and indexing capabilities. The schema design models three primary collections:",
        body_style
    ))

    # Collections Table
    schema_data = [
        [Paragraph("Collection", table_header_style), Paragraph("Field Name", table_header_style), Paragraph("Type", table_header_style), Paragraph("Constraints & Business Description", table_header_style)],
        [
            Paragraph("<b>users</b>", table_cell_style),
            Paragraph("<code>_id<br/>name<br/>email<br/>password<br/>role<br/>account_status<br/>register_no<br/>department<br/>created_at</code>", table_cell_style),
            Paragraph("ObjectId<br/>string<br/>string<br/>string<br/>string<br/>string<br/>string<br/>string<br/>datetime", table_cell_style),
            Paragraph("Primary Key<br/>Full user name<br/>Unique index, case-insensitive<br/>Salted Bcrypt hash (never plaintext)<br/>'student' | 'staff' | 'admin'<br/>'active' | 'pending' | 'rejected'<br/>Unique sparse index. Enforces regex: <code>^\\d{2}[A-Z]{3}\\d{4}$</code><br/>3-character department code (e.g. CSE, ECE)<br/>UTC creation timestamp", table_cell_style)
        ],
        [
            Paragraph("<b>resources</b>", table_cell_style),
            Paragraph("<code>_id<br/>name<br/>type<br/>tier<br/>location<br/>capacity<br/>is_available<br/>created_at</code>", table_cell_style),
            Paragraph("ObjectId<br/>string<br/>string<br/>string<br/>string<br/>int<br/>boolean<br/>datetime", table_cell_style),
            Paragraph("Primary Key<br/>Descriptive title (e.g. AI / ML Lab 1)<br/>'lab' | 'room' | 'equipment' | 'auditorium'<br/>'standard' (staff/admin) | 'premium' (admin only)<br/>Physical campus location (e.g. CS Block 2nd Floor)<br/>Maximum seating/equipment capacity<br/>Global availability toggle switch<br/>UTC creation timestamp", table_cell_style)
        ],
        [
            Paragraph("<b>bookings</b>", table_cell_style),
            Paragraph("<code>_id<br/>user_id<br/>resource_id<br/>date_start<br/>date_end<br/>start_slot<br/>end_slot<br/>is_hackathon<br/>hackathon_event<br/>status<br/>approved_by<br/>created_at</code>", table_cell_style),
            Paragraph("ObjectId<br/>ObjectId<br/>ObjectId<br/>string<br/>string<br/>string<br/>string<br/>boolean<br/>string<br/>string<br/>string<br/>datetime", table_cell_style),
            Paragraph("Primary Key<br/>Foreign Key referencing users collection<br/>Foreign Key referencing resources collection<br/>Start date (YYYY-MM-DD)<br/>End date (YYYY-MM-DD)<br/>Starting slot from ['09:00', ..., '21:00']<br/>Ending slot from ['09:00', ..., '21:00']<br/>Flag indicating multi-day hackathon event<br/>Required event title if hackathon=True<br/>'pending' | 'approved' | 'rejected' | 'cancelled'<br/>User ID of approving staff/admin<br/>UTC reservation timestamp", table_cell_style)
        ]
    ]
    schema_table = Table(schema_data, colWidths=[65, 85, 65, 271])
    schema_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(schema_table)

    # ==========================================
    # SECTION 5: BUSINESS LOGIC & CONFLICT ENGINE
    # ==========================================
    story.append(Paragraph("5. Scheduling Logic & Conflict Prevention Engine", h1_style))
    story.append(Paragraph(
        "CRBS prevents double booking using an algorithmic validation pipeline implemented in <code>backend/routes/bookings.py</code>:",
        body_style
    ))
    story.append(Paragraph(
        "1. <b>Active State Filter:</b> Only reservations with <code>status IN ['pending', 'approved']</code> trigger conflict evaluations.<br/>"
        "2. <b>Date Interval Overlap Verification:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>Conflict occurs if: (date_start &lt;= b_date_end) AND (date_end &gt;= b_date_start)</code><br/>"
        "3. <b>Time Slot Interval Verification (Single Day):</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;For single-day reservations, start and end slots are mapped to indices in the operational slot array <code>['09:00', '10:00', ..., '21:00']</code>. A collision is flagged if:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>(start_index &lt; b_end_index) AND (end_index &gt; b_start_index)</code><br/>"
        "4. <b>Hackathon Preemption:</b> If either booking is marked as a multi-day hackathon, all slots across the reserved date range are locked.",
        body_style
    ))

    # ==========================================
    # SECTION 6: REST API SPECIFICATION
    # ==========================================
    story.append(Paragraph("6. RESTful API Specification (23 Endpoints)", h1_style))

    api_data = [
        [Paragraph("Module", table_header_style), Paragraph("Method", table_header_style), Paragraph("Endpoint URL", table_header_style), Paragraph("Auth Level", table_header_style), Paragraph("Description", table_header_style)],
        # Auth
        [Paragraph("Auth", table_cell_bold), Paragraph("POST", table_cell_style), Paragraph("<code>/api/auth/register/student</code>", table_cell_style), Paragraph("Public", table_cell_style), Paragraph("Registers student; verifies register number regex.", table_cell_style)],
        [Paragraph("Auth", table_cell_bold), Paragraph("POST", table_cell_style), Paragraph("<code>/api/auth/register/staff</code>", table_cell_style), Paragraph("Public", table_cell_style), Paragraph("Registers staff account in pending status.", table_cell_style)],
        [Paragraph("Auth", table_cell_bold), Paragraph("POST", table_cell_style), Paragraph("<code>/api/auth/login</code>", table_cell_style), Paragraph("Public", table_cell_style), Paragraph("Authenticates credentials; issues signed JWT.", table_cell_style)],
        [Paragraph("Auth", table_cell_bold), Paragraph("GET", table_cell_style), Paragraph("<code>/api/auth/departments</code>", table_cell_style), Paragraph("Public", table_cell_style), Paragraph("Returns list of supported 3-letter department codes.", table_cell_style)],
        # Resources
        [Paragraph("Resources", table_cell_bold), Paragraph("GET", table_cell_style), Paragraph("<code>/api/resources/</code>", table_cell_style), Paragraph("Public", table_cell_style), Paragraph("Lists all resources with tier/type filtering.", table_cell_style)],
        [Paragraph("Resources", table_cell_bold), Paragraph("GET", table_cell_style), Paragraph("<code>/api/resources/&lt;id&gt;</code>", table_cell_style), Paragraph("Public", table_cell_style), Paragraph("Fetches single resource metadata.", table_cell_style)],
        [Paragraph("Resources", table_cell_bold), Paragraph("GET", table_cell_style), Paragraph("<code>/api/resources/&lt;id&gt;/availability</code>", table_cell_style), Paragraph("Public", table_cell_style), Paragraph("Returns booked & available hourly slots for a date.", table_cell_style)],
        [Paragraph("Resources", table_cell_bold), Paragraph("POST", table_cell_style), Paragraph("<code>/api/resources/</code>", table_cell_style), Paragraph("Staff / Admin", table_cell_style), Paragraph("Creates resource. Staff limited to standard tier.", table_cell_style)],
        [Paragraph("Resources", table_cell_bold), Paragraph("PUT", table_cell_style), Paragraph("<code>/api/resources/&lt;id&gt;</code>", table_cell_style), Paragraph("Staff / Admin", table_cell_style), Paragraph("Updates existing resource attributes.", table_cell_style)],
        [Paragraph("Resources", table_cell_bold), Paragraph("PATCH", table_cell_style), Paragraph("<code>/api/resources/&lt;id&gt;/availability</code>", table_cell_style), Paragraph("Staff / Admin", table_cell_style), Paragraph("Toggles active availability flag.", table_cell_style)],
        [Paragraph("Resources", table_cell_bold), Paragraph("DELETE", table_cell_style), Paragraph("<code>/api/resources/&lt;id&gt;</code>", table_cell_style), Paragraph("Staff / Admin", table_cell_style), Paragraph("Deletes resource if no active bookings exist.", table_cell_style)],
        # Bookings
        [Paragraph("Bookings", table_cell_bold), Paragraph("GET", table_cell_style), Paragraph("<code>/api/bookings/</code>", table_cell_style), Paragraph("Auth (All)", table_cell_style), Paragraph("Role-aware list (Student: own; Staff: std; Admin: all).", table_cell_style)],
        [Paragraph("Bookings", table_cell_bold), Paragraph("GET", table_cell_style), Paragraph("<code>/api/bookings/my</code>", table_cell_style), Paragraph("Student", table_cell_style), Paragraph("Returns authenticated student's bookings.", table_cell_style)],
        [Paragraph("Bookings", table_cell_bold), Paragraph("POST", table_cell_style), Paragraph("<code>/api/bookings/</code>", table_cell_style), Paragraph("Student", table_cell_style), Paragraph("Creates booking request with collision checks.", table_cell_style)],
        [Paragraph("Bookings", table_cell_bold), Paragraph("PATCH", table_cell_style), Paragraph("<code>/api/bookings/&lt;id&gt;/approve</code>", table_cell_style), Paragraph("Staff / Admin", table_cell_style), Paragraph("Approves booking (Staff blocked on premium/hack).", table_cell_style)],
        [Paragraph("Bookings", table_cell_bold), Paragraph("PATCH", table_cell_style), Paragraph("<code>/api/bookings/&lt;id&gt;/reject</code>", table_cell_style), Paragraph("Staff / Admin", table_cell_style), Paragraph("Rejects booking request.", table_cell_style)],
        [Paragraph("Bookings", table_cell_bold), Paragraph("PATCH", table_cell_style), Paragraph("<code>/api/bookings/&lt;id&gt;/cancel</code>", table_cell_style), Paragraph("Student / Admin", table_cell_style), Paragraph("Cancels pending reservation.", table_cell_style)],
        # Admin
        [Paragraph("Admin", table_cell_bold), Paragraph("GET", table_cell_style), Paragraph("<code>/api/admin/stats</code>", table_cell_style), Paragraph("Admin Only", table_cell_style), Paragraph("Aggregates real-time counts across the database.", table_cell_style)],
        [Paragraph("Admin", table_cell_bold), Paragraph("GET", table_cell_style), Paragraph("<code>/api/admin/users</code>", table_cell_style), Paragraph("Admin Only", table_cell_style), Paragraph("Retrieves all registered user profiles.", table_cell_style)],
        [Paragraph("Admin", table_cell_bold), Paragraph("GET", table_cell_style), Paragraph("<code>/api/admin/pending-staff</code>", table_cell_style), Paragraph("Admin Only", table_cell_style), Paragraph("Lists staff accounts awaiting activation.", table_cell_style)],
        [Paragraph("Admin", table_cell_bold), Paragraph("PATCH", table_cell_style), Paragraph("<code>/api/admin/staff/&lt;id&gt;/approve</code>", table_cell_style), Paragraph("Admin Only", table_cell_style), Paragraph("Activates staff account for login.", table_cell_style)],
        [Paragraph("Admin", table_cell_bold), Paragraph("PATCH", table_cell_style), Paragraph("<code>/api/admin/staff/&lt;id&gt;/reject</code>", table_cell_style), Paragraph("Admin Only", table_cell_style), Paragraph("Rejects staff registration.", table_cell_style)],
        [Paragraph("Admin", table_cell_bold), Paragraph("PATCH", table_cell_style), Paragraph("<code>/api/admin/users/&lt;id&gt;/role</code>", table_cell_style), Paragraph("Admin Only", table_cell_style), Paragraph("Modifies user permissions (student, staff, admin).", table_cell_style)]
    ]
    api_table = Table(api_data, colWidths=[55, 45, 140, 66, 180])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(api_table)

    # ==========================================
    # SECTION 7: QUALITY ASSURANCE & AUDIT
    # ==========================================
    story.append(Paragraph("7. Quality Assurance & Automated Verification Audit", h1_style))
    story.append(Paragraph(
        "To verify system integrity, an automated test suite (<code>backend/tests/verify_codebase.py</code>) was executed against the production environment. All 31 test cases passed:",
        body_style
    ))

    audit_data = [
        [Paragraph("Test Suite Category", table_header_style), Paragraph("Test Cases Evaluated", table_header_style), Paragraph("Success Rate", table_header_style), Paragraph("Audit Result", table_header_style)],
        [Paragraph("Public APIs & Health Check", table_cell_style), Paragraph("<code>/api/health</code>, <code>/api/auth/departments</code>", table_cell_style), Paragraph("2 / 2 (100%)", table_cell_style), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", table_cell_style)],
        [Paragraph("Roll Number Validation", table_cell_style), Paragraph("Regex matching, non-compliant rejection, department parsing", table_cell_style), Paragraph("4 / 4 (100%)", table_cell_style), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", table_cell_style)],
        [Paragraph("Staff Approval Lifecycle", table_cell_style), Paragraph("Pending creation, login gate (403), admin activation, login success", table_cell_style), Paragraph("6 / 6 (100%)", table_cell_style), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", table_cell_style)],
        [Paragraph("Resource Tier Guards", table_cell_style), Paragraph("Staff standard creation, staff premium block (403), admin creation", table_cell_style), Paragraph("3 / 3 (100%)", table_cell_style), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", table_cell_style)],
        [Paragraph("Scheduling & Conflict Engine", table_cell_style), Paragraph("Max 4h cap, multi-day regular block, 48h hackathon, double-booking block", table_cell_style), Paragraph("7 / 7 (100%)", table_cell_style), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", table_cell_style)],
        [Paragraph("Hierarchical Approval Routing", table_cell_style), Paragraph("Staff standard approve, staff premium block (403), admin overrides", table_cell_style), Paragraph("5 / 5 (100%)", table_cell_style), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", table_cell_style)],
        [Paragraph("Student Self-Service", table_cell_style), Paragraph("Pending cancellation, approved cancellation block (400)", table_cell_style), Paragraph("2 / 2 (100%)", table_cell_style), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", table_cell_style)],
        [Paragraph("Dynamic Availability Endpoint", table_cell_style), Paragraph("Live calculation of booked vs available time slots", table_cell_style), Paragraph("1 / 1 (100%)", table_cell_style), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", table_cell_style)],
        [Paragraph("Admin Overview Aggregation", table_cell_style), Paragraph("Real-time database count aggregation", table_cell_style), Paragraph("1 / 1 (100%)", table_cell_style), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", table_cell_style)],
        [Paragraph("<b>TOTAL VERIFICATION AUDIT</b>", table_cell_bold), Paragraph("<b>Comprehensive End-to-End System Evaluation</b>", table_cell_bold), Paragraph("<b>31 / 31 (100%)</b>", table_cell_bold), Paragraph("<font color='#16a34a'><b>ALL PASSED</b></font>", table_cell_style)]
    ]
    audit_table = Table(audit_data, colWidths=[130, 200, 80, 76])
    audit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(audit_table)

    # ==========================================
    # SECTION 8: CONCLUSION & ROADMAP
    # ==========================================
    story.append(Paragraph("8. Conclusion & Future Roadmap", h1_style))
    story.append(Paragraph(
        "The Campus Resource Booking System (CRBS) provides an automated, secure platform for university scheduling. The single-container Docker architecture ensures that deployment to Render remains lightweight, reliable, and cost-free.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Future Roadmap:</b><br/>"
        "1. <b>Automated Notification Dispatcher:</b> Integration with transactional email/SMS services (SendGrid/Twilio) for status change alerts.<br/>"
        "2. <b>Hardware IoT Smart Lock Integration:</b> Generating dynamic QR codes or RFID access synced with approved booking windows to physically unlock doors.<br/>"
        "3. <b>Calendar Sync:</b> Exporting approved reservations directly to Google Calendar and Microsoft Outlook via standard <code>.ics</code> feeds.",
        body_style
    ))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report successfully compiled into: {output_filename}")

if __name__ == '__main__':
    create_report()
