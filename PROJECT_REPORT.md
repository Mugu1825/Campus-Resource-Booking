# Campus Resource Booking System (CRBS)
**Project Report | Full-Stack Web Development**  
**Author:** Mugunth (Computer Science & Engineering)  
**Live Application:** [https://campus-resource-booking-cqt7.onrender.com](https://campus-resource-booking-cqt7.onrender.com)  
**GitHub Repository:** [https://github.com/Mugu1825/Campus-Resource-Booking](https://github.com/Mugu1825/Campus-Resource-Booking)  

---

## 1. Project Overview & Motivation

In our college, reserving shared facilities—like computer labs, seminar halls, projectors, or the auditorium—is still handled manually using paper registers or informal messages. This causes frequent scheduling clashes, confusion over who approved what, and no real-time way for students to know if a lab is free.

I built the **Campus Resource Booking System (CRBS)** to solve this problem with a clean, fully functional web app. Rather than building a basic CRUD application with just one generic user type, I designed it around real campus requirements:
- **3 distinct user roles:** Student, Staff, and Admin.
- **Automatic department detection** from college register numbers.
- **Real-time hourly slot checking** so students see what's free before booking.
- **Automatic conflict prevention** to stop double bookings before they happen.
- **Special rules for events** like 48-hour hackathons vs regular study sessions.

---

## 2. User Roles & Workflow

| Role | How It Works in the App | Key Permissions & Rules |
|---|---|---|
| **Student** | Self-registers using their college roll number (e.g. `25CSE1011`). The app checks the format and automatically extracts their department. Students can browse resources, check hourly slot availability, submit booking requests, and cancel pending requests. | • Regular bookings: max 4 hours (same-day)<br/>• Hackathon bookings: up to 48 hours<br/>• Can only cancel their own pending requests |
| **Staff** | Registers with their department. Their account is set to `pending` until the Admin approves it. Once active, staff can manage standard labs/rooms and approve student bookings for their department. | • Can approve standard resources<br/>• *Cannot* create or approve premium halls or hackathons (preventing misuse) |
| **Admin** | Superuser account. Reviews and approves new staff registrations, manages all resources (both standard and premium), approves multi-day hackathons and high-value spaces (like the main auditorium), and can promote or change user roles. | • Full system authority<br/>• Exclusive approval for premium & hackathons<br/>• Monitors live stats and user accounts |

---

## 3. Technology Choices & Architecture

- **Backend (Python & Flask):** I chose Flask because it is lightweight, fast to get running, and keeps REST API routes clean and organized using blueprints. Password security uses `flask-bcrypt` for salted hashing, and authentication uses stateless `flask-jwt-extended` tokens.
- **Database (MongoDB Atlas):** College resources and bookings naturally map to JSON documents. Using MongoDB Atlas gives a reliable cloud database with built-in TLS encryption and connection pooling.
- **Frontend (HTML5, Modern CSS, Vanilla JavaScript):** I intentionally avoided bulky frameworks like React to keep the site fast, clean, and dependency-free. Modular JS files and a custom responsive CSS design system handle the UI.
- **Containerization (Docker & Nginx):** I packaged the frontend and backend together into a single Docker container. Nginx serves the static HTML/CSS/JS and acts as a reverse proxy forwarding `/api/*` requests to Gunicorn. This eliminated all CORS headaches and allowed hosting everything on Render's free tier under one unified URL.

---

## 4. Database Design (Collections)

### `users`
Stores all user profiles.
- `name`, `email` (unique index, case-insensitive)
- `password` (bcrypt salted hash, never stored in plain text)
- `role` (`student`, `staff`, or `admin`)
- `account_status` (`active`, `pending`, or `rejected`)
- `register_no` (unique sparse index, format: `25CSE1011`)
- `department` (e.g. `CSE`, `ECE`, `MEE`)

### `resources`
Stores campus facilities.
- `name` (e.g. "Computing Lab 1 (AI / ML)", "Dr. APJ Abdul Kalam Auditorium")
- `type` (`lab`, `room`, `equipment`, `auditorium`)
- `tier` (`standard` managed by staff, or `premium` managed by admin)
- `location`, `capacity`
- `is_available` (boolean toggle switch for maintenance)

### `bookings`
Stores reservation records.
- `user_id` (references student)
- `resource_id` (references facility)
- `date_start`, `date_end`
- `start_slot`, `end_slot` (e.g. `10:00` to `12:00`)
- `is_hackathon` (boolean) & `hackathon_event` (event title)
- `status` (`pending`, `approved`, `rejected`, `cancelled`)
- `approved_by` (ID of approving staff or admin)

---

## 5. Key Features & Business Logic

### A. Register Number Format Validation
Students must register with a valid college roll number format: 2-digit year + 3-character department code + 4 digits (e.g. `25CSE1011`). The app uses regex validation (`^\d{2}(CSE|ECE|EEE|MEE|INT|CIV|CHE|AER|BIO|MBA|MCA)\d{4}$`) on both client and server, and automatically parses the department without asking the student to re-enter it.

### B. Double-Booking Conflict Engine
Before creating any booking, the backend queries active reservations on that resource (`pending` or `approved`). If dates overlap, it compares slot indices from `09:00` to `21:00`. If any slot collides, the request is blocked immediately with a clear error message.

### C. Live Slot Availability Grid
When a student clicks "Check Availability" on any resource card, an interactive modal shows the full slot schedule for the selected date. Free slots appear in green outline, booked slots appear in red, and selected slots highlight in blue. Clicking "Book this slot" auto-fills the booking form.

### D. Dual Ruleset (Regular vs. Hackathon)
- **Regular Bookings:** Max 4 hours, same-day only.
- **Hackathon Bookings:** Multi-day blocks allowed up to 48 hours. Requires an event name, and routes exclusively to Admin for sign-off.

---

## 6. Challenges Faced & Solutions

1. **CORS & Multiple Domains:** Running frontend and backend on separate Render services caused cross-origin blocking and required managing two separate URLs. I resolved this by writing a custom Docker container with Nginx as a reverse proxy, serving the frontend and proxying `/api/*` to Gunicorn under one single domain.
2. **MongoDB Cold Boot Connection:** Calling index creation on application startup caused crashes during cold starts when Atlas took a few seconds to connect. I moved index creation into a one-shot `@app.before_request` hook so the server boots cleanly without errors.
3. **Role Gating & Security:** To prevent staff from approving high-value facilities or overriding multi-day events, I wrote custom Flask decorators (`@staff_required` and `@admin_required`) that inspect the JWT token claims before any route executes.

---

## 7. Testing & Verification

I wrote an automated verification suite (`backend/tests/verify_codebase.py`) that tests all 31 core scenarios against the live database:
- ✅ Public health check & department list
- ✅ Register number regex validation & department extraction
- ✅ Staff approval lifecycle (pending gate $\rightarrow$ admin approval $\rightarrow$ login)
- ✅ Resource tier restrictions (staff cannot create premium)
- ✅ Booking rules (4-hour regular limit, 48-hour hackathon, conflict detection)
- ✅ Hierarchical approvals (staff blocked on premium/hackathons)
- ✅ Student self-cancellation rules
- **Result: 31 / 31 tests passed (100% success rate).**

---

## 8. Conclusion & What I Learned

Building this project gave me practical experience taking a full-stack web application from idea to production:
- Structuring RESTful APIs with Flask blueprints.
- Designing document schemas and indexes in MongoDB Atlas.
- Writing clean, framework-free JavaScript for interactive UI elements.
- Packaging multi-tier services using Docker and Nginx.
- Deploying and monitoring a live web application on Render.
