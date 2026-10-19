import io
import csv
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from models import db, User, Department, ClassRoom, Faculty, Subject, Student, Attendance
from routes import login_required, role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
@role_required(['admin'])
def restrict_to_admin():
    """Ensure all routes in admin_bp require admin role."""
    pass

@admin_bp.route('/dashboard')
def dashboard():
    """Admin Dashboard Control Center with metrics, trends, and alerts."""
    total_students = Student.query.count()
    total_faculty = Faculty.query.count()
    total_departments = Department.query.count()
    total_attendance_records = Attendance.query.count()

    # Identify students with attendance < 75%
    students = Student.query.all()
    low_attendance_students = []

    for s in students:
        total = Attendance.query.filter_by(student_id=s.id).count()
        if total > 0:
            present = Attendance.query.filter_by(student_id=s.id, status='Present').count()
            rate = round((present / total) * 100, 1)
            if rate < 75.0:
                low_attendance_students.append({
                    'student': s,
                    'percentage': rate
                })

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_faculty=total_faculty,
        total_departments=total_departments,
        total_attendance_records=total_attendance_records,
        low_attendance_students=low_attendance_students,
        active_page='admin_dashboard'
    )

# -------------------------------------------------------------------------
# Student Management
# -------------------------------------------------------------------------
@admin_bp.route('/students')
def students():
    """Manage and list all registered students."""
    student_list = Student.query.order_by(Student.roll_number).all()
    departments = Department.query.order_by(Department.name).all()
    classes = ClassRoom.query.all()

    return render_template(
        'admin/students.html',
        students=student_list,
        departments=departments,
        classes=classes,
        active_page='admin_students'
    )

