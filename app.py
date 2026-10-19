import os
from datetime import datetime
from flask import Flask, jsonify, render_template, redirect, url_for
from config import config_dict
from models import db
from database import init_db
from routes import auth_bp, admin_bp, faculty_bp, student_bp, api_bp

def create_app(config_name=None):
    """Application Factory to configure and assemble all modules and blueprints."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_dict.get(config_name, config_dict['default']))

    # Initialize SQLAlchemy with this app
    db.init_app(app)

    # Register Blueprints connecting all system roles & APIs
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(faculty_bp, url_prefix='/faculty')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Cloud System Health Monitoring API
    @app.route('/health')
    def health_check():
        try:
            # Ping database connection
            db.session.execute(db.text('SELECT 1'))
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"

        return jsonify({
            'status': 'healthy' if db_status == 'connected' else 'degraded',
            'database': db_status,
            'college_name': app.config.get('COLLEGE_NAME'),
            'college_code': app.config.get('COLLEGE_CODE'),
            'cloud_provider': app.config.get('CLOUD_PROVIDER'),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })

    # Global Template Context Processor (injects branding into all templates)
    @app.context_processor
    def inject_global_branding():
        return {
            'college_name': app.config.get('COLLEGE_NAME', 'Apex Institute of Technology & Science'),
            'college_code': app.config.get('COLLEGE_CODE', 'AITS-EDU'),
            'app_title': app.config.get('APP_TITLE', 'Cloud-Based Student Attendance Management System'),
            'cloud_provider': app.config.get('CLOUD_PROVIDER', 'Local / Cloud Ready')
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('auth/login.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please contact the administrator.'
        }), 500

    # Initialize tables and seed demo dataset if empty
    init_db(app)

    return app

# Main entry point application instance
app = create_app()

if __name__ == '__main__':
    print("==================================================================")
    print("  Apex Institute of Technology - Cloud Attendance System")
    print("  Server running on http://127.0.0.1:5000")
    print("  Admin Login:   admin@college.edu       / Password: admin123")
    print("  Faculty Login: anurag.verma@college.edu / Password: faculty123")
    print("  Student Login: aarav.patel@college.edu  / Password: student123")
    print("==================================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
