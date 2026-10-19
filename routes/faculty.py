from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Department, ClassRoom, Faculty, Subject, Student, Attendance
from routes import login_required, role_required

faculty_bp = Blueprint('faculty', __name__)

@faculty_bp.before_request
@login_required
@role_required(['faculty', 'admin'])
def restrict_to_faculty():
    """Ensure all routes in faculty_bp require faculty or admin role."""
    pass

def get_current_faculty():
    """Helper to retrieve the Faculty model for current session user."""
    user_id = session.get('user_id')
    fac = Faculty.query.filter_by(user_id=user_id).first()
    if not fac and session.get('role') == 'admin':
        # Admin testing faculty routes: fallback to first faculty
        fac = Faculty.query.first()
    return fac

@faculty_bp.route('/dashboard')
def dashboard():
    """Faculty Dashboard Overview with assigned courses and session stats."""
    fac = get_current_faculty()
    if not fac:
        flash('Faculty profile not found for this user account.', 'warning')
        return redirect(url_for('auth.login'))

    assigned_subjects = Subject.query.filter_by(faculty_id=fac.id).all()
    today = date.today()

    total_marked_by_faculty = Attendance.query.filter_by(marked_by_faculty_id=fac.id).count()
    
    # Sessions conducted today by this faculty
    today_sessions_count = db.session.query(
        Attendance.subject_id, Attendance.class_id
    ).filter(
        Attendance.marked_by_faculty_id == fac.id,
        Attendance.date == today
    ).distinct().count()

    return render_template(
        'faculty/dashboard.html',
        faculty=fac,
        assigned_subjects=assigned_subjects,
        today=today,
        total_marked_by_faculty=total_marked_by_faculty,
        today_sessions_count=today_sessions_count,
        active_page='faculty_dashboard'
    )

@faculty_bp.route('/mark-attendance', methods=['GET'])
def mark_attendance():
    """Daily Attendance Register interface for faculty marking."""
    fac = get_current_faculty()
    assigned_subjects = Subject.query.filter_by(faculty_id=fac.id).all() if fac else []
    if not assigned_subjects:
        assigned_subjects = Subject.query.all()

    departments = Department.query.order_by(Department.name).all()
    classes = ClassRoom.query.all()

    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    selected_subject_id = request.args.get('subject_id', type=int)

    if not selected_subject_id and assigned_subjects:
        selected_subject_id = assigned_subjects[0].id

    selected_subject = Subject.query.get(selected_subject_id) if selected_subject_id else None

    # Determine default department
    selected_dept_id = request.args.get('department_id', type=int)
    if not selected_dept_id and selected_subject:
        selected_dept_id = selected_subject.department_id
    elif not selected_dept_id and departments:
        selected_dept_id = departments[0].id

    # Determine default class
    selected_class_id = request.args.get('class_id', type=int)
    if not selected_class_id and selected_subject:
        matching_class = ClassRoom.query.filter_by(
            department_id=selected_subject.department_id,
            semester=selected_subject.semester
        ).first()
        selected_class_id = matching_class.id if matching_class else (classes[0].id if classes else None)
    elif not selected_class_id and classes:
        selected_class_id = classes[0].id

    # Load students in selected class
    students = []
    if selected_class_id:
        students = Student.query.filter_by(class_id=selected_class_id).order_by(Student.roll_number).all()

    # Check for existing attendance records on this date
    existing_attendance = {}
    existing_remarks = {}
    is_existing_record = False

    try:
        sel_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
        if selected_subject_id and selected_class_id:
            existing_records = Attendance.query.filter_by(
                subject_id=selected_subject_id,
                class_id=selected_class_id,
                date=sel_date_obj
            ).all()

            if existing_records:
                is_existing_record = True
                for r in existing_records:
                    existing_attendance[r.student_id] = r.status
                    existing_remarks[r.student_id] = r.remarks or ''
    except ValueError:
        pass

    return render_template(
        'faculty/mark_attendance.html',
        departments=departments,
        classes=classes,
        subjects=assigned_subjects,
        students=students,
        selected_dept_id=selected_dept_id,
        selected_class_id=selected_class_id,
        selected_subject_id=selected_subject_id,
        selected_date=selected_date,
        existing_attendance=existing_attendance,
        existing_remarks=existing_remarks,
        is_existing_record=is_existing_record,
        active_page='faculty_mark'
    )

