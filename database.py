from datetime import date, timedelta
import random
from models import db, User, Department, ClassRoom, Faculty, Subject, Student, Attendance

def init_db(app):
    """Initializes the database tables within app context."""
    with app.app_context():
        db.create_all()
        # If database is fresh, populate with complete sample dataset
        if User.query.first() is None:
            print("[Database] Empty database detected. Seeding initial data...")
            seed_initial_data()
            print("[Database] Sample data seeded successfully!")

def seed_initial_data():
    """Populates initial departments, classes, users, faculty, students, subjects and attendance records."""
    # 1. Departments
    dept_cs = Department(code='CS', name='Computer Science & Engineering')
    dept_it = Department(code='IT', name='Information Technology')
    dept_ece = Department(code='ECE', name='Electronics & Communication Engineering')
    dept_me = Department(code='ME', name='Mechanical Engineering')

    db.session.add_all([dept_cs, dept_it, dept_ece, dept_me])
    db.session.flush()

    # 2. Classes
    class_cs_6a = ClassRoom(department_id=dept_cs.id, semester=6, division='A', academic_year='2025-2026')
    class_cs_6b = ClassRoom(department_id=dept_cs.id, semester=6, division='B', academic_year='2025-2026')
    class_it_6a = ClassRoom(department_id=dept_it.id, semester=6, division='A', academic_year='2025-2026')
    class_ece_4a = ClassRoom(department_id=dept_ece.id, semester=4, division='A', academic_year='2025-2026')

    db.session.add_all([class_cs_6a, class_cs_6b, class_it_6a, class_ece_4a])
    db.session.flush()

    # 3. Admin User
    admin_user = User(
        name='Dr. Rajesh Sharma (Administrator)',
        username='admin',
        email='admin@college.edu',
        role='admin'
    )
    admin_user.set_password('admin123')
    db.session.add(admin_user)
    db.session.flush()

    # 4. Faculty Users & Profiles
    fac1_user = User(
        name='Prof. Anurag Verma',
        username='prof.anurag',
        email='anurag.verma@college.edu',
        role='faculty'
    )
    fac1_user.set_password('faculty123')
    db.session.add(fac1_user)
    db.session.flush()

    fac1_profile = Faculty(
        user_id=fac1_user.id,
        faculty_id_code='FAC-CS-101',
        name='Prof. Anurag Verma',
        department_id=dept_cs.id,
        designation='Associate Professor & Cloud Lead',
        phone='+91 98765 43210'
    )
    db.session.add(fac1_profile)

    fac2_user = User(
        name='Dr. Neha Saxena',
        username='dr.neha',
        email='neha.saxena@college.edu',
        role='faculty'
    )
    fac2_user.set_password('faculty123')
    db.session.add(fac2_user)
    db.session.flush()

    fac2_profile = Faculty(
        user_id=fac2_user.id,
        faculty_id_code='FAC-CS-102',
        name='Dr. Neha Saxena',
        department_id=dept_cs.id,
        designation='Assistant Professor',
        phone='+91 98765 43211'
    )
    db.session.add(fac2_profile)

    fac3_user = User(
        name='Prof. Vikrant Joshi',
        username='prof.vikrant',
        email='vikrant.joshi@college.edu',
        role='faculty'
    )
    fac3_user.set_password('faculty123')
    db.session.add(fac3_user)
    db.session.flush()

    fac3_profile = Faculty(
        user_id=fac3_user.id,
        faculty_id_code='FAC-IT-201',
        name='Prof. Vikrant Joshi',
        department_id=dept_it.id,
        designation='Assistant Professor',
        phone='+91 98765 43212'
    )
    db.session.add(fac3_profile)
    db.session.flush()

    # 5. Subjects
    subj_cloud = Subject(
        code='CS601',
        name='Cloud Computing & Virtualization',
        department_id=dept_cs.id,
        semester=6,
        faculty_id=fac1_profile.id,
        credits=4
    )
    subj_dbms = Subject(
        code='CS602',
        name='Distributed Database Systems',
        department_id=dept_cs.id,
        semester=6,
        faculty_id=fac2_profile.id,
        credits=3
    )
    subj_se = Subject(
        code='CS603',
        name='Software Engineering & DevOps',
        department_id=dept_cs.id,
        semester=6,
        faculty_id=fac1_profile.id,
        credits=3
    )
    subj_web = Subject(
        code='IT601',
        name='Full Stack Web Development',
        department_id=dept_it.id,
        semester=6,
        faculty_id=fac3_profile.id,
        credits=4
    )
    db.session.add_all([subj_cloud, subj_dbms, subj_se, subj_web])
    db.session.flush()

    # 6. Students
    student_records = [
        # Roll, Name, Email, Username, Dept, Class, Semester, Phone, Target Attendance rate
        ('CS2026001', 'Aarav Patel', 'aarav.patel@college.edu', 'aarav01', dept_cs.id, class_cs_6a.id, 6, '+91 98234 11001', 0.90),
        ('CS2026002', 'Priya Sharma', 'priya.sharma@college.edu', 'priya02', dept_cs.id, class_cs_6a.id, 6, '+91 98234 11002', 0.95),
        ('CS2026003', 'Rohan Gupta', 'rohan.gupta@college.edu', 'rohan03', dept_cs.id, class_cs_6a.id, 6, '+91 98234 11003', 0.65), # Low attendance (<75%)
        ('CS2026004', 'Ananya Iyer', 'ananya.iyer@college.edu', 'ananya04', dept_cs.id, class_cs_6a.id, 6, '+91 98234 11004', 0.85),
        ('CS2026005', 'Kabir Mehra', 'kabir.mehra@college.edu', 'kabir05', dept_cs.id, class_cs_6a.id, 6, '+91 98234 11005', 0.70), # Low attendance (<75%)
        ('CS2026006', 'Sneha Kulkarni', 'sneha.k@college.edu', 'sneha06', dept_cs.id, class_cs_6a.id, 6, '+91 98234 11006', 0.88),
        ('CS2026007', 'Aditya Singh', 'aditya.s@college.edu', 'aditya07', dept_cs.id, class_cs_6a.id, 6, '+91 98234 11007', 0.92),
        ('CS2026008', 'Diya Kapoor', 'diya.k@college.edu', 'diya08', dept_cs.id, class_cs_6a.id, 6, '+91 98234 11008', 0.82),
        ('CS2026009', 'Vikram Malhotra', 'vikram.m@college.edu', 'vikram09', dept_cs.id, class_cs_6a.id, 6, '+91 98234 11009', 0.78),
        ('CS2026010', 'Ishaan Deshmukh', 'ishaan.d@college.edu', 'ishaan10', dept_cs.id, class_cs_6a.id, 6, '+91 98234 11010', 0.94),
        # Class CS 6B
        ('CS2026101', 'Meera Nair', 'meera.nair@college.edu', 'meera11', dept_cs.id, class_cs_6b.id, 6, '+91 98234 11011', 0.86),
        ('CS2026102', 'Siddharth Rao', 'siddharth.rao@college.edu', 'sid12', dept_cs.id, class_cs_6b.id, 6, '+91 98234 11012', 0.80),
        # Class IT 6A
        ('IT2026001', 'Tanvi Chawla', 'tanvi.c@college.edu', 'tanvi13', dept_it.id, class_it_6a.id, 6, '+91 98234 11013', 0.89),
        ('IT2026002', 'Devendra Roy', 'devendra.r@college.edu', 'dev14', dept_it.id, class_it_6a.id, 6, '+91 98234 11014', 0.72)
    ]

    created_students = []
    student_rates = {}

    for roll, name, email, uname, dept_id, cl_id, sem, phone, target_rate in student_records:
        user = User(
            name=name,
            username=uname,
            email=email,
            role='student'
        )
        user.set_password('student123')
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            roll_number=roll,
            name=name,
            department_id=dept_id,
            class_id=cl_id,
            semester=sem,
            phone=phone,
            guardian_phone='+91 98111 22334'
        )
        db.session.add(student)
        created_students.append(student)
        student_rates[roll] = target_rate

    db.session.flush()

    # 7. Seed Past Attendance records for CS 6A (CS601, CS602, CS603) over the past 14 days
    today = date.today()
    cs_6a_students = [s for s in created_students if s.class_id == class_cs_6a.id]
    subjects_to_seed = [
        (subj_cloud, fac1_profile.id),
        (subj_dbms, fac2_profile.id),
        (subj_se, fac1_profile.id)
    ]

    # Generate dates excluding Sundays
    dates_list = []
    for days_back in range(14, 0, -1):
        d = today - timedelta(days=days_back)
        if d.weekday() != 6:  # Skip Sunday
            dates_list.append(d)

    for att_date in dates_list:
        for subj, faculty_id in subjects_to_seed:
            for student in cs_6a_students:
                rate = student_rates.get(student.roll_number, 0.85)
                # Determine status based on student's target attendance rate
                rand_val = random.random()
                if rand_val < rate:
                    status = 'Present'
                elif rand_val < (rate + 0.05):
                    status = 'Late'
                else:
                    status = 'Absent'

                att = Attendance(
                    student_id=student.id,
                    subject_id=subj.id,
                    class_id=class_cs_6a.id,
                    date=att_date,
                    status=status,
                    marked_by_faculty_id=faculty_id,
                    remarks='Regular Lecture' if status == 'Present' else ('Traffic delay' if status == 'Late' else 'Uninformed absence')
                )
                db.session.add(att)

    db.session.commit()
    print("[Database] Successfully committed seed records to database.")
