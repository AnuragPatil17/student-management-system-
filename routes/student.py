from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Department, ClassRoom, Faculty, Subject, Student, Attendance
from routes import login_required, role_required

student_bp = Blueprint('student', __name__)

@student_bp.before_request
@login_required
@role_required(['student', 'admin'])
def restrict_to_student():
    """Ensure all routes in student_bp require student or admin role."""
    pass

def get_current_student():
    """Helper to retrieve the Student model for current session user."""
    user_id = session.get('user_id')
    stud = Student.query.filter_by(user_id=user_id).first()
    if not stud and session.get('role') == 'admin':
        # Admin inspecting student dashboard
        stud = Student.query.first()
    return stud

@student_bp.route('/dashboard')
def dashboard():
    """Student Attendance Dashboard Overview."""
    stud = get_current_student()
    if not stud:
        flash('Student profile not found for this account.', 'warning')
        return redirect(url_for('auth.login'))

    all_records = Attendance.query.filter_by(student_id=stud.id).all()

    total_lectures = len(all_records)
    attended_lectures = sum(1 for r in all_records if r.status == 'Present')
    late_lectures = sum(1 for r in all_records if r.status == 'Late')
    absent_lectures = sum(1 for r in all_records if r.status == 'Absent')
    
    # Calculate percentage (Present counts full, Late counts as attended)
    overall_rate = round(((attended_lectures + late_lectures) / total_lectures * 100), 1) if total_lectures > 0 else 100.0

    # Subject-wise analytics
    semester_subjects = Subject.query.filter_by(
        department_id=stud.department_id,
        semester=stud.semester
    ).all()

    if not semester_subjects:
        # Fallback to any subjects with records
        distinct_subj_ids = list(set([r.subject_id for r in all_records]))
        semester_subjects = Subject.query.filter(Subject.id.in_(distinct_subj_ids)).all()

    subject_breakdown = []
    for subj in semester_subjects:
        s_recs = [r for r in all_records if r.subject_id == subj.id]
        s_total = len(s_recs)
        s_pres = sum(1 for r in s_recs if r.status == 'Present')
        s_late = sum(1 for r in s_recs if r.status == 'Late')
        s_abs = sum(1 for r in s_recs if r.status == 'Absent')
        s_rate = round(((s_pres + s_late) / s_total * 100), 1) if s_total > 0 else 100.0

        subject_breakdown.append({
            'subject': subj,
            'total': s_total,
            'present': s_pres,
            'late': s_late,
            'absent': s_abs,
            'rate': s_rate
        })

    # Recent 10 attendance records
    recent_logs = Attendance.query.filter_by(student_id=stud.id).order_by(Attendance.date.desc()).limit(10).all()

    return render_template(
        'student/dashboard.html',
        student=stud,
        overall_rate=overall_rate,
        total_lectures=total_lectures,
        attended_lectures=attended_lectures,
        late_lectures=late_lectures,
        absent_lectures=absent_lectures,
        subject_breakdown=subject_breakdown,
        recent_logs=recent_logs,
        active_page='student_dashboard'
    )

@student_bp.route('/history')
def history():
    """Detailed filterable attendance history for the student."""
    stud = get_current_student()
    if not stud:
        flash('Student profile not found.', 'warning')
        return redirect(url_for('auth.login'))

    subject_id = request.args.get('subject_id', '')
    status_filter = request.args.get('status', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')

    query = Attendance.query.filter_by(student_id=stud.id).join(Subject)

    if subject_id:
        query = query.filter(Attendance.subject_id == int(subject_id))

    if status_filter:
        query = query.filter(Attendance.status == status_filter)

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

    records = query.order_by(Attendance.date.desc()).all()

    subjects = Subject.query.filter_by(
        department_id=stud.department_id,
        semester=stud.semester
    ).all()

    filters = {
        'subject_id': subject_id,
        'status': status_filter,
        'from_date': from_date,
        'to_date': to_date
    }

    return render_template(
        'student/history.html',
        student=stud,
        records=records,
        subjects=subjects,
        filters=filters,
        active_page='student_history'
    )
