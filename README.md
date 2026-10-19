# Cloud-Based Student Attendance Management System

**Apex Institute of Technology & Science (AITS-EDU)**  
A role-based web application connecting Students, Faculty, and Administrators with attendance tracking, interactive Chart.js analytics, duplicate prevention, and CSV exports.

---

## Architecture & How All Files Connect Together

```
                  +--------------------------------------+
                  |         run.py / app.py              |
                  |     (Flask App Factory & DB)         |
                  +-------------------+------------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
+--------v---------+         +--------v---------+         +--------v---------+
|     config.py    |         |    database.py   |         |    models.py     |
| (Env / Settings) |         | (Seeds & Schema) |         | (SQLAlchemy ORM) |
+------------------+         +------------------+         +------------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
+--------v---------+         +--------v---------+         +--------v---------+
|   routes/auth.py |         |  routes/admin.py |         | routes/faculty.py|
|  (Auth & Roles)  |         | (CRUD & Reports) |         | (Marking & Logs) |
+------------------+         +------------------+         +------------------+
         |                            |                            |
+--------v---------+         +--------v---------+                  |
| routes/student.py|         |   routes/api.py  |                  |
| (Analytics & Log)|         | (Chart.js JSON)  |                  |
+------------------+         +------------------+                  |
         |                            |                            |
         +----------------------------+----------------------------+
                                      |
                     +----------------v-----------------+
                     |   templates/ & static/ (UI/UX)   |
                     |  - templates/base.html           |
                     |  - templates/auth/login.html     |
                     |  - templates/admin/*.html        |
                     |  - templates/faculty/*.html      |
                     |  - templates/student/*.html      |
                     |  - static/css/style.css          |
                     |  - static/js/*.js                |
                     +----------------------------------+
```

### Module Connections
1. **Entry Point (`app.py` & `run.py`)**:
   - Assembles the Flask application using `create_app()`.
   - Initializes database tables via `models.db` and auto-populates demo records via `database.init_db(app)`.
   - Mounts role-based blueprints:
     - `auth_bp` (`/`, `/login`, `/logout`, `/dashboard`)
     - `admin_bp` (`/admin/*`)
     - `faculty_bp` (`/faculty/*`)
     - `student_bp` (`/student/*`)
     - `api_bp` (`/api/*`)
   - Provides global context processor for branding and health monitoring (`/health`).

2. **Database & Data Models (`models.py` & `database.py`)**:
   - `User`: Handles credential hashing and role authentication (`admin`, `faculty`, `student`).
   - `Department`, `ClassRoom`, `Faculty`, `Subject`, `Student`, `Attendance`: Real-world relational structure with integrity constraints.
   - Initial seed generates departments, classrooms, faculty accounts, subjects, enrolled students, and 14 days of realistic past attendance logs.

3. **Role-Based Portals (`routes/` & `templates/`)**:
   - **Administrator**: Controls students, faculty, departments, classes, curriculum subjects, 7-day attendance trends, <75% attendance alerts, and CSV exports.
   - **Faculty**: Provides interactive attendance register with 1-click **Mark All Present**, real-time duplicate checks, and subject completion summaries.
   - **Student**: Displays personal attendance compliance rate, status doughnut chart, subject-by-subject percentage bar chart, and filterable history logs.

4. **Dynamic API & Frontend Scripts (`static/js/` & `routes/api.py`)**:
   - `admin.js` connects to `/api/admin/chart-data` for dynamic Chart.js visualizations.
   - `faculty.js` connects to `/api/faculty/check-duplicate` for real-time duplicate warning checks before submitting attendance.
   - `student.js` connects to `/api/student/chart-data` for live gauges and subject breakdown charts.
   - `auth.js` provides role tab toggling, password visibility toggle, and 1-click demo credential filling.

---

## How to Run the Application

1. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

2. **Start the Application**:
   ```powershell
   python run.py
   # OR
   python app.py
   ```

3. **Open in Browser**:
   Navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Demo Login Credentials

| Role | Email / Username | Password | Notes |
|---|---|---|---|
| **Administrator** | `admin@college.edu` | `admin123` | Full control center, student & faculty directories, academics, CSV export |
| **Faculty** | `anurag.verma@college.edu` | `faculty123` | Cloud Computing & DevOps instructor, mark & view attendance |
| **Faculty** | `dr.neha@college.edu` | `faculty123` | Distributed Database Systems instructor |
| **Student** | `aarav.patel@college.edu` | `student123` | CS Sem 6, Section A (Satisfactory attendance: ~91%) |
| **Student** | `rohan.gupta@college.edu` | `student123` | CS Sem 6, Section A (Flagged for attendance < 75%) |

*(Note: The login page also features 1-click quick test buttons to auto-fill these credentials).*
