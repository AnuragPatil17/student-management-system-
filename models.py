from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """
    Users Table:
    - ID, Name, Email, Password Hash, Role (admin, faculty, student)
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'faculty', 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    student_profile = db.relationship('Student', backref='user_account', uselist=False, cascade="all, delete-orphan")
    faculty_profile = db.relationship('Faculty', backref='user_account', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }


class Department(db.Model):
    """Departments Table: Computer Science, Information Technology, etc."""
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # e.g., 'CS', 'IT', 'ECE'
    name = db.Column(db.String(100), nullable=False)               # e.g., 'Computer Science & Engineering'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    classes = db.relationship('ClassRoom', backref='department', cascade="all, delete-orphan")
    faculty_members = db.relationship('Faculty', backref='department', cascade="all, delete-orphan")
    students = db.relationship('Student', backref='department', cascade="all, delete-orphan")
    subjects = db.relationship('Subject', backref='department', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'faculty_count': len(self.faculty_members),
            'student_count': len(self.students)
        }


class ClassRoom(db.Model):
    """
    Classes Table:
    - class ID, department, semester, division/section, academic_year
    """
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)              # 1 through 8
    division = db.Column(db.String(10), nullable=False)           # 'A', 'B', 'C'
    academic_year = db.Column(db.String(20), default='2025-2026') # e.g., '2025-2026'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    students = db.relationship('Student', backref='classroom', cascade="all, delete-orphan")
    attendance_records = db.relationship('Attendance', backref='classroom', cascade="all, delete-orphan")

    @property
    def display_name(self):
        dept_code = self.department.code if self.department else 'Dept'
        return f"{dept_code} - Sem {self.semester} (Sec {self.division})"

    def to_dict(self):
        return {
            'id': self.id,
            'department_id': self.department_id,
            'department_code': self.department.code if self.department else '',
            'semester': self.semester,
            'division': self.division,
            'academic_year': self.academic_year,
            'display_name': self.display_name,
            'student_count': len(self.students)
        }


class Faculty(db.Model):
    """
    Faculty Table:
    - faculty ID, name, department, designation, phone, user_id
    """
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    faculty_id_code = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'FAC-CS-01'
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    designation = db.Column(db.String(80), default='Assistant Professor')    # Professor, HOD, etc.
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subjects = db.relationship('Subject', backref='assigned_faculty', lazy='dynamic')
    marked_attendance = db.relationship('Attendance', backref='recorded_by', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'faculty_id_code': self.faculty_id_code,
            'name': self.name,
            'email': self.user_account.email if self.user_account else '',
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else '',
            'designation': self.designation,
            'phone': self.phone or '',
            'assigned_subjects_count': self.subjects.count()
        }


class Subject(db.Model):
    """
    Subjects Table:
    - subject ID, subject name, code, department ID, semester, faculty ID
    """
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)       # e.g. 'CS601'
    name = db.Column(db.String(100), nullable=False)                    # e.g. 'Cloud Computing'
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)                   # e.g. 6
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='SET NULL'), nullable=True)
    credits = db.Column(db.Integer, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attendance_records = db.relationship('Attendance', backref='subject', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'department_id': self.department_id,
            'department_code': self.department.code if self.department else '',
            'semester': self.semester,
            'faculty_id': self.faculty_id,
            'faculty_name': self.assigned_faculty.name if self.assigned_faculty else 'Unassigned',
            'credits': self.credits
        }


class Student(db.Model):
    """
    Students Table:
    - student ID, user_id, roll number, department, semester, class
    """
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False, index=True) # e.g. 'CS2026-001'
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    guardian_phone = db.Column(db.String(20), nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'roll_number': self.roll_number,
            'name': self.name,
            'email': self.user_account.email if self.user_account else '',
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else '',
            'class_id': self.class_id,
            'class_name': self.classroom.display_name if self.classroom else '',
            'semester': self.semester,
            'phone': self.phone or '',
            'guardian_phone': self.guardian_phone or ''
        }


class Attendance(db.Model):
    """
    Attendance Table:
    - attendance ID, student ID, subject ID, date, status ('Present', 'Absent', 'Late')
    - class ID, marked_by_faculty_id, remarks, created_at, updated_at
    - Unique constraint: (student_id, subject_id, date) prevents accidental duplicates!
    """
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, index=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    status = db.Column(db.String(20), nullable=False)  # 'Present', 'Absent', 'Late'
    marked_by_faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='SET NULL'), nullable=True)
    remarks = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint ensures no duplicate attendance for the same student + subject + date
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'date', name='uq_student_subject_date'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else '',
            'student_roll': self.student.roll_number if self.student else '',
            'subject_id': self.subject_id,
            'subject_code': self.subject.code if self.subject else '',
            'subject_name': self.subject.name if self.subject else '',
            'class_id': self.class_id,
            'class_name': self.classroom.display_name if self.classroom else '',
            'date': self.date.strftime('%Y-%m-%d'),
            'status': self.status,
            'remarks': self.remarks or '',
            'marked_by': self.recorded_by.name if self.recorded_by else 'System'
        }
