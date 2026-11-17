# A Man's Benchmark (Personal Growth Dashboard)

> **"Beat your former limits. Academy first. Evidence over feelings."**

A deliberate, responsive web application and productivity workspace built for a university student aspiring to become a research scientist.

---

## 1. Core Philosophy & Architectural Hierarchy

1. **Non-Negotiable #1 Priority (Academy First):**  
   University coursework, exam mastery, and GPA standing strictly come first. Coursework tasks automatically take precedence in priority queues before open-ended research or side projects. Efficiency must reach **90%** before allocating surplus energy to discretionary pursuits.

2. **Beat Your Previous Limits (No External Leaderboards):**  
   You are never compared against other people. Every metric benchmarks your current week against your own all-time personal records (PRs)—including weekly deep-study hours, longest uninterrupted focus block, and weekly study delta.

3. **Evidence Over Feelings:**  
   Self-evaluation on the internal scoreboard mandates concrete, objective evidence (e.g. derivations solved, papers annotated, problem sets verified without solution manuals) rather than vague impressions.

4. **Visual Aesthetic:**  
   Clean, serious personal workspace styled with a light neutral `slate-50` background, crisp white rounded cards with subtle borders (`border-slate-200`), dark navy/charcoal typography, and restrained `indigo-600` accents. Zero gamified neon badges or distracting animations.

---

## 2. Project Architecture & Folder Structure

```text
a-mans-benchmark/
├── vercel.json                 # Vercel serverless Python & static routing configuration
├── requirements.txt            # Python dependencies (Django, DRF, psycopg2, whitenoise, etc.)
├── build_files.sh              # Vercel build script (pip install, collectstatic, migrate)
├── .env.example                # Sample environment variables
├── .gitignore
├── README.md                   # Complete architectural and deployment manual
├── frontend/                   # Stage 1 Prototype & Stage 3 User Interface
│   ├── index.html              # Main application shell with responsive sidebar & tabs
│   ├── css/
│   │   └── style.css           # Custom typography (Plus Jakarta Sans, JetBrains Mono) & utilities
│   └── js/
│       ├── api.js              # Stage 3 API integration layer (Dual-mode: Django REST API + Local fallback)
│       ├── overview.js         # Overview dashboard, Academy Standing card, PR banner, KPIs & chart
│       ├── priorities.js       # Priority task queue, Academy #1 sorting, CRUD & filters
│       ├── scoreboard.js       # 5 Core Pillars, 1-5 scale, mandatory evidence, trajectory chart
│       ├── reflection.js       # Strategic weekly debrief, automated summary strip, archive
│       ├── study.js            # Study session tracker, stopwatch timer, subject-wise allocation
│       └── settings.js         # Workspace PR targets, JSON export/import & demo reset
└── backend/                    # Stage 2 Django REST Framework Backend
    ├── manage.py
    ├── benchmark_project/
    │   ├── __init__.py
    │   ├── settings.py         # Production settings (dj-database-url, WhiteNoise, CORS)
    │   ├── urls.py             # Root routing (/api/..., /admin/..., /)
    │   ├── wsgi.py             # WSGI callable for Vercel serverless deployment
    │   └── asgi.py
    └── growth/                 # Core domain app
        ├── __init__.py
        ├── admin.py            # Django admin models configuration
        ├── apps.py
        ├── models.py           # Task, ScoreArea, WeeklyScore, StudySession, WeeklyReview, UserSettings
        ├── serializers.py      # DRF ModelSerializers with strict validation
        ├── views.py            # ViewSets, DashboardSummaryView, toggle_complete action
        ├── urls.py             # API routes (/api/tasks/, /api/dashboard-summary/, etc.)
        └── migrations/
            ├── __init__.py
            └── 0001_initial.py # Initial migration with pre-seeded 5 Core Pillars
```

---

## 3. Functional Modules

### A. Navigation
- **Desktop Sidebar:** Clean brand identity, scientist status indicator, core law reminder, and seamless tab routing.
- **Mobile Navigation:** Compact top header with mobile hamburger drawer for touch devices.

### B. Overview Dashboard
- **Priority #1 Academy Standing Card:** Compares current execution percentage against the 90% target, tracking completed vs total coursework tasks.
- **Personal Record (PR) Challenge Banner:** Displays the user's weekly intention alongside live benchmark bars:
  - Current Week Deep Study Hours vs All-Time Weekly PR.
  - Longest Uninterrupted Session This Week vs Single-Session PR.
- **4 Summary KPI Cards:**
  1. Academy Priorities Completed (with completion rate badge).
  2. Pending Priorities (highlighting urgent High-priority tasks).
  3. Study Hours vs Last Week (+/- delta and target record to beat).
  4. **Limit-Breaker Index:** Composite score (0–100) combining 40% Academy execution, 35% Study PR progress, and 25% Scoreboard average.
- **Today's & Urgent Priorities:** Automatically surfaces University Coursework tasks with an `Academy #1` badge, sorted ahead of research or side projects, with one-click completion.
- **Internal Scoreboard Preview:** Live status bars for the 5 core pillars.
- **Weekly Study Activity Chart:** Chart.js bar chart displaying deep-work hours over the last 7 days.

