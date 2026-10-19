from functools import wraps
from flask import session, flash, redirect, url_for, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """Decorator to enforce role-based access control (admin, faculty, student)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            user_role = session.get('role')
            if user_role not in allowed_roles:
                flash('Access Denied: You do not have permission to view this page.', 'danger')
                return redirect(url_for('auth.dashboard_redirect'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Blueprint exports for convenient single-import in app.py
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.faculty import faculty_bp
from routes.student import student_bp
from routes.api import api_bp

__all__ = [
    'login_required',
    'role_required',
    'auth_bp',
    'admin_bp',
    'faculty_bp',
    'student_bp',
    'api_bp'
]
