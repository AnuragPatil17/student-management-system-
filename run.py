#!/usr/bin/env python
import os
import sys

# Ensure current directory is on pythonpath
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1')
    print("==================================================================")
    print("  Apex Institute of Technology - Cloud Attendance System")
    print(f"  Server starting on http://127.0.0.1:{port}")
    print("  Admin Login:   admin@college.edu       / Password: admin123")
    print("  Faculty Login: anurag.verma@college.edu / Password: faculty123")
    print("  Student Login: aarav.patel@college.edu  / Password: student123")
    print("==================================================================")
    app.run(host='0.0.0.0', port=port, debug=debug)
