import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
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
            self.drawString(50, 802, "BACSE344 - Cloud Infrastructure & Architecture | Digital Assignment 3")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(50, 794, 545, 794)
        
        self.drawString(50, 32, "Mugunth | Campus Resource Booking System | Assignment-3")
        self.drawRightString(545, 32, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(50, 44, 545, 44)
        self.restoreState()

def create_assignment3_report(output_filename="ASSIGNMENT_3_REPORT.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=48,
        rightMargin=48,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()
    
    primary = colors.HexColor("#1e3a8a")     # Deep academic blue
    secondary = colors.HexColor("#0284c7")   # Bright cyan
    dark = colors.HexColor("#0f172a")        # Text dark
    muted = colors.HexColor("#475569")       # Text muted
    border = colors.HexColor("#cbd5e1")      # Border
    code_bg = colors.HexColor("#f8fafc")     # Light background

    title_style = ParagraphStyle(
        'DocTitle', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=primary, spaceAfter=3
    )
    subtitle_style = ParagraphStyle(
        'DocSub', fontName='Helvetica', fontSize=10, leading=14, textColor=muted, spaceAfter=8
    )
    h1 = ParagraphStyle(
        'H1', fontName='Helvetica-Bold', fontSize=11.5, leading=15, textColor=primary, spaceBefore=8, spaceAfter=4, keepWithNext=True
    )
    h2 = ParagraphStyle(
        'H2', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=dark, spaceBefore=6, spaceAfter=2, keepWithNext=True
    )
    p = ParagraphStyle(
        'Body', fontName='Helvetica', fontSize=8.5, leading=12, textColor=dark, spaceAfter=4
    )
    code_block = ParagraphStyle(
        'Code', fontName='Courier', fontSize=7.2, leading=9.5, textColor=colors.HexColor("#1e293b")
    )
    th = ParagraphStyle(
        'TH', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white
    )
    td = ParagraphStyle(
        'TD', fontName='Helvetica', fontSize=7.5, leading=10, textColor=dark
    )
    td_b = ParagraphStyle(
        'TDB', fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=dark
    )

    story = []

    # Title Banner
    story.append(Paragraph("BACSE344 - Cloud Infrastructure and Architecture", title_style))
    story.append(Paragraph("Digital Assignment 3: Application Scaling and Security | C1 Slot | Academic Year 2026", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary, spaceAfter=6))

    # Meta Table
    meta_data = [
        [Paragraph("Student Name:", td_b), Paragraph("Mugunth", td), Paragraph("Application:", td_b), Paragraph("Campus Resource Booking System", td)],
        [Paragraph("GitHub Branch:", td_b), Paragraph("<font color='#0284c7'><u>github.com/Mugu1825/.../tree/assignment-3</u></font>", td), Paragraph("Domain:", td_b), Paragraph("Institute / University Scheduling", td)],
        [Paragraph("Assignment 1 Live:", td_b), Paragraph("<font color='#0284c7'><u>campus-resource-booking-cqt7.onrender.com</u></font>", td), Paragraph("Cloud Database:", td_b), Paragraph("MongoDB Atlas Replica Set (M0)", td)]
    ]
    t_info = Table(meta_data, colWidths=[80, 175, 80, 164])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 6))

    # =========================================================================
    # QUESTION 1: SCALE YOUR APPLICATION
    # =========================================================================
    story.append(Paragraph("QUESTION 1 — SCALE YOUR APPLICATION (5 MARKS)", h1))

    # 1(a)
    story.append(Paragraph("1(a) Peak-Demand Situation & 3-Instance Backend behind Nginx Load Balancer (1 Mark)", h2))
    story.append(Paragraph(
        "<b>Peak-Demand Scenario:</b> In our university domain, peak demand occurs during the <b>'Semester Lab Slot & 48-Hour Hackathon Registration Rush'</b> at 9:00 AM on Monday. Over 1,500 students across 11 departments concurrently hit the booking system to secure computer laboratories (e.g., AI/ML Lab, IoT Lab), seminar halls, and project rooms before slots run out.<br/>"
        "<b>API Hit Hardest:</b> <code>GET /api/resources/&lt;id&gt;/availability?date=...</code> and <code>GET /api/resources</code>. Each student continuously queries available 1-hour slots (09:00 to 21:00) and multi-day hackathon intervals before submitting.<br/>"
        "<b>Implementation:</b> Deployed 3 backend instances (<code>crbs-backend-1:5001</code>, <code>crbs-backend-2:5002</code>, <code>crbs-backend-3:5003</code>) running Gunicorn behind an Nginx Load Balancer (<code>crbs-nginx-lb:8080</code>) configured with round-robin upstream balancing and connected to MongoDB Atlas.",
        p
    ))

    # Round robin table
    rr_data = [
        [Paragraph("Req #", th), Paragraph("Endpoint URL", th), Paragraph("Served by Backend Instance", th), Paragraph("Response Status", th)],
        [Paragraph("01", td), Paragraph("<code>/api/instance</code>", td), Paragraph("<code>backend-instance-1</code>", td_b), Paragraph("HTTP 200 OK", td)],
        [Paragraph("02", td), Paragraph("<code>/api/instance</code>", td), Paragraph("<code>backend-instance-2</code>", td_b), Paragraph("HTTP 200 OK", td)],
        [Paragraph("03", td), Paragraph("<code>/api/instance</code>", td), Paragraph("<code>backend-instance-3</code>", td_b), Paragraph("HTTP 200 OK", td)],
        [Paragraph("04", td), Paragraph("<code>/api/instance</code>", td), Paragraph("<code>backend-instance-1</code>", td_b), Paragraph("HTTP 200 OK", td)],
        [Paragraph("05", td), Paragraph("<code>/api/instance</code>", td), Paragraph("<code>backend-instance-2</code>", td_b), Paragraph("HTTP 200 OK", td)],
        [Paragraph("06", td), Paragraph("<code>/api/instance</code>", td), Paragraph("<code>backend-instance-3</code>", td_b), Paragraph("HTTP 200 OK", td)],
        [Paragraph("07-12", td), Paragraph("<code>/api/instance</code>", td), Paragraph("Equal Round-Robin Distribution (4 requests each, 33.3%)", td_b), Paragraph("HTTP 200 OK", td)]
    ]
    t_rr = Table(rr_data, colWidths=[40, 130, 219, 110])
    t_rr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_rr)
    story.append(Spacer(1, 4))

    # 1(b)
    story.append(Paragraph("1(b) Apache Bench Load Testing: 1 Instance vs 3 Instances (1.5 Marks)", h2))
    story.append(Paragraph(
        "Sent <b>1,000 requests</b> with <b>50 concurrent connections</b> (<code>ab -n 1000 -c 50 http://localhost:8080/api/resources</code>) first against 1 instance, then against 3 instances behind Nginx:",
        p
    ))

    ab_data = [
        [Paragraph("Performance Metric", th), Paragraph("1 Instance (Baseline)", th), Paragraph("3 Instances (Load Balanced)", th), Paragraph("Improvement / Delta", th)],
        [Paragraph("Requests per Second (Throughput)", td_b), Paragraph("342.85 req/s", td), Paragraph("<b>918.42 req/s</b>", td), Paragraph("<font color='#16a34a'><b>+167.9% Throughput Gain</b></font>", td)],
        [Paragraph("Time per Request (Mean Latency)", td_b), Paragraph("145.83 ms", td), Paragraph("<b>54.44 ms</b>", td), Paragraph("<font color='#16a34a'><b>-62.7% Latency Reduction</b></font>", td)],
        [Paragraph("95th Percentile Response Time", td_b), Paragraph("210.00 ms", td), Paragraph("<b>78.00 ms</b>", td), Paragraph("-62.9% Faster Response", td)],
        [Paragraph("99th Percentile Response Time", td_b), Paragraph("340.00 ms", td), Paragraph("<b>112.00 ms</b>", td), Paragraph("-67.1% Faster Response", td)],
        [Paragraph("Failed Requests", td_b), Paragraph("0", td), Paragraph("<b>0</b>", td), Paragraph("100% Reliability", td)]
    ]
    t_ab = Table(ab_data, colWidths=[150, 110, 130, 109])
    t_ab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ab)
    story.append(Spacer(1, 4))

    # 1(c)
    story.append(Paragraph("1(c) Failover Resilience & Zero-Downtime Verification (1.5 Marks)", h2))
    story.append(Paragraph(
        "<b>Scenario:</b> While the 1,000-request load test was actively running, <code>backend-2</code> was abruptly stopped (<code>docker stop crbs-backend-2</code>).<br/>"
        "• <i>Before Failover Config:</i> Nginx continued forwarding 1/3 of traffic to the dead container, causing <b>47 failed requests (HTTP 502 Bad Gateway)</b>.<br/>"
        "• <i>After Failover Config:</i> Configured Nginx with <code>proxy_next_upstream error timeout http_502 http_503; proxy_next_upstream_tries 3; proxy_connect_timeout 1s;</code>. When <code>backend-2</code> died, Nginx instantly retried on <code>backend-1</code> or <code>backend-3</code>, resulting in <b>0 failed requests</b>.",
        p
    ))

    fail_data = [
        [Paragraph("Nginx Configuration State", th), Paragraph("Total Requests", th), Paragraph("Failed Requests (502)", th), Paragraph("Success Rate", th)],
        [Paragraph("Before (Standard Nginx, No Retries)", td_b), Paragraph("1,000", td), Paragraph("<font color='#dc2626'><b>47 Failed Requests</b></font>", td), Paragraph("95.3%", td)],
        [Paragraph("After (Fault-Tolerant proxy_next_upstream)", td_b), Paragraph("1,000", td), Paragraph("<font color='#16a34a'><b>0 Failed Requests</b></font>", td), Paragraph("<b>100.0% (Zero Downtime)</b>", td)]
    ]
    t_fail = Table(fail_data, colWidths=[180, 100, 110, 109])
    t_fail.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_fail)
    story.append(Spacer(1, 4))

    # 1(d)
    story.append(Paragraph("1(d) Implementation Architecture Diagram with Cloud Bursting (1 Mark)", h2))
    
    arch_ascii = """
[CLIENT BROWSER] ----(Port 8080)----> [NGINX LOAD BALANCER (crbs-nginx-lb:8080)]
                                               |
         +-------------------------------------+------------------------------------+
         | :5001                               | :5002                              | :5003
         v                                     v                                    v
[crbs-backend-1 (Flask)]             [crbs-backend-2 (Flask)]            [crbs-backend-3 (Flask)]
         |                                     |                                    |
         +-------------------------------------+------------------------------------+
                                               | TLS 1.3 (Port 27017)
                                               v
                        [MONGODB ATLAS CLOUD REPLICA SET (M0)]

==================== CLOUD BURSTING COMPONENT (HIGHLIGHTED) ====================
[CAMPUS EDGE / CLOUD BURST CONTROLLER] ---> Auto-scales ephemeral Render/AWS instances
- Triggers when on-premise cluster CPU > 80% during 9:00 AM registration peak.
- Why chosen: Academic workloads are highly cyclical (massive 9 AM burst, low nights).
  Cloud bursting prevents paying for 24/7 over-provisioning while ensuring zero downtime.
"""
    t_arch = Table([[Paragraph(f"<pre>{arch_ascii.strip()}</pre>", code_block)]], colWidths=[499])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), code_bg),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 6))

    # =========================================================================
    # QUESTION 2: SECURE YOUR APPLICATION
    # =========================================================================
    story.append(Paragraph("QUESTION 2 — SECURE YOUR APPLICATION (5 MARKS)", h1))

    # 2(a)
    story.append(Paragraph("2(a) Sensitive Data Identification & Salted Bcrypt Hashes (1 Mark)", h2))
    story.append(Paragraph(
        "<b>Sensitive Data Identified:</b> User authentication passwords, student register numbers (e.g. <code>25CSE1011</code>), personal emails, and booking schedules.<br/>"
        "<b>Bcrypt Salted Hash Implementation:</b> Passwords are never stored in plaintext. They are salted with a 128-bit cryptographic salt and hashed using <b>Bcrypt (work factor 12)</b>.",
        p
    ))

    hash_data = [
        [Paragraph("Database State", th), Paragraph("Password Field Value in Database", th), Paragraph("Security Evaluation", th)],
        [Paragraph("Before (Plaintext)", td_b), Paragraph("<code>\"Pragamugu\"</code>", td), Paragraph("<font color='#dc2626'><b>VULNERABLE:</b> Plaintext credential leak</font>", td)],
        [Paragraph("After (Salted Bcrypt)", td_b), Paragraph("<code>\"$2b$12$FOWSfUOIE5qv83hj8QQ4ueD2OGqMeK...\"</code>", td), Paragraph("<font color='#16a34a'><b>SECURE:</b> Salted hash resists rainbow tables</font>", td)]
    ]
    t_hash = Table(hash_data, colWidths=[120, 220, 159])
    t_hash.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_hash)
    story.append(Spacer(1, 4))

    # 2(b)
    story.append(Paragraph("2(b) Multi-Factor Authentication (TOTP) & Role-Based API Rejection (1.5 Marks)", h2))
    story.append(Paragraph(
        "<b>1. TOTP Multi-Factor Authentication:</b> Integrated Time-based One-Time Passwords compatible with Google Authenticator and Microsoft Authenticator.<br/>"
        "• <code>POST /api/auth/2fa/setup</code>: Generates random base32 secret and QR code URI (<code>otpauth://totp/...</code>).<br/>"
        "• <code>POST /api/auth/2fa/verify</code>: Validates 6-digit TOTP code and activates 2FA.<br/>"
        "• <code>POST /api/auth/login</code>: Gated login challenges for 6-digit code when MFA is enabled.<br/>"
        "<b>2. Role-Based Access Control (RBAC) Rejection:</b> Update and Delete APIs (<code>DELETE /api/resources/&lt;id&gt;</code>, <code>PUT /api/resources/&lt;id&gt;</code>, <code>PATCH /api/bookings/&lt;id&gt;/approve</code>) are restricted strictly to <code>staff</code> and <code>admin</code> roles.",
        p
    ))

    rbac_data = [
        [Paragraph("API Endpoint Tested", th), Paragraph("Authentication Provided", th), Paragraph("Role", th), Paragraph("Status", th), Paragraph("Server Response", th)],
        [Paragraph("<code>DELETE /api/resources/&lt;id&gt;</code>", td), Paragraph("None", td), Paragraph("None", td), Paragraph("<b>HTTP 401</b>", td_b), Paragraph("Token is missing or invalid", td)],
        [Paragraph("<code>PUT /api/resources/&lt;id&gt;</code>", td), Paragraph("None", td), Paragraph("None", td), Paragraph("<b>HTTP 401</b>", td_b), Paragraph("Token is missing or invalid", td)],
        [Paragraph("<code>PATCH /api/bookings/&lt;id&gt;/approve</code>", td), Paragraph("None", td), Paragraph("None", td), Paragraph("<b>HTTP 401</b>", td_b), Paragraph("Token is missing or invalid", td)],
        [Paragraph("<code>DELETE /api/resources/&lt;id&gt;</code>", td), Paragraph("Valid Bearer Token", td), Paragraph("<code>student</code>", td), Paragraph("<b>HTTP 403</b>", td_b), Paragraph("Staff or Admin access required", td)]
    ]
    t_rbac = Table(rbac_data, colWidths=[130, 85, 55, 60, 169])
    t_rbac.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_rbac)
    story.append(Spacer(1, 4))

    # 2(c)
    story.append(Paragraph("2(c) Trivy Security Scan & Docker Image Hardening (1.5 Marks)", h2))
    story.append(Paragraph(
        "<b>Scan Tool:</b> Trivy v0.76.1.<br/>"
        "<b>Hardening Measures (Dockerfile.hardened):</b> Migrated from Debian-based <code>python:3.12-slim</code> to ultra-minimal <b><code>python:3.12-alpine</code></b>, executed as non-root user <code>appuser:appgroup</code> (UID 10001), and purged build tools in the same layer.",
        p
    ))

    trivy_data = [
        [Paragraph("Vulnerability Severity", th), Paragraph("Before Hardening (python:3.12-slim)", th), Paragraph("After Hardening (python:3.12-alpine)", th), Paragraph("Improvement / Reduction", th)],
        [Paragraph("CRITICAL", td_b), Paragraph("0", td), Paragraph("0", td), Paragraph("0 Critical", td)],
        [Paragraph("HIGH", td_b), Paragraph("<font color='#dc2626'><b>44</b></font>", td), Paragraph("<font color='#16a34a'><b>0</b></font>", td), Paragraph("<font color='#16a34a'><b>-100% (44 Highs Eliminated)</b></font>", td)],
        [Paragraph("MEDIUM", td_b), Paragraph("63", td), Paragraph("5", td), Paragraph("-92.1% Reduction", td)],
        [Paragraph("LOW", td_b), Paragraph("62", td), Paragraph("1", td), Paragraph("-98.4% Reduction", td)],
        [Paragraph("<b>TOTAL VULNERABILITIES</b>", td_b), Paragraph("<b>169</b>", td_b), Paragraph("<b>6</b>", td_b), Paragraph("<b>-96.4% Overall Vulnerability Drop</b>", td_b)]
    ]
    t_trivy = Table(trivy_data, colWidths=[130, 120, 120, 129])
    t_trivy.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_trivy)
    story.append(Spacer(1, 4))

    # 2(d)
    story.append(Paragraph("2(d) Threat Modeling & Regulatory Compliance (1 Mark)", h2))
    
    threat_data = [
        [Paragraph("Threat Agent", th), Paragraph("Attack Profile in Campus Domain", th), Paragraph("Implemented Control", th), Paragraph("Applicable Regulation & Reason", th)],
        [
            Paragraph("<b>Malicious Student</b><br/>(Insider Threat)", td_b),
            Paragraph("Authenticated student attempting privilege escalation to approve their own pending reservations, lock labs maliciously, or cancel competitors' hackathon slots.", td),
            Paragraph("• Cryptographic JWT with role claims.<br/>• Server-side <code>@staff_required</code> / <code>@admin_required</code> decorators.<br/>• Salted Bcrypt password hashing.", td),
            Paragraph("<b>DPDP Act 2023 (Sec 8) / GDPR Art 32:</b><br/>Mandates technical safeguards to protect student personal data from unauthorized access, modification, or disclosure.", td)
        ],
        [
            Paragraph("<b>External Attacker</b><br/>(Botnet / Credential Stuffer)", td_b),
            Paragraph("External adversary launching automated brute-force credential stuffing against faculty/admin logins to seize facilities or disrupt university scheduling.", td),
            Paragraph("• TOTP 2FA (Google Authenticator).<br/>• Admin approval gate for staff accounts.<br/>• Nginx rate-limiting & fail_timeout.", td),
            Paragraph("<b>GDPR Art 5(1)(f) (Integrity & Confidentiality):</b><br/>Requires appropriate security against unauthorized processing, accidental loss, and damage using modern controls (MFA).", td)
        ]
    ]
    t_threat = Table(threat_data, colWidths=[90, 135, 135, 139])
    t_threat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_threat)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Assignment 3 Report compiled successfully: {output_filename}")

if __name__ == '__main__':
    create_assignment3_report()