### C. My Priorities (Task Management)
- **Fields:** Title, Standard of Completion / Definition of Done, Category (`University Coursework`, `Research`, `Programming and Technical Skills`, `Reading`, `Personal Development`, `Health and Fitness`, `Other`), Priority (`High`, `Medium`, `Low`), Due Date, Status (`Pending`, `In Progress`, `Completed`).
- **Features:** Full CRUD (Add, Edit, Delete, Toggle Complete), multi-criteria filtering, and sorting (`Academy First`, `Due Date`, `Priority`, `Status`).

### D. Internal Scoreboard (Evidence-Based Self-Evaluation)
- **5 Core Pillars:**
  1. Academic Mastery (1st Priority)
  2. Scientific Thinking & Research
  3. Deep Work & Limit-Breaking Discipline
  4. Physical Stamina & Recovery
  5. Character & Intellectual Honesty
- **Rules:** 1–5 rating scale, mandatory objective evidence text field (no empty reviews), week selector, historical mini-badges, duplicate entry constraint per pillar/week, and multi-week Chart.js trajectory line chart.

### E. Weekly Reflection
- **Structured Fields:** Accomplishments, Failures & Shortcomings, Distractions & Energy Leaks, Lessons Learned, Next Week Improvements, and Three Non-Negotiable Priorities (Priority #1 strictly reserved for Academy).
- **Features:** Automated weekly summary strip (Tasks Completed, Logged Hours, Scoreboard Avg) and clickable Reflection Archive.

### F. Study Tracker
- **Fields:** Subject/Topic, Date, Duration (minutes), Optional Notes.
- **Features:** 7-day, 30-day, and all-time KPI cards; Live Focus Stopwatch Timer; Chart.js horizontal bar chart of subject-wise allocation; and chronological session history table with delete functionality.

### G. Settings & Data Portability
- **Configuration:** Student Profile, Target Execution (90%), Weekly Study PR, Longest Session PR, and Weekly Intention.
- **Data Safety:** Instant Export Workspace Snapshot (JSON), Import Snapshot, and Reset Demo Data modal.

---

## 4. Stage 1: Instant Interactive Prototype Testing

You can run the interactive frontend prototype immediately without configuring any backend:

1. Open `frontend/index.html` directly in any web browser, or serve it using Python's built-in HTTP server:
   ```bash
   cd frontend
   python -m http.server 8080
   ```
2. Navigate to `http://localhost:8080`.
3. The Stage 3 integration layer (`api.js`) automatically detects that the backend is offline and seamlessly mounts the local persistence engine loaded with realistic scientist demo data. All CRUD actions, charts, scoreboards, and settings are fully functional and persistent in `localStorage`.

---

## 5. Stage 2 & 3: Local Django REST API Setup

### Prerequisites
- Python 3.10+
- (Optional) PostgreSQL or local SQLite (default fallback)

### Step 1: Create Virtual Environment & Install Dependencies
```bash
# From the repository root
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(If `DATABASE_URL` is omitted, Django automatically uses `db.sqlite3` for zero-configuration local development).*

### Step 3: Run Migrations & Start Server
```bash
python backend/manage.py migrate
python backend/manage.py runserver 8000
```

Visit `http://localhost:8000/`. The Django app will serve the application with live REST API endpoints at `/api/...`.

---

## 6. Step-by-Step Vercel Deployment Guide

Deploying **A Man's Benchmark** to Vercel with a free cloud PostgreSQL database (via **Supabase** or **Neon**) takes less than 5 minutes.

### Step 1: Provision a Free Cloud PostgreSQL Database
Choose either **Supabase** or **Neon**:

#### Option A: Neon (Recommended for instant serverless PostgreSQL)
1. Go to [neon.tech](https://neon.tech) and create a free account.
2. Create a new project named `a-mans-benchmark`.
3. Copy the **Connection String** (e.g., `postgresql://alex:password@ep-cool-cloud.us-east-2.aws.neon.tech/neondb?sslmode=require`).

#### Option B: Supabase
1. Go to [supabase.com](https://supabase.com) and create a free project.
2. Go to **Project Settings** → **Database** → **Connection String** → **URI**.
3. Copy the URI and replace `[YOUR-PASSWORD]` with your database password.

---

### Step 2: Push Repository to GitHub
```bash
git init
git add .
git commit -m "feat: complete A Man's Benchmark application"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/a-mans-benchmark.git
git push -u origin main
```

---

### Step 3: Import Project to Vercel
1. Log in to [vercel.com](https://vercel.com).
2. Click **Add New** → **Project**.
3. Import your `a-mans-benchmark` GitHub repository.
4. In the **Configure Project** screen:
   - **Framework Preset:** Leave as *Other*.
   - **Root Directory:** `./` (leave default).

---

### Step 4: Configure Environment Variables in Vercel
Under the **Environment Variables** section, add the following:

| Variable Name | Value | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://...` | Connection URI from Neon or Supabase |
| `SECRET_KEY` | *(A long random string)* | Production secret key for Django |
| `DEBUG` | `False` | Disables debug mode in production |
| `ALLOWED_HOSTS` | `.vercel.app` | Allows requests from your Vercel domains |

Click **Deploy**.

---

### Step 5: Verify Deployment & Automated Migrations
- `build_files.sh` automatically installs dependencies, runs `collectstatic`, and applies database migrations (`migrate --noinput`) during Vercel's build phase.
- Once deployed, your production URL (e.g. `https://a-mans-benchmark.vercel.app`) will be live!
- The frontend will detect the live Django REST API backend and display the green `Django REST API` status badge in the bottom-left profile widget.
