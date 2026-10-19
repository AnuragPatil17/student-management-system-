from datetime import datetime, date
from flask import Blueprint, jsonify, request, session
from models import db, Attendance, Department, Student, Subject, Faculty
from routes import login_required

api_bp = Blueprint('api', __name__)

@api_bp.route('/admin/chart-data')
@login_required
def admin_chart_data():
    """Returns aggregated data for Admin Dashboard Charts."""
    # 1. 7-Day Attendance Trend
    distinct_dates = db.session.query(Attendance.date).distinct().order_by(Attendance.date.desc()).limit(7).all()
    trend_dates = sorted([d[0] for d in distinct_dates])

    trend_labels = []
    present_counts = []
    absent_counts = []

    for d in trend_dates:
        trend_labels.append(d.strftime('%b %d'))
        pres = Attendance.query.filter_by(date=d, status='Present').count()
        absn = Attendance.query.filter_by(date=d, status='Absent').count()
        present_counts.append(pres)
        absent_counts.append(absn)

    # 2. Department-wise Average Attendance
    departments = Department.query.order_by(Department.code).all()
    dept_names = []
    dept_rates = []

    for dept in departments:
        total = Attendance.query.join(Student).filter(Student.department_id == dept.id).count()
        if total > 0:
            attended = Attendance.query.join(Student).filter(
                Student.department_id == dept.id,
                Attendance.status.in_(['Present', 'Late'])
            ).count()
            rate = round((attended / total * 100), 1)
        else:
            rate = 0.0

        dept_names.append(dept.code)
        dept_rates.append(rate)

    # 3. Overall Status Ratio
    present_total = Attendance.query.filter_by(status='Present').count()
    absent_total = Attendance.query.filter_by(status='Absent').count()
    late_total = Attendance.query.filter_by(status='Late').count()

    return jsonify({
        'trend': {
            'dates': trend_labels,
            'present': present_counts,
            'absent': absent_counts
        },
        'departments': {
            'names': dept_names,
            'rates': dept_rates
        },
        'status_ratio': {
            'present': present_total,
            'absent': absent_total,
            'late': late_total
        }
    })

@api_bp.route('/faculty/check-duplicate')
@login_required
def faculty_check_duplicate():
    """Checks whether attendance has already been recorded for a subject, class, and date."""
    subject_id = request.args.get('subject_id', type=int)
    date_str = request.args.get('date', '').strip()
    class_id = request.args.get('class_id', type=int)

    if not subject_id or not date_str:
        return jsonify({'exists': False, 'count': 0})

    try:
        att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'exists': False, 'count': 0})

    query = Attendance.query.filter_by(subject_id=subject_id, date=att_date)
    if class_id:
        query = query.filter_by(class_id=class_id)

    count = query.count()
    return jsonify({
        'exists': count > 0,
        'count': count
    })

@api_bp.route('/student/chart-data')
@login_required
def student_chart_data():
    """Provides personalized attendance statistics for the Student Dashboard."""
    user_id = session.get('user_id')
    student = Student.query.filter_by(user_id=user_id).first()

    if not student and session.get('role') == 'admin':
        student = Student.query.first()

    if not student:
        return jsonify({'error': 'Student not found'}), 404

    records = Attendance.query.filter_by(student_id=student.id).all()
    total = len(records)
    attended = sum(1 for r in records if r.status == 'Present')
    late = sum(1 for r in records if r.status == 'Late')
    absent = sum(1 for r in records if r.status == 'Absent')

    overall_pct = round(((attended + late) / total * 100), 1) if total > 0 else 100.0

    # Subject Breakdown
    subjects = Subject.query.filter_by(
        department_id=student.department_id,
        semester=student.semester
    ).all()

    if not subjects:
        distinct_subj_ids = list(set([r.subject_id for r in records]))
        subjects = Subject.query.filter(Subject.id.in_(distinct_subj_ids)).all()

    subj_names = []
    subj_percentages = []

    for s in subjects:
        s_recs = [r for r in records if r.subject_id == s.id]
        if s_recs:
            s_attended = sum(1 for r in s_recs if r.status in ('Present', 'Late'))
            s_pct = round((s_attended / len(s_recs) * 100), 1)
        else:
            s_pct = 100.0

        subj_names.append(s.code)
        subj_percentages.append(s_pct)

    return jsonify({
        'overall': {
            'percentage': overall_pct,
            'attended': attended,
            'absent': absent,
            'late': late
        },
        'subjects': {
            'names': subj_names,
            'percentages': subj_percentages
        }
    })
