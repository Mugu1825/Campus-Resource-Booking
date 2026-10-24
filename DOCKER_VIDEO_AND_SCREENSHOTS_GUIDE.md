# Docker Implementation: Screenshots & 2-Minute Video Guide

This guide gives you the exact commands, screenshot checklist, and second-by-second video script to complete your submission.

---

## Part 1: Required Screenshots Checklist

You need 4–5 clean screenshots for your report/submission:

### Screenshot 1: Docker Configuration Files (in VS Code)
- **What to show:** Open `Dockerfile`, `nginx.conf`, and `docker-compose.yml` side-by-side or open in VS Code tabs.
- **Shows:** The multi-tier architecture combining Python 3.12, Nginx, and Gunicorn.

### Screenshot 2: Building the Docker Image (`docker build`)
- **Command to run in terminal:**
  ```bash
  sudo docker build -t campus-booking .
  ```
- **What to show:** Terminal showing the build steps (Step 1/11: FROM python:3.12-slim, installing Nginx, pip install, successfully tagged `campus-booking`).

### Screenshot 3: Running the Container (`docker run` / `docker compose`)
- **Command to run in terminal:**
  ```bash
  sudo docker run -d --name campus-booking-app -p 3000:80 --env-file backend/.env campus-booking
  ```
  *(Or: `sudo docker compose up -d`)*
- **What to show:** The container starting with its container ID output.

### Screenshot 4: Container Verification (`docker ps` & `docker logs`)
- **Commands to run in terminal:**
  ```bash
  sudo docker ps
  sudo docker logs campus-booking-app
  ```
- **What to show:** 
  - `docker ps` showing `campus-booking-app` with status `Up` and port mapping `0.0.0.0:3000->80/tcp`.
  - `docker logs` showing Gunicorn running on 127.0.0.1:5000 and Nginx ready.

### Screenshot 5: Live App Running from Docker
- **What to show:** Browser open at `http://localhost:3000` (or `https://campus-resource-booking-cqt7.onrender.com`) showing the logged-in Student or Admin Dashboard with campus resources.

---

## Part 2: 2-Minute Video Script (Step-by-Step)

> **Time limit:** Under 2 minutes (Target: ~1 min 45 secs)  
> **Tool:** Use OBS Studio (already installed on your machine) or screen recorder.

### Scene 1: Introduction & Architecture (0:00 – 0:25)
* **Screen:** VS Code showing `Dockerfile` and `nginx.conf`.
* **Voiceover / What to say:**
  > *"Hello! For my Docker implementation project, I containerized the Campus Resource Booking System. Here is our Dockerfile. We use a single-container architecture where Nginx acts as a reverse proxy on port 80, serving our static frontend and proxying all `/api/` calls to Gunicorn running our Flask backend. This eliminates CORS issues and packages the entire full-stack app into a single deployable image."*

### Scene 2: Building the Docker Image (0:25 – 0:50)
* **Screen:** Terminal inside the project folder.
* **Action:** Run:
  ```bash
  sudo docker build -t campus-booking .
  ```
* **Voiceover / What to say:**
  > *"Now, we build our Docker image using `docker build -t campus-booking .`. Docker pulls the lightweight Python 3.12-slim base, installs Nginx, installs our Python requirements like PyMongo, Flask, and Bcrypt, and packages our frontend and backend together."*

### Scene 3: Running the Container & Inspecting Processes (0:50 – 1:15)
* **Screen:** Terminal.
* **Action:** Run:
  ```bash
  sudo docker run -d --name campus-booking-app -p 3000:80 --env-file backend/.env campus-booking
  sudo docker ps
  sudo docker logs campus-booking-app
  ```
* **Voiceover / What to say:**
  > *"Next, we run the container mapping host port 3000 to container port 80. Running `docker ps`, we can see our container `campus-booking-app` is healthy and active. Checking the logs, Gunicorn started on loopback, the internal health check passed, and Nginx is actively listening."*

### Scene 4: Interacting with the App in Browser (1:15 – 1:45)
* **Screen:** Web browser opening `http://localhost:3000`.
* **Action:**
  1. Open `http://localhost:3000`.
  2. Log in with admin credentials (`mugunth@gmail.com` / `Pragamugu`).
  3. Show the Admin Dashboard with live stats loaded through the Nginx $\rightarrow$ Gunicorn Docker proxy.
* **Voiceover / What to say:**
  > *"Now we open `http://localhost:3000` in our browser. The page is served directly through Nginx in the container. We log in as Admin, and our overview metrics load immediately from MongoDB Atlas through the Docker reverse proxy. Everything—authentication, static assets, and API routing—works seamlessly inside the container."*

### Scene 5: Cloud Deployment & Wrap-Up (1:45 – 2:00)
* **Screen:** Switch browser tab to the live cloud URL (`https://campus-resource-booking-cqt7.onrender.com`).
* **Voiceover / What to say:**
  > *"Finally, this exact Dockerfile is deployed on Render as a live Docker Web Service at `campus-resource-booking-cqt7.onrender.com`. In conclusion, Docker gave us a portable, production-ready container that runs identically on local machines and in the cloud. Thank you!"*

---

## Quick Clean-Up Commands (if needed)
```bash
# Stop and remove test container
sudo docker stop campus-booking-app
sudo docker rm campus-booking-app
```
