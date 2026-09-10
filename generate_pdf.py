import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
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
        if self._pageNumber > 1:
            self.drawString(54, 802, "Campus Resource Booking System — Project Report")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 794, 540, 794)
        
        self.drawString(54, 32, "Submitted by Mugunth | CSE Department")
        self.drawRightString(540, 32, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 44, 540, 44)
        self.restoreState()

def create_humanized_report(output_filename="PROJECT_REPORT.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=50,
        rightMargin=50,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()
    
    primary = colors.HexColor("#1e40af")    # Clean navy
    dark = colors.HexColor("#1e293b")       # Dark slate text
    muted = colors.HexColor("#475569")      # Muted gray text
    border = colors.HexColor("#cbd5e1")     # Soft border

    title_style = ParagraphStyle(
        'Title', fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=primary, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'Subtitle', fontName='Helvetica', fontSize=10, leading=14, textColor=muted, spaceAfter=10
    )
    h1 = ParagraphStyle(
        'H1', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=primary, spaceBefore=10, spaceAfter=4, keepWithNext=True
    )
    h2 = ParagraphStyle(
        'H2', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=dark, spaceBefore=7, spaceAfter=3, keepWithNext=True
    )
    p = ParagraphStyle(
        'Body', fontName='Helvetica', fontSize=9, leading=13, textColor=dark, spaceAfter=5
    )
    th = ParagraphStyle(
        'TH', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.white
    )
    td = ParagraphStyle(
        'TD', fontName='Helvetica', fontSize=8, leading=11, textColor=dark
    )
    td_b = ParagraphStyle(
        'TDB', fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=dark
    )

    story = []

    # Title & Quick Info
    story.append(Paragraph("Campus Resource Booking System", title_style))
    story.append(Paragraph("Full-Stack Web Development Project Report | Python Flask + MongoDB + Vanilla JS + Docker", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary, spaceAfter=8))

    # Project Links Table
    info_data = [
        [Paragraph("Student Name:", td_b), Paragraph("Mugunth", td), Paragraph("Live Demo:", td_b), Paragraph("<font color='#1d4ed8'><u>campus-resource-booking-cqt7.onrender.com</u></font>", td)],
        [Paragraph("Branch / Tech:", td_b), Paragraph("Computer Science & Engineering", td), Paragraph("GitHub Repo:", td_b), Paragraph("<font color='#1d4ed8'><u>github.com/Mugu1825/Campus-Resource-Booking</u></font>", td)],
        [Paragraph("Deployment:", td_b), Paragraph("Docker on Render Cloud", td), Paragraph("Database:", td_b), Paragraph("MongoDB Atlas Cloud (Replica Set)", td)]
    ]
    t_info = Table(info_data, colWidths=[80, 165, 80, 170])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 8))

    # 1. Why I Built This
    story.append(Paragraph("1. Project Motivation & Problem Statement", h1))
    story.append(Paragraph(
        "In our college, booking shared facilities—like computer labs, seminar halls, projectors, or the auditorium—is still handled through physical registers or informal messages. This causes frequent scheduling clashes, confusion over who approved what, and no easy way to check if a lab is free for an upcoming slot.",
        p
    ))
    story.append(Paragraph(
        "I built this project to solve that with a clean, fully functional booking website. Rather than making a basic CRUD app with just one generic user type, I designed it around real campus requirements: <b>3 separate user roles</b> (Student, Staff, and Admin), <b>automatic department detection</b> from roll numbers, <b>hourly time slot checking</b>, and <b>preventing double-bookings</b> automatically.",
        p
    ))

    # 2. How the System Works (Roles & Flow)
    story.append(Paragraph("2. User Roles & Workflow", h1))
    
    roles_data = [
        [Paragraph("Role", th), Paragraph("How It Works in the App", th), Paragraph("Key Permissions & Rules", th)],
        [
            Paragraph("<b>Student</b>", td_b),
            Paragraph("Registers using their college roll number (e.g. <code>25CSE1011</code>). The app checks the format and automatically detects their department. They can browse labs/halls, check free slots, book, and cancel pending requests.", td),
            Paragraph("• Regular booking: Max 4 hours (same day)<br/>• Hackathon booking: Up to 48 hours<br/>• Can cancel only their own pending requests", td)
        ],
        [
            Paragraph("<b>Staff</b>", td_b),
            Paragraph("Registers with department. Their account is set to 'pending' until the Admin reviews and approves it. Once active, staff can manage standard labs/rooms and approve student bookings for their department.", td),
            Paragraph("• Can approve standard resources<br/>• <i>Cannot</i> create or approve premium halls or hackathons (preventing misuse)", td)
        ],
        [
            Paragraph("<b>Admin</b>", td_b),
            Paragraph("The superuser account. Approves new staff accounts, manages all resources (standard and premium), has final say on multi-day hackathons and high-value spaces (like the main auditorium), and can change user roles.", td),
            Paragraph("• Full system authority<br/>• Approves premium and hackathon bookings<br/>• Monitors live stats and user accounts", td)
        ]
    ]
    t_roles = Table(roles_data, colWidths=[65, 230, 200])
    t_roles.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_roles)
    story.append(Spacer(1, 8))

    # 3. Tech Stack & Architecture
    story.append(Paragraph("3. Technology Choices & Architecture", h1))
    story.append(Paragraph(
        "• <b>Backend (Python & Flask):</b> I chose Flask because it is lightweight, fast to set up, and makes writing clean REST API routes straightforward. Password security uses <code>flask-bcrypt</code> (salted hashing), and sessions use stateless <code>flask-jwt-extended</code> tokens.<br/>"
        "• <b>Database (MongoDB Atlas):</b> I used MongoDB because college resources and bookings naturally fit JSON documents. Using Atlas gives a free cloud cluster with automatic TLS encryption and connection pooling.<br/>"
        "• <b>Frontend (Pure HTML5, CSS3, Vanilla JS):</b> I intentionally avoided bulky frameworks like React or Angular to keep the app fast, clean, and dependency-free. Responsive CSS and modular JavaScript files handle the UI.<br/>"
        "• <b>Containerization (Docker & Nginx):</b> I packaged both the frontend and backend into a single Docker container. Nginx serves the static HTML/CSS/JS and acts as a reverse proxy forwarding <code>/api/*</code> calls to Gunicorn. This eliminated all CORS headaches and allowed hosting everything on Render's free tier under one single URL.",
        p
    ))

    # 4. Database Design
    story.append(Paragraph("4. Database Design (Collections)", h1))
    db_data = [
        [Paragraph("Collection", th), Paragraph("Important Fields", th), Paragraph("Description & Purpose", th)],
        [
            Paragraph("<b>users</b>", td_b),
            Paragraph("<code>name, email, password, role, account_status, register_no, department</code>", td),
            Paragraph("Stores user profiles. Student accounts store roll number (unique). Staff accounts track approval status (<code>pending</code> / <code>active</code>). Passwords are never plain text.", td)
        ],
        [
            Paragraph("<b>resources</b>", td_b),
            Paragraph("<code>name, type, tier, location, capacity, is_available</code>", td),
            Paragraph("Campus assets. <code>tier</code> is either 'standard' (regular labs) or 'premium' (auditorium / compute cluster). <code>is_available</code> allows temporary maintenance takedowns.", td)
        ],
        [
            Paragraph("<b>bookings</b>", td_b),
            Paragraph("<code>user_id, resource_id, date_start, date_end, start_slot, end_slot, is_hackathon, status</code>", td),
            Paragraph("Reservation records. Connects user to resource. Tracks approval status (<code>pending</code>, <code>approved</code>, <code>rejected</code>, <code>cancelled</code>).", td)
        ]
    ]
    t_db = Table(db_data, colWidths=[70, 205, 220])
    t_db.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_db)
    story.append(Spacer(1, 8))

    # 5. Key Features & Implementation Details
    story.append(Paragraph("5. Key Features & Logic Implemented", h1))
    story.append(Paragraph(
        "<b>A. Roll Number Format Verification:</b><br/>"
        "Students must register with a valid college roll number format: 2-digit year + 3-letter department code + 4 digits (e.g., <code>25CSE1011</code>). Regex: <code>^\\d{2}(CSE|ECE|EEE|MEE|INT|CIV|CHE|AER|BIO|MBA|MCA)\\d{4}$</code>. The backend extracts characters 2-4 and auto-fills their department.",
        p
    ))
    story.append(Paragraph(
        "<b>B. Double-Booking Conflict Engine:</b><br/>"
        "Before creating any booking, the backend checks for existing requests on the same resource where status is <code>pending</code> or <code>approved</code>. If dates overlap, it compares slot indices from <code>09:00</code> to <code>21:00</code>. If an overlap is detected, the request is immediately rejected with a clear message.",
        p
    ))
    story.append(Paragraph(
        "<b>C. Real-time Slot Availability Grid:</b><br/>"
        "When students click 'Check Availability' on any lab, an interactive visual slot grid opens for the selected date. Free slots appear in green outline, booked slots appear in red, and clicked slots highlight in blue. Clicking 'Book this slot' auto-fills the booking form.",
        p
    ))
    story.append(Paragraph(
        "<b>D. Dual Ruleset (Regular vs. Hackathon):</b><br/>"
        "Regular bookings are limited to 4 hours on the same date. For hackathons, students check 'Is Hackathon', enter the event name, and can reserve multi-day blocks up to 48 hours (routed exclusively to Admin for review).",
        p
    ))

    # 6. Challenges Faced and How I Solved Them
    story.append(Paragraph("6. Challenges Faced & Solutions", h1))
    story.append(Paragraph(
        "• <b>CORS & Port Configuration in Deployment:</b> Initially, running frontend and backend as separate Render services created cross-origin errors and needed two separate URLs. I resolved this by writing a custom Dockerfile with Nginx serving the static frontend and reverse-proxying <code>/api/*</code> to Gunicorn. This gave a unified single-URL deployment with zero CORS issues.<br/>"
        "• <b>MongoDB Eager Index Crash on Startup:</b> Creating indexes at application startup caused Flask to crash when MongoDB Atlas had not finished connecting. I moved index creation into a one-shot <code>@app.before_request</code> hook so the server starts cleanly even during cold boots.<br/>"
        "• <b>Safe Role Gating:</b> To prevent staff members from approving high-value auditoriums or overriding multi-day events, I wrote custom Flask decorators (<code>@staff_required</code> and <code>@admin_required</code>) that inspect the JWT token claims before route execution.",
        p
    ))

    # 7. Testing & Verification Summary
    story.append(Paragraph("7. Testing & Verification Summary", h1))
    story.append(Paragraph(
        "To make sure the entire project works reliably, I wrote an automated test script (<code>backend/tests/verify_codebase.py</code>) that runs <b>31 integration test cases</b> covering:<br/>"
        "1. Public endpoints (Health check, department list)<br/>"
        "2. Roll number validation (Rejecting invalid codes, auto-extracting department)<br/>"
        "3. Staff approval lifecycle (Pending state $\\rightarrow$ Login blocked $\\rightarrow$ Admin approval $\\rightarrow$ Login success)<br/>"
        "4. Resource security (Staff blocked from creating premium resources)<br/>"
        "5. Booking rules (4-hour limit enforcement, double-booking rejection, hackathon rules)<br/>"
        "6. Student self-cancellation (Pending cancel allowed, approved cancel blocked)<br/>"
        "<b>Result: 31 / 31 tests passed (100% success rate).</b>",
        p
    ))

    # 8. What I Learned & Conclusion
    story.append(Paragraph("8. Conclusion & What I Learned", h1))
    story.append(Paragraph(
        "Working on this project gave me practical, hands-on experience building a real-world web system from start to finish. I learned how to structure REST APIs with Flask blueprints, model relational concepts inside MongoDB, write clean vanilla JavaScript for interactive UI elements, containerize applications using Docker and Nginx, and deploy production code to the cloud.",
        p
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Humanized report compiled into: {output_filename}")

if __name__ == '__main__':
    create_humanized_report()
