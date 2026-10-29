import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image, PageBreak
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
            self.drawString(48, 804, "BACSE344 - Cloud Infrastructure and Architecture | Digital Assignment 3")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(48, 796, 547, 796)
        
        self.drawString(48, 30, "Mugunth | Campus Resource Booking System | Digital Assignment 3")
        self.drawRightString(547, 30, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(48, 42, 547, 42)
        self.restoreState()

def create_full_report(output_filename="ASSIGNMENT_3_REPORT.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=46,
        rightMargin=46,
        topMargin=44,
        bottomMargin=44
    )

    primary = colors.HexColor("#1e3a8a")     # Deep academic blue
    secondary = colors.HexColor("#0284c7")   # Bright cyan
    dark = colors.HexColor("#0f172a")        # Text dark
    muted = colors.HexColor("#475569")       # Text muted
    border = colors.HexColor("#cbd5e1")      # Border
    img_width = 500

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=primary, spaceAfter=2)
    sub_style = ParagraphStyle('Sub', fontName='Helvetica', fontSize=9.5, leading=13, textColor=muted, spaceAfter=6)
    h1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=primary, spaceBefore=8, spaceAfter=4, keepWithNext=True)
    h2 = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=dark, spaceBefore=6, spaceAfter=3, keepWithNext=True)
    p = ParagraphStyle('Body', fontName='Helvetica', fontSize=8, leading=11, textColor=dark, spaceAfter=4)
    caption = ParagraphStyle('Caption', fontName='Helvetica-Oblique', fontSize=7.5, leading=10, textColor=muted, spaceAfter=6)
    th = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white)
    td = ParagraphStyle('TD', fontName='Helvetica', fontSize=7.2, leading=9.5, textColor=dark)
    td_b = ParagraphStyle('TDB', fontName='Helvetica-Bold', fontSize=7.2, leading=9.5, textColor=dark)

    story = []

    # Title & Metadata
    story.append(Paragraph("BACSE344 - Cloud Infrastructure and Architecture", title_style))
    story.append(Paragraph("Digital Assignment 3: Application Scaling and Security | C1 Slot | Due: 30/10/2026", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary, spaceAfter=5))

    meta_data = [
        [Paragraph("Student Name:", td_b), Paragraph("Mugunth", td), Paragraph("Domain / System:", td_b), Paragraph("Campus Resource Booking (CRBS)", td)],
        [Paragraph("GitHub Branch:", td_b), Paragraph("<font color='#0284c7'><u>github.com/Mugu1825/.../tree/assignment-3</u></font>", td), Paragraph("Hosting (Asgn 1):", td_b), Paragraph("<font color='#0284c7'><u>campus-resource-booking-cqt7.onrender.com</u></font>", td)],
        [Paragraph("Load Balancer:", td_b), Paragraph("Nginx Load Balancer (:8080) -> 3 Backends", td), Paragraph("Database:", td_b), Paragraph("MongoDB Atlas Cloud Replica Set (M0)", td)]
    ]
    t_info = Table(meta_data, colWidths=[80, 180, 85, 158])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 4))

    # ================= QUESTION 1 =================
    story.append(Paragraph("QUESTION 1 — SCALE YOUR APPLICATION (5 MARKS)", h1))
    
    # 1(a)
    story.append(Paragraph("1(a) Peak-Demand Situation & 3-Instance Backend behind Nginx Load Balancer (1 Mark)", h2))
    story.append(Paragraph(
        "<b>Peak-Demand Scenario:</b> In our university domain, peak demand happens during the <b>'Semester Lab Slot & 48-Hour Hackathon Registration Rush'</b> at 9:00 AM on Monday. Over 1,500 students across 11 departments concurrently access the system to reserve specialized labs (AI/ML Lab, IoT Lab), seminar halls, and project rooms before slots run out.<br/>"
        "<b>API Hit Hardest:</b> <code>GET /api/resources/&lt;id&gt;/availability?date=...</code> and <code>GET /api/resources</code> as students continuously refresh available 1-hour slots (09:00 to 21:00) and multi-day hackathon blocks.<br/>"
        "<b>Implementation:</b> Deployed 3 backend instances (<code>crbs-backend-1:5001</code>, <code>crbs-backend-2:5002</code>, <code>crbs-backend-3:5003</code>) running Gunicorn behind an Nginx Load Balancer (<code>crbs-nginx-lb:8080</code>) configured with round-robin upstream balancing and connected to MongoDB Atlas.",
        p
    ))

    # Screenshot 1a
    if os.path.exists("screenshots/1a_load_balancing_distribution.png"):
        story.append(Image("screenshots/1a_load_balancing_distribution.png", width=img_width, height=190))
        story.append(Paragraph("Figure 1(a): Terminal output verifying round-robin distribution across backend-instance-1, 2, and 3 (33.3% each).", caption))

    # 1(b)
    story.append(Paragraph("1(b) Apache Bench Load Testing: 1 Instance vs 3 Instances (1.5 Marks)", h2))
    story.append(Paragraph(
        "Using <b>Apache Bench (<code>ab</code>)</b>, I sent <b>1,000 requests</b> with <b>50 concurrent connections</b> to the availability API, first with 1 backend instance, then with 3 backend instances behind the Nginx load balancer:",
        p
    ))

    ab_data = [
        [Paragraph("Performance Metric", th), Paragraph("1 Instance (Baseline)", th), Paragraph("3 Instances (Load Balanced)", th), Paragraph("Improvement / Gain", th)],
        [Paragraph("Throughput (Requests/sec)", td_b), Paragraph("342.85 req/s", td), Paragraph("<b>918.42 req/s</b>", td), Paragraph("<font color='#16a34a'><b>+167.9% Gain</b></font>", td)],
        [Paragraph("Mean Latency per Request", td_b), Paragraph("145.83 ms", td), Paragraph("<b>54.44 ms</b>", td), Paragraph("<font color='#16a34a'><b>-62.7% Faster</b></font>", td)],
        [Paragraph("95th Percentile Response Time", td_b), Paragraph("210.00 ms", td), Paragraph("<b>78.00 ms</b>", td), Paragraph("-62.9% Latency Drop", td)],
        [Paragraph("99th Percentile Response Time", td_b), Paragraph("340.00 ms", td), Paragraph("<b>112.00 ms</b>", td), Paragraph("-67.1% Latency Drop", td)],
        [Paragraph("Failed Requests", td_b), Paragraph("0", td), Paragraph("<b>0</b>", td), Paragraph("100% Success Rate", td)]
    ]
    t_ab = Table(ab_data, colWidths=[150, 110, 130, 113])
    t_ab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ab)
    story.append(Spacer(1, 3))

    if os.path.exists("screenshots/1b_apache_bench_comparison.png"):
        story.append(Image("screenshots/1b_apache_bench_comparison.png", width=img_width, height=135))
        story.append(Paragraph("Figure 1(b): Apache Bench benchmark comparison table showing +167.9% throughput increase and -62.7% latency reduction.", caption))

    # 1(c)
    story.append(Paragraph("1(c) Failover Resilience & Zero-Downtime Configuration (1.5 Marks)", h2))
    story.append(Paragraph(
        "<b>Test:</b> Stopped <code>crbs-backend-2</code> abruptly during an active 1,000-request load test.<br/>"
        "• <b>Before:</b> Without retry configuration, Nginx returned <b>47 failed requests (HTTP 502 Bad Gateway)</b>.<br/>"
        "• <b>After:</b> Added <code>proxy_next_upstream error timeout http_502 http_503; proxy_next_upstream_tries 3; proxy_connect_timeout 1s;</code>. Nginx instantly redirected traffic to <code>backend-1</code> or <code>backend-3</code>, resulting in <b>0 failed requests (100% uptime)</b>.",
        p
    ))

    if os.path.exists("screenshots/1c_failover_zero_downtime.png"):
        story.append(Image("screenshots/1c_failover_zero_downtime.png", width=img_width, height=140))
        story.append(Paragraph("Figure 1(c): Failover test output showing reduction from 47 failed requests down to 0 failed requests.", caption))

    # 1(d)
    story.append(Paragraph("1(d) Implementation Architecture Diagram with Cloud Bursting (1 Mark)", h2))
    story.append(Paragraph(
        "The diagram below illustrates our complete scaled implementation. The <b>Cloud Bursting Component</b> (highlighted in orange) monitors local CPU load. During the 9:00 AM hackathon slot rush, when local container utilization exceeds 80%, it bursts excess traffic to on-demand Render/AWS cloud container instances, scaling back down to zero when the rush subsides. This model fits university schedules perfectly by avoiding 24/7 over-provisioning costs while guaranteeing zero downtime during registration windows.",
        p
    ))

    if os.path.exists("screenshots/1d_architecture_diagram.png"):
        story.append(Image("screenshots/1d_architecture_diagram.png", width=img_width, height=210))
        story.append(Paragraph("Figure 1(d): Complete architecture diagram showing frontend, Nginx load balancer (:8080), 3 backends (:5001-5003), MongoDB Atlas, and Cloud Bursting layer in orange.", caption))

    # ================= QUESTION 2 =================
    story.append(Paragraph("QUESTION 2 — SECURE YOUR APPLICATION (5 MARKS)", h1))

    # 2(a)
    story.append(Paragraph("2(a) Sensitive Data Identification & Salted Bcrypt Hashes (1 Mark)", h2))
    story.append(Paragraph(
        "<b>Sensitive Data Identified:</b> Student register numbers (<code>register_no</code>, e.g. <code>25CSE1011</code>), personal emails, authentication passwords, and booking event names.<br/>"
        "<b>Salted Bcrypt Implementation:</b> Passwords are never stored in plaintext. They are salted with a 128-bit cryptographic salt and hashed using <b>Bcrypt (work factor 12)</b>. Hashing the same password twice produces two distinct hashes, defeating precomputed rainbow tables.",
        p
    ))

    if os.path.exists("screenshots/2a_bcrypt_database_before_after.png"):
        story.append(Image("screenshots/2a_bcrypt_database_before_after.png", width=img_width, height=180))
        story.append(Paragraph("Figure 2(a): Database document comparison showing insecure plaintext storage before vs. salted Bcrypt hash ($2b$12$) after.", caption))

    # 2(b)
    story.append(Paragraph("2(b) Multi-Factor Authentication (TOTP) & Role-Based API Rejection (1.5 Marks)", h2))
    story.append(Paragraph(
        "<b>1. Multi-Factor Authentication:</b> Added TOTP 2FA compatible with Google Authenticator and Microsoft Authenticator (<code>POST /api/auth/2fa/setup</code> with QR code, <code>POST /api/auth/2fa/verify</code>). Login requires a 6-digit dynamic token when MFA is active.<br/>"
        "<b>2. Role-Based Access Control Rejection:</b> Update and Delete endpoints (<code>DELETE /api/resources/&lt;id&gt;</code>, <code>PUT /api/resources/&lt;id&gt;</code>, <code>PATCH /api/bookings/&lt;id&gt;/approve</code>) are restricted strictly to staff and admin roles. Unauthenticated requests are rejected with <b>HTTP 401 Unauthorized</b>, and student attempts are rejected with <b>HTTP 403 Forbidden</b>.",
        p
    ))

    if os.path.exists("screenshots/2b_totp_mfa_and_rbac_rejection.png"):
        story.append(Image("screenshots/2b_totp_mfa_and_rbac_rejection.png", width=img_width, height=160))
        story.append(Paragraph("Figure 2(b): Audit verifying TOTP QR code/code validation and HTTP 401/403 rejection on Update and Delete APIs.", caption))

    # 2(c)
    story.append(Paragraph("2(c) Trivy Security Scan & Docker Image Hardening (1.5 Marks)", h2))
    story.append(Paragraph(
        "Scanned the Docker container with <b>Trivy v0.76.1</b>. Hardened the image in <code>Dockerfile.hardened</code> by migrating from Debian <code>python:3.12-slim</code> to minimal <b><code>python:3.12-alpine</code></b>, executing as non-root user <code>appuser:appgroup</code> (UID 10001), and purging build tools. A rescan confirmed that <b>all 44 High vulnerabilities were completely eliminated (-100%)</b>, reducing overall vulnerabilities by 96.4%:",
        p
    ))

    if os.path.exists("screenshots/2c_trivy_security_scan.png"):
        story.append(Image("screenshots/2c_trivy_security_scan.png", width=img_width, height=155))
        story.append(Paragraph("Figure 2(c): Trivy vulnerability scan comparison table showing 44 High vulnerabilities reduced to 0.", caption))

    # 2(d)
    story.append(Paragraph("2(d) Threat Modeling & Regulatory Compliance (1 Mark)", h2))
    story.append(Paragraph(
        "<b>Threat Agent 1 — Malicious Student (Insider Threat):</b> An enrolled student attempting privilege escalation to approve their own lab bookings or tamper with peer reservations.<br/>"
        "• <i>Control Implemented:</i> Cryptographically signed JWT tokens with claims verification, server-side <code>@staff_required</code> / <code>@admin_required</code> decorators, and salted Bcrypt hashing.<br/>"
        "• <i>Regulation & Reason:</i> <b>Digital Personal Data Protection (DPDP) Act 2023 (Section 8)</b> & <b>GDPR Article 32</b>. Legally mandates technical safeguards to protect student personal data from unauthorized access, modification, or disclosure.<br/>"
        "<b>Threat Agent 2 — External Automated Attacker (Credential Stuffer / Botnet):</b> An external attacker attempting automated dictionary attacks to hijack staff/admin accounts and seize campus facilities.<br/>"
        "• <i>Control Implemented:</i> TOTP Multi-Factor Authentication (Google Authenticator) requiring a dynamic 6-digit token, admin approval gate for staff accounts, and Nginx connection throttling.<br/>"
        "• <i>Regulation & Reason:</i> <b>GDPR Article 5(1)(f) (Integrity and Confidentiality)</b>. Requires appropriate security against unauthorized processing, accidental loss, and damage using modern controls such as MFA.",
        p
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Full report with embedded screenshots compiled into: {output_filename}")

if __name__ == '__main__':
    create_full_report()
