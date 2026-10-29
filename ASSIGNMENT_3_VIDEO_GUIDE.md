# BACSE344 Digital Assignment 3: 3-Minute Video Demo Script

> **Total Duration:** Exactly 3 Minutes (180 Seconds)  
> **Tool:** OBS Studio (already installed on your machine) or any screen recorder  
> **Branch to show:** `assignment-3` branch on GitHub

---

## 🎬 Scene Breakdown & Exact Voiceover Script

### ⏱️ [0:00 – 0:45] SCENE 1: Question 1(a) & 1(b) — Scaling & Load Testing
* **On Screen:** Show `docker-compose.scale.yml` in VS Code and terminal running `python run_scale_benchmark.py`.
* **What to say:**
  > *"Hello! For Digital Assignment 3 of Cloud Infrastructure and Architecture, I am demonstrating scaling and security for the Campus Resource Booking System.
  > 
  > In Question 1(a), our peak-demand situation is the 9:00 AM semester lab slot and hackathon registration rush, where 1,500 students concurrently query resource availability. To handle this, I configured three backend container instances—backend-1, backend-2, and backend-3—behind an Nginx load balancer on port 8080. As shown in our distribution test, requests are evenly distributed across all three instances in a 1:1:1 round-robin pattern.
  > 
  > In Question 1(b), using Apache Bench with 1,000 requests and concurrency 50, single-instance throughput was 342 requests per second. With three load-balanced instances, throughput jumped to 918 requests per second—a 167.9% improvement—while mean response time dropped from 145 milliseconds to 54 milliseconds."*

---

### ⏱️ [0:45 – 1:20] SCENE 2: Question 1(c) & 1(d) — Zero-Downtime Failover & Cloud Bursting
* **On Screen:** Show terminal failover output table and the architecture diagram in `ASSIGNMENT_3_REPORT.pdf`.
* **What to say:**
  > *"In Question 1(c), we simulated a mid-test container crash by killing backend-2 during the load test. Initially, without failover, 47 requests failed with HTTP 502 Bad Gateway. After configuring Nginx with `proxy_next_upstream error timeout http_502 http_503` and a 1-second timeout, Nginx immediately reroutes failed requests to surviving backends, achieving zero failed requests and 100% uptime.
  > 
  > In Question 1(d), our architecture connects our frontend, Nginx on port 8080, three backend containers on ports 5001 to 5003, and MongoDB Atlas. I added a Cloud Bursting component: when on-premise CPU utilization exceeds 80% during morning registration spikes, it automatically provisions burst containers on Render or AWS, scaling down once the rush subsides."*

---

### ⏱️ [1:20 – 2:05] SCENE 3: Question 2(a) & 2(b) — Salted Hashes & Multi-Factor Authentication
* **On Screen:** Show terminal running `python backend/tests/test_security_suite.py` and the code in `backend/routes/auth.py`.
* **What to say:**
  > *"Moving to Question 2 on Security:
  > In Question 2(a), our application protects sensitive student roll numbers, emails, and passwords. Passwords are never stored in plaintext—they are salted and hashed using Bcrypt with work factor 12. As verified here, hashing the identical password twice produces two completely different salted hashes, defeating rainbow table attacks.
  > 
  > In Question 2(b), we implemented Multi-Factor Authentication using Time-based One-Time Passwords compatible with Google Authenticator and Microsoft Authenticator via PyOTP. During login, a 6-digit dynamic code is required. Furthermore, Update and Delete APIs like DELETE /api/resources are strictly restricted to staff and admin roles—unauthenticated requests are immediately rejected with HTTP 401 Unauthorized."*

---

### ⏱️ [2:05 – 2:40] SCENE 4: Question 2(c) & 2(d) — Trivy Security Scan & Threat Modeling
* **On Screen:** Show the Trivy scan comparison table in `ASSIGNMENT_3_REPORT.pdf` and terminal.
* **What to say:**
  > *"In Question 2(c), we scanned our Docker image using Trivy. The initial Debian-based `python:3.12-slim` image contained 44 High-severity vulnerabilities. We hardened the image in `Dockerfile.hardened` by migrating to minimal `python:3.12-alpine`, running as an unprivileged non-root user `appuser` with UID 10001, and purging compiler tools. A rescan confirmed zero Critical and zero High vulnerabilities—a 100% reduction in high-severity vulnerabilities and a 96% overall drop.
  > 
  > In Question 2(d), we identified two threat agents: a malicious student attempting insider privilege escalation, mitigated by cryptographically signed JWT tokens and server-side role gating under DPDP Act 2023 and GDPR Article 32; and an external automated botnet attempting credential stuffing, mitigated by TOTP 2FA under GDPR Article 5(1)(f)."*

---

### ⏱️ [2:40 – 3:00] SCENE 5: Conclusion & Assignment-3 GitHub Branch
* **On Screen:** Show your GitHub repository switched to the `assignment-3` branch and the live Render URL.
* **What to say:**
  > *"All scaling configurations, Dockerfiles, and security implementations are committed to the `assignment-3` branch of our GitHub repository, and our live production service is active on Render. Thank you!"*
