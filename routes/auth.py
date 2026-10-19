from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Student, Faculty
from routes import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Root redirect to appropriate dashboard or login page."""
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard_redirect'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard')
@login_required
def dashboard_redirect():
    """Directs logged in users to their respective role dashboard."""
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif role == 'faculty':
        return redirect(url_for('faculty.dashboard'))
    elif role == 'student':
        return redirect(url_for('student.dashboard'))
    flash('Unrecognized user role.', 'danger')
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """College Login Page handling Admin, Faculty, and Student authentication."""
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard_redirect'))

    if request.method == 'POST':
        login_id = request.form.get('login_id', '').strip()
        password = request.form.get('password', '').strip()
        selected_role = request.form.get('role', '').strip().lower()

        # Validation
        if not login_id:
            flash('Please enter your email or username.', 'danger')
            return render_template('auth/login.html', login_id=login_id, selected_role=selected_role)
        if not password:
            flash('Please enter your password.', 'danger')
            return render_template('auth/login.html', login_id=login_id, selected_role=selected_role)
        if selected_role not in ['admin', 'faculty', 'student']:
            flash('Please select a valid role (Admin, Faculty, or Student).', 'danger')
            return render_template('auth/login.html', login_id=login_id, selected_role=selected_role)

        # Lookup by email or username
        user = User.query.filter(
            (User.email.ilike(login_id)) | (User.username.ilike(login_id))
        ).first()

        if not user or not user.check_password(password):
            flash('Invalid credentials. Please verify your email/username and password.', 'danger')
            return render_template('auth/login.html', login_id=login_id, selected_role=selected_role)

        if not user.is_active:
            flash('This account is currently deactivated. Please contact the administrator.', 'warning')
            return render_template('auth/login.html', login_id=login_id, selected_role=selected_role)

        # Verify role selection matches account role
        if user.role != selected_role:
            flash(f"Account exists, but it is registered as '{user.role.title()}', not '{selected_role.title()}'. Please choose the correct role.", 'warning')
            return render_template('auth/login.html', login_id=login_id, selected_role=selected_role)

        # Create session
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['name'] = user.name
        session['email'] = user.email
        session['role'] = user.role

        # If student or faculty, cache their entity ID in session for fast lookup
        if user.role == 'student' and user.student_profile:
            session['student_id'] = user.student_profile.id
            session['roll_number'] = user.student_profile.roll_number
        elif user.role == 'faculty' and user.faculty_profile:
            session['faculty_id'] = user.faculty_profile.id
            session['faculty_code'] = user.faculty_profile.faculty_id_code

        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('auth.dashboard_redirect'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Clears user session and logs out."""
    user_name = session.get('name', 'User')
    session.clear()
    flash(f'You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Handles demo password reset request."""
    email = request.form.get('reset_email', '').strip()
    if not email:
        flash('Please provide your registered college email address.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter(User.email.ilike(email)).first()
    if user:
        flash(f'Password reset instructions have been sent to {email}. (Demo Note: Default password is "{user.role}123")', 'info')
    else:
        # Prevent user enumeration attack in production, but confirm email submitted
        flash(f'If an account with {email} exists, password reset instructions have been sent.', 'info')

    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Allows authenticated user to change their password."""
    current_pwd = request.form.get('current_password', '')
    new_pwd = request.form.get('new_password', '')
    confirm_pwd = request.form.get('confirm_password', '')

    user = User.query.get(session['user_id'])
    if not user.check_password(current_pwd):
        flash('Current password incorrect.', 'danger')
        return redirect(url_for('auth.dashboard_redirect'))

    if len(new_pwd) < 6:
        flash('New password must be at least 6 characters.', 'warning')
        return redirect(url_for('auth.dashboard_redirect'))

    if new_pwd != confirm_pwd:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('auth.dashboard_redirect'))

    user.set_password(new_pwd)
    db.session.commit()
    flash('Password updated successfully!', 'success')
    return redirect(url_for('auth.dashboard_redirect'))
