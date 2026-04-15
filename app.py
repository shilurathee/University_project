from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_db_connection



app = Flask(__name__)
app.secret_key = "your_secret_key_here"


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            selected_role = request.form.get('role')
            if selected_role and selected_role != user['role']:
                flash("Invalid role selected for this account")
                return render_template('login.html')

            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user['role'] == 'student':
                return redirect(url_for('student_dashboard'))
        else:
            flash("Invalid username or password")

    return render_template('login.html')
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as count FROM student")
    total_students = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM teacher")
    total_teachers = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM course")
    total_courses = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM registration")
    total_registrations = cursor.fetchone()['count']

    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html',
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_courses=total_courses,
                         total_registrations=total_registrations)

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    return render_template('teacher_dashboard.html')


@app.route('/student/dashboard')
def student_dashboard():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    return render_template('student_dashboard.html')

'''student management routes'''
@app.route('/admin/students')
def view_students():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM student ORDER BY student_id")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('students.html', students=students)


@app.route('/admin/add_student', methods=['GET', 'POST'])
def add_student():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        usn = request.form['usn']
        student_name = request.form['student_name']
        email = request.form['email']
        department = request.form['department']
        semester = request.form['semester']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO student (usn, student_name, email, department, semester)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (usn, student_name, email, department, semester)
            )
            conn.commit()
            flash("Student added successfully")
            return redirect(url_for('view_students'))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

    return render_template('add_student.html')


