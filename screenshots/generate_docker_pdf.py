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
            self.drawString(50, 802, "Docker Implementation Report — Campus Resource Booking System")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(50, 794, 545, 794)
        
        self.drawString(50, 32, "Submitted by Mugunth | CSE Department")
        self.drawRightString(545, 32, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(50, 44, 545, 44)
        self.restoreState()

def create_docker_report(output_filename="DOCKER_IMPLEMENTATION_REPORT.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=50,
        rightMargin=50,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()
    
    primary = colors.HexColor("#0284c7")    # Docker cyan/blue
    primary_dark = colors.HexColor("#0369a1")
    dark = colors.HexColor("#1e293b")
    muted = colors.HexColor("#475569")
    border = colors.HexColor("#cbd5e1")
    code_bg = colors.HexColor("#f8fafc")

    title_style = ParagraphStyle(
        'Title', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=primary_dark, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'Subtitle', fontName='Helvetica', fontSize=10, leading=14, textColor=muted, spaceAfter=8
    )
    h1 = ParagraphStyle(
        'H1', fontName='Helvetica-Bold', fontSize=11.5, leading=15, textColor=primary_dark, spaceBefore=8, spaceAfter=3, keepWithNext=True
    )
    h2 = ParagraphStyle(
        'H2', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=dark, spaceBefore=5, spaceAfter=2, keepWithNext=True
    )
    p = ParagraphStyle(
        'Body', fontName='Helvetica', fontSize=8.5, leading=12, textColor=dark, spaceAfter=4
    )
    code_text = ParagraphStyle(
        'CodeText', fontName='Courier', fontSize=7.2, leading=9.5, textColor=colors.HexColor("#0f172a")
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
    story.append(Paragraph("Docker Implementation Report", title_style))
    story.append(Paragraph("Application of Choice: Campus Resource Booking System (CRBS)", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary, spaceAfter=6))

    # Meta Table
    meta_data = [
        [Paragraph("Student Name:", td_b), Paragraph("Mugunth", td), Paragraph("Live App URL:", td_b), Paragraph("<font color='#0284c7'><u>campus-resource-booking-cqt7.onrender.com</u></font>", td)],
        [Paragraph("Department:", td_b), Paragraph("Computer Science & Engineering", td), Paragraph("GitHub Repo:", td_b), Paragraph("<font color='#0284c7'><u>github.com/Mugu1825/Campus-Resource-Booking</u></font>", td)],
        [Paragraph("Container Tech:", td_b), Paragraph("Docker, Nginx, Gunicorn, Python 3.12-slim", td), Paragraph("Cloud Runtime:", td_b), Paragraph("Render Web Service (Docker Environment)", td)]
    ]
    t_info = Table(meta_data, colWidths=[80, 165, 80, 170])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0f9ff")),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 6))

    # 1. Introduction & Objectives
    story.append(Paragraph("1. Introduction & Why Docker?", h1))
    story.append(Paragraph(
        "Deploying full-stack applications with separate frontend static assets, Python WSGI backends, and cloud databases typically requires configuring multiple independent servers or struggling with Cross-Origin Resource Sharing (CORS). Furthermore, differences in local machine packages frequently cause unexpected deployment bugs.",
        p
    ))
    story.append(Paragraph(
        "By implementing **Docker containerization** for the Campus Resource Booking System, the complete runtime environment—operating system libraries (Debian), Python interpreter, dependencies, Gunicorn WSGI gateway, and Nginx web server—is compiled into an immutable image. The app runs identically on any developer machine and in the cloud with zero configuration friction.",
        p
    ))

    # 2. Architecture
    story.append(Paragraph("2. Container Architecture: Single-Container Model", h1))
    story.append(Paragraph(
        "I designed a **single-container architecture** combining Nginx and Gunicorn. Nginx listens on port 80 (or Render's dynamic <code>$PORT</code>), directly serves all static frontend assets (HTML/CSS/JS) with caching, and transparently reverse-proxies all <code>/api/*</code> requests to Gunicorn on <code>127.0.0.1:5000</code>. This architecture guarantees:",
        p
    ))
    story.append(Paragraph(
        "• <b>Zero CORS Issues:</b> Frontend and backend are accessed on the exact same origin and port.<br/>"
        "• <b>Cost Efficiency:</b> Packaged into a single web service instead of paying for or managing separate instances.<br/>"
        "• <b>Dynamic Cloud Port Binding:</b> At startup, an entrypoint script reads Render's injected <code>$PORT</code> variable and configures Nginx dynamically.",
        p
    ))

    # Architecture Box Diagram
    arch_box = """
[Browser Request (Port 80 / $PORT)] --> [Nginx Reverse Proxy in Docker Container]
    |--> Static Assets (/*, /css/*, /js/*) --> Served from /usr/share/nginx/html
    |--> API Traffic (/api/*) -------------> Proxied to Gunicorn on 127.0.0.1:5000
                                                |
                                                v [TLS 1.3 Encryption]
                                         [MongoDB Atlas Cloud Database]
"""
    t_box = Table([[Paragraph(f"<pre>{arch_box.strip()}</pre>", code_text)]], colWidths=[495])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), code_bg),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_box)
    story.append(Spacer(1, 4))

    # 3. Docker Configuration Breakdown
    story.append(Paragraph("3. Breakdown of Docker Configuration Files", h1))

    docker_files_data = [
        [Paragraph("File", th), Paragraph("Key Directives & Configuration", th), Paragraph("Purpose in Container Lifecycle", th)],
        [
            Paragraph("<b>Dockerfile</b>", td_b),
            Paragraph("<code>FROM python:3.12-slim<br/>RUN apt-get update && apt-get install -y nginx curl<br/>COPY backend/requirements.txt ...<br/>RUN pip install --no-cache-dir -r ...<br/>COPY frontend /usr/share/nginx/html<br/>ENTRYPOINT [\"/app/entrypoint.sh\"]</code>", td),
            Paragraph("Multi-tier image definition. Installs Nginx and Python runtime, installs PyMongo/Flask/Bcrypt, copies frontend assets to Nginx standard directory, and defines entrypoint.", td)
        ],
        [
            Paragraph("<b>nginx.conf</b>", td_b),
            Paragraph("<code>location / { try_files $uri $uri/ /index.html; }<br/>location /api/ { proxy_pass http://127.0.0.1:5000/api/; ... }<br/>location /css/, /js/ { expires 1d; }</code>", td),
            Paragraph("Web server configuration. Handles static file delivery, gzip compression, client-side routing, and reverse-proxying API calls to Gunicorn with proxy headers.", td)
        ],
        [
            Paragraph("<b>entrypoint.sh</b>", td_b),
            Paragraph("<code>sed -i \"s/LISTEN_PORT/${PORT}/g\" default.conf<br/>gunicorn --bind 127.0.0.1:5000 app:app &<br/>curl http://127.0.0.1:5000/api/health<br/>exec nginx -g 'daemon off;'</code>", td),
            Paragraph("Container orchestrator script. Binds Nginx to Render's dynamic <code>$PORT</code>, spawns Gunicorn in the background, waits for health check, and runs Nginx in the foreground.", td)
        ],
        [
            Paragraph("<b>docker-compose.yml</b>", td_b),
            Paragraph("<code>version: '3.8'<br/>services:<br/>&nbsp;&nbsp;app:<br/>&nbsp;&nbsp;&nbsp;&nbsp;build: .<br/>&nbsp;&nbsp;&nbsp;&nbsp;ports: [\"3000:80\"]<br/>&nbsp;&nbsp;&nbsp;&nbsp;env_file: [./backend/.env]</code>", td),
            Paragraph("One-command local development setup. Maps host port 3000 to container port 80 and passes Atlas credentials securely from local environment files.", td)
        ]
    ]
    t_df = Table(docker_files_data, colWidths=[75, 230, 190])
    t_df.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_dark),
        ('BOX', (0,0), (-1,-1), 1, border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_df)
    story.append(Spacer(1, 4))

    # 4. Commands & Step-by-Step Execution
    story.append(Paragraph("4. Step-by-Step Execution & Commands", h1))
    story.append(Paragraph(
        "<b>Step 1 — Build the Docker Image:</b><br/>"
        "<code>docker build -t campus-booking .</code><br/>"
        "<i>Docker compiles the base image, packages Nginx, installs Python wheels, and copies application code.</i><br/>"
        "<b>Step 2 — Run the Container Locally:</b><br/>"
        "<code>docker run -d --name campus-booking-app -p 3000:80 --env-file backend/.env campus-booking</code><br/>"
        "<i>Or alternatively using Docker Compose:</i> <code>docker compose up -d</code><br/>"
        "<b>Step 3 — Verify Running Status & Logs:</b><br/>"
        "<code>docker ps</code> &nbsp;<i>(shows container active on port 3000)</i><br/>"
        "<code>docker logs campus-booking-app</code> &nbsp;<i>(shows Gunicorn healthy and Nginx ready)</i><br/>"
        "<b>Step 4 — Test in Browser:</b><br/>"
        "Open <code>http://localhost:3000</code> in your browser to interact with the containerized application.",
        p
    ))

    # 5. Cloud Deployment on Render
    story.append(Paragraph("5. Cloud Deployment via Docker on Render", h1))
    story.append(Paragraph(
        "For cloud production, the repository was linked to <b>Render Cloud</b> as a <b>Docker Web Service</b>. Render's automated CI/CD pipeline detected the <code>Dockerfile</code>, compiled the container in the cloud, supplied the <code>MONGO_URI</code> and <code>JWT_SECRET</code> environment variables, and deployed the live service at: <b><font color='#0284c7'>https://campus-resource-booking-cqt7.onrender.com</font></b>.",
        p
    ))

    # 6. Conclusion
    story.append(Paragraph("6. Conclusion & Benefits Realized", h1))
    story.append(Paragraph(
        "Containerizing the Campus Resource Booking System with Docker achieved a fully reproducible, cloud-ready deployment. It eliminated cross-origin resource sharing complexities through an internal Nginx reverse proxy, simplified multi-tier process management with an automated entrypoint script, and allowed one-click deployment to cloud platforms.",
        p
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Docker report compiled successfully: {output_filename}")

if __name__ == '__main__':
    create_docker_report()