@faculty_bp.route('/save-attendance', methods=['POST'])
def save_attendance():
    """Process and save or update attendance records."""
    fac = get_current_faculty()
    class_id = request.form.get('class_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    date_str = request.form.get('date', '').strip()

    if not class_id or not subject_id or not date_str:
        flash('Invalid submission: class, subject, and date must be specified.', 'danger')
        return redirect(url_for('faculty.mark_attendance'))

    try:
        att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format provided.', 'danger')
        return redirect(url_for('faculty.mark_attendance'))

    students = Student.query.filter_by(class_id=class_id).all()
    faculty_id = fac.id if fac else None

    saved_count = 0
    updated_count = 0

    for s in students:
        status = request.form.get(f'status_{s.id}', 'Present')
        remarks = request.form.get(f'remarks_{s.id}', '').strip()

        # Check existing
        rec = Attendance.query.filter_by(
            student_id=s.id,
            subject_id=subject_id,
            date=att_date
        ).first()

        if rec:
            rec.status = status
            rec.remarks = remarks
            rec.class_id = class_id
            rec.marked_by_faculty_id = faculty_id
            updated_count += 1
        else:
            new_rec = Attendance(
                student_id=s.id,
                subject_id=subject_id,
                class_id=class_id,
                date=att_date,
                status=status,
                marked_by_faculty_id=faculty_id,
                remarks=remarks
            )
            db.session.add(new_rec)
            saved_count += 1

    db.session.commit()

    if updated_count > 0:
        flash(f'Attendance records for {len(students)} students updated successfully on {att_date}!', 'success')
    else:
        flash(f'Attendance recorded for {saved_count} students on {att_date}!', 'success')

    return redirect(url_for('faculty.view_attendance', subject_id=subject_id, class_id=class_id, date=date_str))

@faculty_bp.route('/view-attendance')
def view_attendance():
    """View and filter historical attendance logs recorded by faculty."""
    fac = get_current_faculty()
    assigned_subjects = Subject.query.filter_by(faculty_id=fac.id).all() if fac else []
    if not assigned_subjects:
        assigned_subjects = Subject.query.all()

    classes = ClassRoom.query.all()

    date_param = request.args.get('date', '')
    subject_id_param = request.args.get('subject_id', '')
    class_id_param = request.args.get('class_id', '')

    query = Attendance.query.join(Student).join(Subject)

    if fac:
        query = query.filter(
            (Attendance.marked_by_faculty_id == fac.id) |
            (Attendance.subject_id.in_([s.id for s in assigned_subjects]))
        )

    if date_param:
        try:
            d_val = datetime.strptime(date_param, '%Y-%m-%d').date()
            query = query.filter(Attendance.date == d_val)
        except ValueError:
            pass

    if subject_id_param:
        query = query.filter(Attendance.subject_id == int(subject_id_param))

    if class_id_param:
        query = query.filter(Attendance.class_id == int(class_id_param))

    records = query.order_by(Attendance.date.desc(), Student.roll_number).limit(300).all()

    filters = {
        'date': date_param,
        'subject_id': subject_id_param,
        'class_id': class_id_param
    }

    return render_template(
        'faculty/view_attendance.html',
        records=records,
        assigned_subjects=assigned_subjects,
        classes=classes,
        filters=filters,
        active_page='faculty_view'
    )

@faculty_bp.route('/reports')
def reports():
    """Per-course attendance analytics and percentage breakdown."""
    fac = get_current_faculty()
    assigned_subjects = Subject.query.filter_by(faculty_id=fac.id).all() if fac else []
    if not assigned_subjects:
        assigned_subjects = Subject.query.all()

    subject_id = request.args.get('subject_id', type=int)
    if not subject_id and assigned_subjects:
        subject_id = assigned_subjects[0].id

    selected_subject = Subject.query.get(subject_id) if subject_id else None
    period = request.args.get('period', 'all')

    today = date.today()
    min_date = None
    if period == 'week':
        min_date = today - timedelta(days=7)
    elif period == 'month':
        min_date = today - timedelta(days=30)

    student_stats = []

    if selected_subject:
        # Find students in the department and semester of this subject
        students_query = Student.query.filter_by(
            department_id=selected_subject.department_id,
            semester=selected_subject.semester
        ).order_by(Student.roll_number).all()

        if not students_query:
            students_query = Student.query.order_by(Student.roll_number).all()

        for s in students_query:
            q = Attendance.query.filter(
                Attendance.student_id == s.id,
                Attendance.subject_id == selected_subject.id
            )
            if min_date:
                q = q.filter(Attendance.date >= min_date)

            records = q.all()
            total_classes = len(records)
            attended = sum(1 for r in records if r.status in ('Present', 'Late'))
            absent = sum(1 for r in records if r.status == 'Absent')
            pct = round((attended / total_classes * 100), 1) if total_classes > 0 else 0.0

            if total_classes > 0 or period == 'all':
                student_stats.append({
                    'student': s,
                    'total_classes': total_classes,
                    'attended': attended,
                    'absent': absent,
                    'percentage': pct
                })

    return render_template(
        'faculty/reports.html',
        assigned_subjects=assigned_subjects,
        selected_subject=selected_subject,
        period=period,
        student_stats=student_stats,
        active_page='faculty_reports'
    )