@app.route('/admin/delete_student/<int:student_id>')
def delete_student(student_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM student WHERE student_id = %s", (student_id,))
        conn.commit()
        flash("Student deleted successfully")
    except Exception as e:
        conn.rollback()
        flash(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_students'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


'''teacher management routes'''
@app.route('/admin/teachers')
def view_teachers():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teacher ORDER BY teacher_id")
    teachers = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('teachers.html', teachers=teachers)


@app.route('/admin/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        teacher_name = request.form['teacher_name']
        email = request.form['email']
        department = request.form['department']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO teacher (teacher_name, email, department)
                VALUES (%s, %s, %s)
                """,
                (teacher_name, email, department)
            )
            conn.commit()
            flash("Teacher added successfully")
            return redirect(url_for('view_teachers'))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

    return render_template('add_teacher.html')


@app.route('/admin/delete_teacher/<int:teacher_id>')
def delete_teacher(teacher_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM teacher WHERE teacher_id = %s", (teacher_id,))
        conn.commit()
        flash("Teacher deleted successfully")
    except Exception as e:
        conn.rollback()
        flash(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_teachers'))

'''course management routes'''
@app.route('/admin/courses')
def view_courses():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.course_id, c.course_code, c.course_name, c.credits, c.department,
               t.teacher_name
        FROM course c
        LEFT JOIN teacher t ON c.teacher_id = t.teacher_id
        ORDER BY c.course_id
    """)
    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('courses.html', courses=courses)


@app.route('/admin/add_course', methods=['GET', 'POST'])
def add_course():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        course_code = request.form['course_code']
        course_name = request.form['course_name']
        credits = request.form['credits']
        department = request.form['department']
        teacher_id = request.form.get('teacher_id')

        if teacher_id == "":
            teacher_id = None

        try:
            cursor.execute(
                """
                INSERT INTO course (course_code, course_name, credits, department, teacher_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (course_code, course_name, credits, department, teacher_id)
            )
            conn.commit()
            flash("Course added successfully")
            return redirect(url_for('view_courses'))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}")

    cursor.execute("SELECT teacher_id, teacher_name FROM teacher ORDER BY teacher_name")
    teachers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('add_course.html', teachers=teachers)

@app.route('/admin/edit_course/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        course_code = request.form['course_code']
        course_name = request.form['course_name']
        credits = request.form['credits']
        department = request.form['department']
        teacher_id = request.form.get('teacher_id') or None

        try:
            cursor.execute("""
                UPDATE course 
                SET course_code=%s, course_name=%s, credits=%s, 
                    department=%s, teacher_id=%s
                WHERE course_id=%s
            """, (course_code, course_name, credits, department, teacher_id, course_id))
            conn.commit()
            flash("Course updated successfully")
            return redirect(url_for('view_courses'))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

    else:
        cursor.execute("SELECT * FROM course WHERE course_id=%s", (course_id,))
        course = cursor.fetchone()
        cursor.execute("SELECT teacher_id, teacher_name FROM teacher ORDER BY teacher_name")
        teachers = cursor.fetchall()
        cursor.close()
        conn.close()
        if not course:
            flash("Course not found")
            return redirect(url_for('view_courses'))
        return render_template('edit_course.html', course=course, teachers=teachers)

@app.route('/admin/delete_course/<int:course_id>')
def delete_course(course_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM course WHERE course_id = %s", (course_id,))
        conn.commit()
        flash("Course deleted successfully")
    except Exception as e:
        conn.rollback()
        flash(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_courses'))

@app.route('/admin/registrations')
def view_registrations():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.registration_id,
               s.student_name,
               s.usn,
               c.course_name,
               c.course_code,
               r.semester,
               r.academic_year,
               r.registration_date
        FROM registration r
        JOIN student s ON r.student_id = s.student_id
        JOIN course c ON r.course_id = c.course_id
        ORDER BY r.registration_id
    """)
    registrations = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('registrations.html', registrations=registrations)


@app.route('/admin/add_registration', methods=['GET', 'POST'])
def add_registration():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        semester = request.form['semester']
        academic_year = request.form['academic_year']
        registration_date = request.form['registration_date']

        try:
            cursor.execute(
                """
                INSERT INTO registration (student_id, course_id, semester, academic_year, registration_date)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (student_id, course_id, semester, academic_year, registration_date)
            )
            conn.commit()
            flash("Registration added successfully")
            return redirect(url_for('view_registrations'))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}")

    cursor.execute("SELECT student_id, student_name, usn FROM student ORDER BY student_name")
    students = cursor.fetchall()

    cursor.execute("SELECT course_id, course_name, course_code FROM course ORDER BY course_name")
    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('add_registration.html', students=students, courses=courses)

'''admin registration management routes'''
@app.route('/admin/delete_registration/<int:registration_id>')
def delete_registration(registration_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM registration WHERE registration_id = %s", (registration_id,))
        conn.commit()
        flash("Registration deleted successfully")
    except Exception as e:
        conn.rollback()
        flash(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_registrations'))

'''teachers '''

@app.route('/admin/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        usn = request.form['usn']
        student_name = request.form['student_name']
        email = request.form['email']
        department = request.form['department']
        semester = request.form['semester']

        try:
            cursor.execute("""
                UPDATE student 
                SET usn=%s, student_name=%s, email=%s, department=%s, semester=%s
                WHERE student_id=%s
            """, (usn, student_name, email, department, semester, student_id))
            conn.commit()
            flash("Student updated successfully")
            return redirect(url_for('view_students'))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

    else:
        cursor.execute("SELECT * FROM student WHERE student_id=%s", (student_id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        if not student:
            flash("Student not found")
            return redirect(url_for('view_students'))
        return render_template('edit_student.html', student=student)


@app.route('/admin/edit_teacher/<int:teacher_id>', methods=['GET', 'POST'])
def edit_teacher(teacher_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        teacher_name = request.form['teacher_name']
        email = request.form['email']
        department = request.form['department']

        try:
            cursor.execute("""
                UPDATE teacher 
                SET teacher_name=%s, email=%s, department=%s
                WHERE teacher_id=%s
            """, (teacher_name, email, department, teacher_id))
            conn.commit()
            flash("Teacher updated successfully")
            return redirect(url_for('view_teachers'))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

    else:
        cursor.execute("SELECT * FROM teacher WHERE teacher_id=%s", (teacher_id,))
        teacher = cursor.fetchone()
        cursor.close()
        conn.close()
        if not teacher:
            flash("Teacher not found")
            return redirect(url_for('view_teachers'))
        return render_template('edit_teacher.html', teacher=teacher)


@app.route('/teacher/courses')
def teacher_courses():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.course_id, c.course_code, c.course_name, c.credits, c.department
        FROM course c
        JOIN teacher t ON c.teacher_id = t.teacher_id
        WHERE t.user_id = %s
        ORDER BY c.course_id
    """, (user_id,))
    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('teacher_courses.html', courses=courses)


@app.route('/teacher/assessments')
def teacher_assessments_page():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.course_id, c.course_code, c.course_name, c.credits, c.department
        FROM course c
        JOIN teacher t ON c.teacher_id = t.teacher_id
        WHERE t.user_id = %s
        ORDER BY c.course_id
    """, (user_id,))
    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('teacher_assessments_page.html', courses=courses)


@app.route('/teacher/marks')
def teacher_marks_page():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.course_id, c.course_code, c.course_name, c.credits, c.department
        FROM course c
        JOIN teacher t ON c.teacher_id = t.teacher_id
        WHERE t.user_id = %s
        ORDER BY c.course_id
    """, (user_id,))
    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('teacher_marks_page.html', courses=courses)


@app.route('/teacher/results')
def teacher_results_page():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.course_id, c.course_code, c.course_name, c.credits, c.department
        FROM course c
        JOIN teacher t ON c.teacher_id = t.teacher_id
        WHERE t.user_id = %s
        ORDER BY c.course_id
    """, (user_id,))
    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('teacher_results_page.html', courses=courses)


'''teacher task'''
@app.route('/teacher/course/<int:course_id>/assessments')
def teacher_assessments(course_id):
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.course_id, c.course_name, c.course_code
        FROM course c
        JOIN teacher t ON c.teacher_id = t.teacher_id
        WHERE c.course_id = %s AND t.user_id = %s
    """, (course_id, user_id))
    course = cursor.fetchone()

    if not course:
        cursor.close()
        conn.close()
        flash("You are not allowed to access this course")
        return redirect(url_for('teacher_courses'))

    cursor.execute("""
        SELECT assessment_id, assessment_name, assessment_type, max_marks, weightage, created_at
        FROM assessment
        WHERE course_id = %s
        ORDER BY assessment_id
    """, (course_id,))
    assessments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('teacher_assessments.html', course=course, assessments=assessments)


