# Campus Resource Booking System (CRBS)

A full-stack web application for booking campus resources with role-based access control.

## Roles
| Role | Description |
|------|-------------|
| **Student** | Self-register with college register number. Browse and book resources. |
| **Staff** | Register (pending admin approval). Manage standard resources and approve standard bookings. |
| **Admin** | Seeded via script. Full system oversight. Approves staff, premium resources, and hackathon bookings. |

## Tech Stack
- **Backend**: Python / Flask
- **Database**: MongoDB Atlas
- **Frontend**: HTML + CSS + Vanilla JS
- **Deployment**: Render

---

## MongoDB Atlas Setup

### Step 1 — Create a free account
1. Go to [cloud.mongodb.com](https://cloud.mongodb.com) and sign up
2. Choose **Free (M0)** tier when prompted

### Step 2 — Create a cluster
1. Click **Create** → Select **M0 Free**
2. Choose a cloud region (pick one geographically close to you)
3. Name your cluster (e.g. `campus-booking`)
4. Click **Create Deployment**

### Step 3 — Create a database user
1. In the left sidebar, go to **Security → Database Access**
2. Click **Add New Database User**
3. Choose **Password** authentication
4. Set username (e.g. `crbs_user`) and a strong password — **save these**
5. Set role to **Atlas admin** (or read/write to `campus_booking` database)
6. Click **Add User**

### Step 4 — Allow network access
1. Go to **Security → Network Access**
2. Click **Add IP Address**
3. Click **Allow Access from Anywhere** (adds `0.0.0.0/0`)
   > This is required for Render to connect to Atlas
4. Click **Confirm**

### Step 5 — Get your connection string
1. Go to **Deployment → Database**
2. Click **Connect** on your cluster
3. Choose **Connect your application**
4. Select **Python** driver, version **3.12 or later**
5. Copy the URI — it looks like:
   ```
   mongodb+srv://crbs_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<password>` with your actual password
7. Append the database name:
   ```
   mongodb+srv://crbs_user:yourpassword@cluster0.xxxxx.mongodb.net/campus_booking?retryWrites=true&w=majority
   ```

---

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```env
MONGO_URI=mongodb+srv://crbs_user:yourpassword@cluster0.xxxxx.mongodb.net/campus_booking?retryWrites=true&w=majority
JWT_SECRET=your-super-secret-key-change-this
```

Seed the first admin account:
```bash
python seed_admin.py
```

Run the backend:
```bash
python app.py
# or: flask run --port 5000
```

### Frontend

The frontend is pure static files. Open `frontend/index.html` directly in a browser, or serve with any static server:

```bash
# From the project root
cd frontend
python -m http.server 8080
# Visit http://localhost:8080
```

Make sure `js/api.js` has `API_BASE = 'http://localhost:5000/api'`

---

## Running with Docker (Recommended)

You can run the entire application (frontend, backend, Nginx reverse proxy) in a single container:

```bash
# Build and run with Docker Compose
docker compose up --build

# Visit http://localhost:3000 in your browser
```

Or build and run directly with Docker CLI:
```bash
docker build -t campus-booking .
docker run -p 3000:80 \
  -e MONGO_URI="mongodb+srv://..." \
  -e JWT_SECRET="your-secret-key" \
  campus-booking
```

---

## Deployment on Render (with Docker)

Render can build and run this containerized application with a single Web Service!

### Step 1 — Push to GitHub
Initialize git and push the project to a GitHub repository:
```bash
git init
git add .
git commit -m "feat: complete campus resource booking system with Docker support"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

### Step 2 — Deploy on Render
1. Log in to [render.com](https://render.com)
2. Click **New +** → **Web Service**
3. Select **Build and deploy from a Git repository** and pick your repo
4. Configure the service:
   * **Name**: `campus-resource-booking`
   * **Runtime**: **Docker** (it will auto-detect the `Dockerfile`)
   * **Plan**: **Free**
5. Under **Environment Variables**, add:
   * `MONGO_URI` = your MongoDB Atlas connection string
   * `JWT_SECRET` = any random 32+ character string
6. Click **Deploy Web Service**

Render will automatically build the Docker image, launch the Gunicorn backend and Nginx reverse proxy, and provide a single public URL (e.g. `https://campus-resource-booking.onrender.com`).

---

## Register Number Format

Student register numbers follow the format: `YY` + `DEPT` + `NNNN`

| Part | Description | Example |
|------|-------------|---------|
| `YY` | 2-digit admission year | `25` |
| `DEPT` | Department code (exactly 3 uppercase letters) | `CSE` |
| `NNNN` | 4-digit roll number | `1011` |

**Examples**: `25CSE1011`, `24ECE0042`, `23EEE1005`

### Department Codes
| Code | Department |
|------|-----------|
| CSE | Computer Science & Engineering |
| ECE | Electronics & Communication Engineering |
| EEE | Electrical & Electronics Engineering |
| MEE | Mechanical Engineering |
| INT | Information Technology |
| CIV | Civil Engineering |
| CHE | Chemical Engineering |
| AER | Aeronautical Engineering |
| BIO | Biotechnology |
| MBA | Master of Business Administration |
| MCA | Master of Computer Applications |

---

## API Overview

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/student` | Student registration |
| POST | `/api/auth/register/staff` | Staff registration (pending approval) |
| POST | `/api/auth/login` | Login — returns JWT |
| GET | `/api/auth/departments` | Get list of department codes |

### Resources
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/resources` | All | List resources |
| GET | `/api/resources/:id` | All | Resource detail |
| GET | `/api/resources/:id/availability` | All | Available slots for a date |
| POST | `/api/resources` | Staff/Admin | Add resource |
| PUT | `/api/resources/:id` | Staff/Admin | Update resource |
| DELETE | `/api/resources/:id` | Staff/Admin | Delete resource |
| PATCH | `/api/resources/:id/toggle` | Staff/Admin | Toggle availability |

### Bookings
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/bookings` | Staff/Admin | All bookings |
| GET | `/api/bookings/my` | Student | Own bookings |
| POST | `/api/bookings` | Student | Create booking |
| PUT | `/api/bookings/:id/approve` | Staff/Admin | Approve booking |
| PUT | `/api/bookings/:id/reject` | Staff/Admin | Reject booking |
| DELETE | `/api/bookings/:id` | Student/Admin | Cancel booking |

### Admin
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/admin/users` | Admin | All users |
| GET | `/api/admin/staff/pending` | Admin | Pending staff registrations |
| PUT | `/api/admin/staff/:id/approve` | Admin | Approve staff account |
| PUT | `/api/admin/staff/:id/reject` | Admin | Reject staff account |
| PUT | `/api/admin/users/:id/role` | Admin | Change user role |

---

## Project Structure
```
campus-booking/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── seed_admin.py
│   ├── .env                    (create this, not committed)
│   ├── routes/
│   │   ├── auth.py
│   │   ├── resources.py
│   │   ├── bookings.py
│   │   └── admin.py
│   └── middleware/
│       └── auth_middleware.py
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── register-student.html
│   ├── register-staff.html
│   ├── dashboard.html
│   ├── staff.html
│   ├── admin.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── api.js
│       ├── auth.js
│       ├── dashboard.js
│       ├── staff.js
│       └── admin.js
├── postman/
│   └── campus_booking.json
├── render.yaml
└── README.md
```