@admin_bp.route('/students/add', methods=['POST'])
def add_student():
    """Enroll a new student and create associated user account."""
    name = request.form.get('name', '').strip()
    roll_number = request.form.get('roll_number', '').strip().upper()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    department_id = request.form.get('department_id', type=int)
    class_id = request.form.get('class_id', type=int)
    semester = request.form.get('semester', type=int)
    phone = request.form.get('phone', '').strip()
    guardian_phone = request.form.get('guardian_phone', '').strip()

    if not name or not roll_number or not email or not password or not department_id or not class_id:
        flash('All required fields must be filled.', 'danger')
        return redirect(url_for('admin.students'))

    # Check for duplicate email or roll number
    if User.query.filter((User.email.ilike(email)) | (User.username.ilike(roll_number))).first():
        flash(f'An account with email {email} or username {roll_number} already exists.', 'warning')
        return redirect(url_for('admin.students'))

    if Student.query.filter_by(roll_number=roll_number).first():
        flash(f'Student roll number {roll_number} is already registered.', 'warning')
        return redirect(url_for('admin.students'))

    user = User(
        name=name,
        email=email,
        username=roll_number.lower(),
        role='student'
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    student = Student(
        user_id=user.id,
        roll_number=roll_number,
        name=name,
        department_id=department_id,
        class_id=class_id,
        semester=semester,
        phone=phone,
        guardian_phone=guardian_phone
    )
    db.session.add(student)
    db.session.commit()

    flash(f'Student {name} ({roll_number}) enrolled successfully!', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/students/edit/<int:id>', methods=['POST'])
def edit_student(id):
    """Edit student details and optionally reset password."""
    student = Student.query.get_or_404(id)
    name = request.form.get('name', '').strip()
    roll_number = request.form.get('roll_number', '').strip().upper()
    email = request.form.get('email', '').strip().lower()
    department_id = request.form.get('department_id', type=int)
    class_id = request.form.get('class_id', type=int)
    semester = request.form.get('semester', type=int)
    phone = request.form.get('phone', '').strip()
    new_password = request.form.get('password', '').strip()

    # Roll number conflict check
    existing_roll = Student.query.filter(Student.roll_number == roll_number, Student.id != id).first()
    if existing_roll:
        flash(f'Roll number {roll_number} already belongs to another student.', 'warning')
        return redirect(url_for('admin.students'))

    # Email conflict check
    existing_user = User.query.filter(User.email.ilike(email), User.id != student.user_id).first()
    if existing_user:
        flash(f'Email {email} is already in use by another account.', 'warning')
        return redirect(url_for('admin.students'))

    student.name = name
    student.roll_number = roll_number
    student.department_id = department_id
    student.class_id = class_id
    student.semester = semester
    student.phone = phone

    if student.user_account:
        student.user_account.name = name
        student.user_account.email = email
        if new_password:
            student.user_account.set_password(new_password)

    db.session.commit()
    flash(f'Student profile for {name} updated successfully.', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/students/delete/<int:id>', methods=['POST'])
def delete_student(id):
    """Delete student profile and associated user account."""
    student = Student.query.get_or_404(id)
    name = student.name
    roll = student.roll_number
    user = student.user_account

    if user:
        db.session.delete(user)
    else:
        db.session.delete(student)

    db.session.commit()
    flash(f'Student {name} ({roll}) has been deleted.', 'info')
    return redirect(url_for('admin.students'))

# -------------------------------------------------------------------------
# Faculty Management
# -------------------------------------------------------------------------
@admin_bp.route('/faculty')
def faculty():
    """List and manage college faculty members."""
    faculty_list = Faculty.query.all()
    departments = Department.query.order_by(Department.name).all()

    return render_template(
        'admin/faculty.html',
        faculty_list=faculty_list,
        departments=departments,
        active_page='admin_faculty'
    )

@admin_bp.route('/faculty/add', methods=['POST'])
def add_faculty():
    """Register a new faculty instructor."""
    name = request.form.get('name', '').strip()
    code = request.form.get('faculty_id_code', '').strip().upper()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    department_id = request.form.get('department_id', type=int)
    designation = request.form.get('designation', 'Assistant Professor').strip()
    phone = request.form.get('phone', '').strip()

    if not name or not code or not email or not password or not department_id:
        flash('All required fields must be provided.', 'danger')
        return redirect(url_for('admin.faculty'))

    if User.query.filter((User.email.ilike(email)) | (User.username.ilike(code))).first():
        flash(f'An account with email {email} or code {code} already exists.', 'warning')
        return redirect(url_for('admin.faculty'))

    if Faculty.query.filter_by(faculty_id_code=code).first():
        flash(f'Faculty ID Code {code} is already registered.', 'warning')
        return redirect(url_for('admin.faculty'))

    user = User(
        name=name,
        email=email,
        username=code.lower(),
        role='faculty'
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    faculty_profile = Faculty(
        user_id=user.id,
        faculty_id_code=code,
        name=name,
        department_id=department_id,
        designation=designation,
        phone=phone
    )
    db.session.add(faculty_profile)
    db.session.commit()

    flash(f'Faculty member {name} registered successfully!', 'success')
    return redirect(url_for('admin.faculty'))

@admin_bp.route('/faculty/edit/<int:id>', methods=['POST'])
def edit_faculty(id):
    """Edit faculty details and optional password reset."""
    fac = Faculty.query.get_or_404(id)
    name = request.form.get('name', '').strip()
    code = request.form.get('faculty_id_code', '').strip().upper()
    email = request.form.get('email', '').strip().lower()
    department_id = request.form.get('department_id', type=int)
    designation = request.form.get('designation', '').strip()
    phone = request.form.get('phone', '').strip()
    new_password = request.form.get('password', '').strip()

    fac.name = name
    fac.faculty_id_code = code
    fac.department_id = department_id
    fac.designation = designation
    fac.phone = phone

    if fac.user_account:
        fac.user_account.name = name
        fac.user_account.email = email
        if new_password:
            fac.user_account.set_password(new_password)

    db.session.commit()
    flash(f'Faculty details for {name} updated successfully.', 'success')
    return redirect(url_for('admin.faculty'))

@admin_bp.route('/faculty/delete/<int:id>', methods=['POST'])
def delete_faculty(id):
    """Delete faculty member and their user account."""
    fac = Faculty.query.get_or_404(id)
    name = fac.name
    user = fac.user_account

    # Unassign assigned subjects
    for subj in fac.subjects:
        subj.faculty_id = None

    if user:
        db.session.delete(user)
    else:
        db.session.delete(fac)

    db.session.commit()
    flash(f'Faculty member {name} has been removed.', 'info')
    return redirect(url_for('admin.faculty'))

# -------------------------------------------------------------------------
# Academics & Curriculum Management
# -------------------------------------------------------------------------
@admin_bp.route('/academics')
def academics():
    """Academics, Departments, Classes, and Subjects configuration."""
    departments = Department.query.order_by(Department.name).all()
    classes = ClassRoom.query.all()
    subjects = Subject.query.order_by(Subject.code).all()
    faculty_list = Faculty.query.order_by(Faculty.name).all()

    return render_template(
        'admin/academics.html',
        departments=departments,
        classes=classes,
        subjects=subjects,
        faculty_list=faculty_list,
        active_page='admin_academics'
    )

@admin_bp.route('/departments/add', methods=['POST'])
def add_department():
    """Create a new academic department."""
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()

    if not code or not name:
        flash('Department code and name are required.', 'danger')
        return redirect(url_for('admin.academics'))

    if Department.query.filter_by(code=code).first():
        flash(f'Department code {code} already exists.', 'warning')
        return redirect(url_for('admin.academics'))

    dept = Department(code=code, name=name)
    db.session.add(dept)
    db.session.commit()
    flash(f'Department "{name} ({code})" created successfully!', 'success')
    return redirect(url_for('admin.academics'))

@admin_bp.route('/departments/delete/<int:id>', methods=['POST'])
def delete_department(id):
    """Delete an academic department."""
    dept = Department.query.get_or_404(id)
    name = dept.name
    db.session.delete(dept)
    db.session.commit()
    flash(f'Department {name} deleted.', 'info')
    return redirect(url_for('admin.academics'))

@admin_bp.route('/classes/add', methods=['POST'])
def add_class():
    """Create a new class section."""
    dept_id = request.form.get('department_id', type=int)
    semester = request.form.get('semester', type=int)
    division = request.form.get('division', '').strip().upper()
    academic_year = request.form.get('academic_year', '2025-2026').strip()

    if not dept_id or not semester or not division:
        flash('Department, semester, and division are required.', 'danger')
        return redirect(url_for('admin.academics'))

    cl = ClassRoom(
        department_id=dept_id,
        semester=semester,
        division=division,
        academic_year=academic_year
    )
    db.session.add(cl)
    db.session.commit()
    flash(f'Class section {cl.display_name} created successfully!', 'success')
    return redirect(url_for('admin.academics'))

@admin_bp.route('/classes/delete/<int:id>', methods=['POST'])
def delete_class(id):
    """Delete class section."""
    cl = ClassRoom.query.get_or_404(id)
    db.session.delete(cl)
    db.session.commit()
    flash('Class section deleted.', 'info')
    return redirect(url_for('admin.academics'))

@admin_bp.route('/subjects/add', methods=['POST'])
def add_subject():
    """Add a curriculum course subject."""
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()
    dept_id = request.form.get('department_id', type=int)
    semester = request.form.get('semester', type=int)
    faculty_id = request.form.get('faculty_id', type=int) or None
    credits = request.form.get('credits', 3, type=int)

    if not code or not name or not dept_id or not semester:
        flash('Course code, title, department, and semester are required.', 'danger')
        return redirect(url_for('admin.academics'))

    if Subject.query.filter_by(code=code).first():
        flash(f'Subject code {code} already exists.', 'warning')
        return redirect(url_for('admin.academics'))

    subj = Subject(
        code=code,
        name=name,
        department_id=dept_id,
        semester=semester,
        faculty_id=faculty_id,
        credits=credits
    )
    db.session.add(subj)
    db.session.commit()
    flash(f'Subject {code} - {name} added successfully!', 'success')
    return redirect(url_for('admin.academics'))

@admin_bp.route('/subjects/delete/<int:id>', methods=['POST'])
def delete_subject(id):
    """Delete a course subject."""
    subj = Subject.query.get_or_404(id)
    db.session.delete(subj)
    db.session.commit()
    flash(f'Subject {subj.code} removed.', 'info')
    return redirect(url_for('admin.academics'))

# -------------------------------------------------------------------------
# Attendance Audit & CSV Reports
# -------------------------------------------------------------------------
@admin_bp.route('/reports')
def reports():
    """Attendance audit logs with multidimensional filters."""
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    department_id = request.args.get('department_id', '')
    class_id = request.args.get('class_id', '')
    subject_id = request.args.get('subject_id', '')
    student_id = request.args.get('student_id', '')

    query = Attendance.query.join(Student).join(Subject)

    if from_date:
        try:
            d_from = datetime.strptime(from_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date >= d_from)
        except ValueError:
            pass

    if to_date:
        try:
            d_to = datetime.strptime(to_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date <= d_to)
        except ValueError:
            pass

    if department_id:
        query = query.filter(Student.department_id == int(department_id))

    if class_id:
        query = query.filter(Attendance.class_id == int(class_id))

    if subject_id:
        query = query.filter(Attendance.subject_id == int(subject_id))

    if student_id:
        query = query.filter(Attendance.student_id == int(student_id))

    records = query.order_by(Attendance.date.desc(), Student.roll_number).limit(500).all()

    departments = Department.query.order_by(Department.name).all()
    classes = ClassRoom.query.all()

    filters = {
        'from_date': from_date,
        'to_date': to_date,
        'department_id': department_id,
        'class_id': class_id,
        'subject_id': subject_id,
        'student_id': student_id
    }

    return render_template(
        'admin/reports.html',
        records=records,
        departments=departments,
        classes=classes,
        filters=filters,
        active_page='admin_reports'
    )

@admin_bp.route('/export-csv')
def export_csv():
    """Generate and download attendance CSV report."""
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    department_id = request.args.get('department_id', '')
    class_id = request.args.get('class_id', '')
    subject_id = request.args.get('subject_id', '')

    query = Attendance.query.join(Student).join(Subject)

    if from_date:
        try:
            d_from = datetime.strptime(from_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date >= d_from)
        except ValueError:
            pass

    if to_date:
        try:
            d_to = datetime.strptime(to_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date <= d_to)
        except ValueError:
            pass

    if department_id:
        query = query.filter(Student.department_id == int(department_id))

    if class_id:
        query = query.filter(Attendance.class_id == int(class_id))

    if subject_id:
        query = query.filter(Attendance.subject_id == int(subject_id))

    records = query.order_by(Attendance.date.desc(), Student.roll_number).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Date',
        'Roll Number',
        'Student Name',
        'Department',
        'Class',
        'Subject Code',
        'Subject Name',
        'Status',
        'Recorded By',
        'Remarks'
    ])

    for r in records:
        writer.writerow([
            r.date.strftime('%Y-%m-%d'),
            r.student.roll_number if r.student else '',
            r.student.name if r.student else '',
            r.student.department.code if (r.student and r.student.department) else '',
            r.classroom.display_name if r.classroom else '',
            r.subject.code if r.subject else '',
            r.subject.name if r.subject else '',
            r.status,
            r.recorded_by.name if r.recorded_by else 'Admin',
            r.remarks or ''
        ])

    csv_data = output.getvalue()
    filename = f"attendance_report_{date.today().strftime('%Y%m%d')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