@app.route('/teacher/course/<int:course_id>/add_assessment', methods=['GET', 'POST'])
def add_assessment(course_id):
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.course_id, c.course_name, c.course_code
        FROM course c
        JOIN teacher t ON c.teacher_id = t.teacher_id
        WHERE c.course_id = %s AND t.user_id = %s
    """, (course_id, user_id))
    course = cursor.fetchone()

    if not course:
        cursor.close()
        conn.close()
        flash("You are not allowed to add assessments for this course")
        return redirect(url_for('teacher_courses'))

    if request.method == 'POST':
        assessment_name = request.form['assessment_name']
        assessment_type = request.form['assessment_type']
        max_marks = request.form['max_marks']
        weightage = request.form['weightage']

        try:
            cursor.execute("""
                INSERT INTO assessment (course_id, assessment_name, assessment_type, max_marks, weightage)
                VALUES (%s, %s, %s, %s, %s)
            """, (course_id, assessment_name, assessment_type, max_marks, weightage))
            conn.commit()
            flash("Assessment added successfully")
            return redirect(url_for('teacher_assessments', course_id=course_id))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}")

    cursor.close()
    conn.close()

    return render_template('add_assessment.html', course=course)


@app.route('/teacher/course/<int:course_id>/delete_assessment/<int:assessment_id>')
def delete_assessment(course_id, assessment_id):
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.course_id
        FROM course c
        JOIN teacher t ON c.teacher_id = t.teacher_id
        WHERE c.course_id = %s AND t.user_id = %s
    """, (course_id, user_id))
    course = cursor.fetchone()

    if not course:
        cursor.close()
        conn.close()
        flash("You are not allowed to delete assessments from this course")
        return redirect(url_for('teacher_courses'))

    try:
        cursor.execute("""
            DELETE FROM assessment
            WHERE assessment_id = %s AND course_id = %s
        """, (assessment_id, course_id))
        conn.commit()
        flash("Assessment deleted successfully")
    except Exception as e:
        conn.rollback()
        flash(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('teacher_assessments', course_id=course_id))


