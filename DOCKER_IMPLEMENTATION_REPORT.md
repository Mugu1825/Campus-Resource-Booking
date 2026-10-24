# Implementation Report: Docker Containerization for Campus Resource Booking System

**Student Name:** Mugunth  
**Department:** Computer Science & Engineering  
**Application:** Campus Resource Booking System (CRBS)  
**Live Production URL:** [https://campus-resource-booking-cqt7.onrender.com](https://campus-resource-booking-cqt7.onrender.com)  
**GitHub Repository:** [https://github.com/Mugu1825/Campus-Resource-Booking](https://github.com/Mugu1825/Campus-Resource-Booking)  

---

## 1. Introduction & Objectives

### 1.1 Why Containerization?
In modern software development, running applications across diverse environments (development laptops, testing servers, and cloud production) often leads to the classic *"it works on my machine"* dilemma. Differences in Python versions, operating system packages, and web server configurations cause unexpected failures.

To address this, I implemented **Docker containerization** for the Campus Resource Booking System. Docker packages the complete runtime environment—including the operating system libraries, Python interpreter, Nginx web server, Gunicorn WSGI gateway, and application dependencies—into an immutable, portable container image.

### 1.2 Key Objectives
1. **Single-Container Architecture:** Package both the static frontend and the Python Flask backend into one unified Docker container.
2. **Reverse Proxy Integration:** Use Nginx inside the container to serve static assets directly and reverse-proxy all `/api/*` requests to Gunicorn on localhost, completely eliminating Cross-Origin Resource Sharing (CORS) issues.
3. **Dynamic Cloud Port Binding:** Ensure the container dynamically adapts to Render's dynamic `$PORT` environment variable while remaining runnable locally on standard port 80/3000.
4. **Reproducible Local Orchestration:** Provide a `docker-compose.yml` specification for one-command local startup (`docker compose up --build`).

---

## 2. Docker Architecture Design

The containerized application implements a multi-tier single-container architecture:

```
[User Browser / Client]
          │
          ▼ (Port 80 locally / $PORT on Render)
+───────────────────────────────────────────────────────────────+
|                       DOCKER CONTAINER                        |
|                                                               |
|  +─────────────────────────────────────────────────────────+  |
|  |                 NGINX REVERSE PROXY                     |  |
|  +─────────────────────────────────────────────────────────+  |
|         │                                          │          |
|         │ (/*, /css/*, /js/*)                      │ (/api/*) |
|         ▼                                          ▼          |
|  +──────────────────────+       +──────────────────────────+  |
|  |  Frontend Directory  |       | Gunicorn WSGI (Port 5000)|  |
|  |  (/usr/share/nginx/  |       | Flask Backend App Engine |  |
|  |   html)              |       +──────────────────────────+  |
|  +──────────────────────+                    │                |
+──────────────────────────────────────────────┼────────────────+
                                               ▼ TLS 1.3
                                  +──────────────────────────+
                                  |   MongoDB Atlas Cloud    |
                                  +──────────────────────────+
```

### Architectural Benefits:
- **Zero CORS Issues:** The frontend and backend share the exact same host and port. API requests use relative paths (`/api/auth/login`, `/api/bookings`), eliminating CORS pre-flight latency.
- **Enhanced Performance:** Nginx handles static file delivery with gzip compression and caching headers, taking the load off Python.
- **Portability:** The exact same Docker image runs on local developer machines and in cloud production (Render) without code changes.

---

## 3. Breakdown of Docker Configuration Files

### 3.1 `Dockerfile`
The Dockerfile defines the build steps starting from a lightweight Debian-based Python image:

```dockerfile
FROM python:3.12-slim

# 1. Install system utilities (Nginx web server and curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Cache & install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 3. Copy application source code
COPY backend /app/backend
COPY frontend /usr/share/nginx/html

# 4. Configure Nginx reverse proxy
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default 2>/dev/null || true
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 5. Set up startup entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV PORT=80
EXPOSE 80 10000

ENTRYPOINT ["/app/entrypoint.sh"]
```

### 3.2 `nginx.conf`
Configures Nginx to serve the UI and proxy API traffic:
- `location /`: Serves static HTML pages with fallback to `index.html`.
- `location /css/`, `location /js/`: Adds 1-day browser caching headers.
- `location /api/`: Forwards incoming requests to `http://127.0.0.1:5000/api/` along with `Host`, `X-Real-IP`, and `X-Forwarded-For` headers.

### 3.3 `entrypoint.sh`
The container initialization script:
1. Dynamically replaces `LISTEN_PORT` in `nginx.conf` with Render's `$PORT` (defaulting to 80 locally).
2. Spawns Gunicorn with 2 worker processes on `127.0.0.1:5000` in the background.
3. Loops health checks (`curl http://127.0.0.1:5000/api/health`) until Flask confirms `ok`.
4. Starts Nginx in the foreground (`nginx -g 'daemon off;'`) so Docker can monitor the process lifecycle.

### 3.4 `docker-compose.yml`
Simplifies local developer setup:
```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: campus-resource-booking
    ports:
      - "3000:80"
    environment:
      - MONGO_URI=${MONGO_URI}
      - JWT_SECRET=${JWT_SECRET}
    env_file:
      - ./backend/.env
    restart: unless-stopped
```

### 3.5 `.dockerignore`
Prevents unnecessary files from bloating the Docker image:
- Ignores `backend/venv/`, `__pycache__/`, `.git/`, `.env`, and test artifacts.

---

## 4. Step-by-Step Execution & Commands

### Step 1: Building the Docker Image
```bash
docker build -t campus-booking .
```
*Docker pulls `python:3.12-slim`, installs Nginx and Python packages, copies code, and tags the image.*

### Step 2: Running the Container Locally
```bash
docker run -d \
  --name campus-booking-app \
  -p 3000:80 \
  --env-file backend/.env \
  campus-booking
```
*Maps host port `3000` to container port `80`, passing MongoDB credentials securely.*

### Step 3: Verifying Container Status & Logs
```bash
# Verify container is running
docker ps

# Check startup logs (Gunicorn + Nginx health check)
docker logs campus-booking-app
```

### Step 4: Testing Application in Browser
Open `http://localhost:3000` in any web browser. Both the frontend UI and the `/api/` endpoints respond smoothly through the Nginx reverse proxy.

---

## 5. Cloud Deployment on Render (with Docker)

1. **Repository Link:** Pushed the repository containing `Dockerfile` to GitHub.
2. **Web Service Setup:** Created a new Web Service on Render with **Runtime: Docker**.
3. **Environment Variables:** Configured `MONGO_URI` (MongoDB Atlas connection string) and `JWT_SECRET`.
4. **Automated Cloud Build:** Render's CI/CD pipeline pulled the code, built the Docker container, and deployed it to:  
   👉 **`https://campus-resource-booking-cqt7.onrender.com`**

---

## 6. Conclusion

Implementing Docker containerization for the Campus Resource Booking System transformed a multi-part application (frontend + WSGI + database connection) into a self-contained, cloud-ready artifact. It achieved:
- **Portability:** Can be run on any machine with Docker installed via a single command.
- **Zero Configuration Conflicts:** Dependencies and web servers are isolated within the container.
- **Seamless Production Deployment:** One-click deployment to Render without CORS configuration.