@app.route('/teacher/course/<int:course_id>/marks')
def teacher_marks(course_id):
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.course_id, c.course_name, c.course_code
        FROM course c
        JOIN teacher t ON c.teacher_id = t.teacher_id
        WHERE c.course_id = %s AND t.user_id = %s
    """, (course_id, user_id))
    course = cursor.fetchone()

    if not course:
        cursor.close()
        conn.close()
        flash("You are not allowed to access this course")
        return redirect(url_for('teacher_courses'))

    cursor.execute("""
        SELECT assessment_id, assessment_name, assessment_type
        FROM assessment
        WHERE course_id = %s
        ORDER BY assessment_id
    """, (course_id,))
    assessments = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('teacher_marks.html', course=course, assessments=assessments)


@app.route('/teacher/course/<int:course_id>/assessment/<int:assessment_id>/enter_marks', methods=['GET', 'POST'])
def enter_marks(course_id, assessment_id):
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.course_id, c.course_name, c.course_code
        FROM course c
        JOIN teacher t ON c.teacher_id = t.teacher_id
        WHERE c.course_id = %s AND t.user_id = %s
    """, (course_id, user_id))
    course = cursor.fetchone()

    if not course:
        cursor.close()
        conn.close()
        flash("Unauthorized access")
        return redirect(url_for('teacher_courses'))

    cursor.execute("""
        SELECT assessment_id, assessment_name, max_marks, weightage
        FROM assessment
        WHERE assessment_id = %s AND course_id = %s
    """, (assessment_id, course_id))
    assessment = cursor.fetchone()

    if not assessment:
        cursor.close()
        conn.close()
        flash("Assessment not found")
        return redirect(url_for('teacher_marks', course_id=course_id))

    if request.method == 'POST':
        try:
            cursor.execute("""
                SELECT r.registration_id, s.student_name, s.usn
                FROM registration r
                JOIN student s ON r.student_id = s.student_id
                WHERE r.course_id = %s
                ORDER BY s.student_name
            """, (course_id,))
            students = cursor.fetchall()

            for student in students:
                field_name = f"marks_{student['registration_id']}"
                obtained = request.form.get(field_name)

                if obtained is None or obtained == '':
                    continue

                obtained = float(obtained)

                if obtained < 0 or obtained > float(assessment['max_marks']):
                    raise ValueError(
                        f"Marks for {student['student_name']} must be between 0 and {assessment['max_marks']}"
                    )

                cursor.execute("""
                    INSERT INTO marks (registration_id, assessment_id, obtained_marks)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE obtained_marks = VALUES(obtained_marks)
                """, (student['registration_id'], assessment_id, obtained))

            conn.commit()
            flash("Marks saved successfully")
            return redirect(url_for('enter_marks', course_id=course_id, assessment_id=assessment_id))

        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}")

    cursor.execute("""
        SELECT r.registration_id, s.student_name, s.usn, m.obtained_marks
        FROM registration r
        JOIN student s ON r.student_id = s.student_id
        LEFT JOIN marks m
            ON r.registration_id = m.registration_id
           AND m.assessment_id = %s
        WHERE r.course_id = %s
        ORDER BY s.student_name
    """, (assessment_id, course_id))
    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'enter_marks.html',
        course=course,
        assessment=assessment,
        students=students
    )


@app.route('/teacher/course/<int:course_id>/results')
def teacher_results(course_id):
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.course_id, c.course_name, c.course_code
        FROM course c
        JOIN teacher t ON c.teacher_id = t.teacher_id
        WHERE c.course_id = %s AND t.user_id = %s
    """, (course_id, user_id))
    course = cursor.fetchone()

    if not course:
        cursor.close()
        conn.close()
        flash("Unauthorized access")
        return redirect(url_for('teacher_courses'))

    cursor.execute("""
        SELECT 
            r.registration_id,
            s.student_name,
            s.usn,
            ROUND(SUM((m.obtained_marks / a.max_marks) * a.weightage), 2) AS total_marks
        FROM registration r
        JOIN student s ON r.student_id = s.student_id
        LEFT JOIN marks m ON r.registration_id = m.registration_id
        LEFT JOIN assessment a ON m.assessment_id = a.assessment_id
        WHERE r.course_id = %s
        GROUP BY r.registration_id, s.student_name, s.usn
        ORDER BY s.student_name
    """, (course_id,))
    results = cursor.fetchall()

    for row in results:
        total = row['total_marks'] if row['total_marks'] is not None else 0
        cursor.execute("""
            SELECT grade_name
            FROM gradecutoff
            WHERE course_id = %s AND %s BETWEEN min_marks AND max_marks
            LIMIT 1
        """, (course_id, total))
        grade_row = cursor.fetchone()
        row['grade_name'] = grade_row['grade_name'] if grade_row else 'N/A'
        row['total_marks'] = total

    cursor.close()
    conn.close()

    return render_template('teacher_results.html', course=course, results=results)

@app.route('/admin/grade_cutoffs')
def view_grade_cutoffs():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT g.grade_id, g.grade_name, g.min_marks, g.max_marks,
               c.course_name, c.course_code
        FROM gradecutoff g
        JOIN course c ON g.course_id = c.course_id
        ORDER BY c.course_name, g.max_marks DESC
    """)
    cutoffs = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('grade_cutoffs.html', cutoffs=cutoffs)


@app.route('/admin/add_grade_cutoff', methods=['GET', 'POST'])
def add_grade_cutoff():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        course_id = request.form['course_id']
        grade_name = request.form['grade_name']
        min_marks = float(request.form['min_marks'])
        max_marks = float(request.form['max_marks'])

        try:
            if min_marks > max_marks:
                raise ValueError("Min marks cannot be greater than max marks")

            cursor.execute("""
                SELECT *
                FROM gradecutoff
                WHERE course_id = %s
                AND NOT (%s < min_marks OR %s > max_marks)
            """, (course_id, max_marks, min_marks))
            overlap = cursor.fetchone()

            if overlap:
                raise ValueError("Grade range overlaps with an existing cutoff")

            cursor.execute("""
                INSERT INTO gradecutoff (course_id, grade_name, min_marks, max_marks)
                VALUES (%s, %s, %s, %s)
            """, (course_id, grade_name, min_marks, max_marks))

            conn.commit()
            flash("Grade cutoff added successfully")
            return redirect(url_for('view_grade_cutoffs'))

        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}")

    cursor.execute("SELECT course_id, course_name, course_code FROM course ORDER BY course_name")
    courses = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('add_grade_cutoff.html', courses=courses)


@app.route('/admin/delete_grade_cutoff/<int:grade_id>')
def delete_grade_cutoff(grade_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM gradecutoff WHERE grade_id = %s", (grade_id,))
        conn.commit()
        flash("Grade cutoff deleted successfully")
    except Exception as e:
        conn.rollback()
        flash(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_grade_cutoffs'))


@app.route('/student/my_courses')
def student_my_courses():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT student_id
        FROM student
        WHERE user_id = %s
    """, (user_id,))
    student = cursor.fetchone()

    if not student:
        cursor.close()
        conn.close()
        flash("Student profile not linked")
        return redirect(url_for('student_dashboard'))

    cursor.execute("""
        SELECT c.course_name, c.course_code, c.credits, r.semester, r.academic_year
        FROM registration r
        JOIN course c ON r.course_id = c.course_id
        WHERE r.student_id = %s
        ORDER BY c.course_name
    """, (student['student_id'],))
    courses = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('student_my_courses.html', courses=courses)


@app.route('/student/my_results')
def student_my_results():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()

    if not student:
        cursor.close()
        conn.close()
        flash("Student profile not linked")
        return redirect(url_for('student_dashboard'))

    cursor.execute("""
        SELECT 
            c.course_name,
            c.course_code,
            r.registration_id,
            r.course_id,
            ROUND(SUM((m.obtained_marks / a.max_marks) * a.weightage), 2) AS total_marks
        FROM registration r
        JOIN course c ON r.course_id = c.course_id
        LEFT JOIN marks m ON r.registration_id = m.registration_id
        LEFT JOIN assessment a ON m.assessment_id = a.assessment_id
        WHERE r.student_id = %s
        GROUP BY c.course_name, c.course_code, r.registration_id, r.course_id
        ORDER BY c.course_name
    """, (student['student_id'],))
    results = cursor.fetchall()

    for row in results:
        total = row['total_marks'] if row['total_marks'] is not None else 0
        cursor.execute("""
            SELECT grade_name
            FROM gradecutoff
            WHERE course_id = %s AND %s BETWEEN min_marks AND max_marks
            LIMIT 1
        """, (row['course_id'], total))
        grade_row = cursor.fetchone()
        row['grade_name'] = grade_row['grade_name'] if grade_row else 'N/A'
        row['total_marks'] = total

    cursor.close()
    conn.close()
    return render_template('student_my_results.html', results=results)


@app.route('/admin/dropout')
def dropout_analysis():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    students = get_student_features()
    
    high = sum(1 for s in students if s['risk_level'] == 'High')
    medium = sum(1 for s in students if s['risk_level'] == 'Medium')
    low = sum(1 for s in students if s['risk_level'] == 'Low')
    
    return render_template('dropout_analysis.html', 
                         students=students,
                         high=high,
                         medium=medium,
                         low=low)


if __name__ == '__main__':
    app.run(debug=True)