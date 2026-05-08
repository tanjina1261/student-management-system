import sqlite3

def get_connection():
    conn = sqlite3.connect("students.db")
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS students")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            cgpa TEXT NOT NULL,
            earned_credit INTEGER NOT NULL DEFAULT 0,
            total_credit INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_student(name, student_id, department, email, phone, cgpa,
                earned_credit, total_credit):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO students
            (name, student_id, department, email, phone, cgpa,
             earned_credit, total_credit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, student_id, department, email, phone, cgpa,
              earned_credit, total_credit))
        conn.commit()
        return True, "Student added successfully!"
    except sqlite3.IntegrityError:
        return False, "Student ID already exists!"
    finally:
        conn.close()

def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_students(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM students
        WHERE name LIKE ? OR student_id LIKE ? OR department LIKE ?
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    cursor.execute("SELECT id FROM students ORDER BY id ASC")
    rows = cursor.fetchall()
    for new_id, (old_id,) in enumerate(rows, start=1):
        cursor.execute(
            "UPDATE students SET id = ? WHERE id = ?",
            (new_id, old_id))
    cursor.execute(
        "DELETE FROM sqlite_sequence WHERE name='students'")
    new_count = len(rows)
    if new_count > 0:
        cursor.execute(
            "UPDATE sqlite_sequence SET seq = ? WHERE name='students'",
            (new_count,))
    conn.commit()
    conn.close()

def update_student(id, name, student_id, department, email, phone,
                   cgpa, earned_credit, total_credit):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE students
            SET name=?, student_id=?, department=?, email=?,
                phone=?, cgpa=?, earned_credit=?, total_credit=?
            WHERE id=?
        """, (name, student_id, department, email, phone, cgpa,
              earned_credit, total_credit, id))
        conn.commit()
        return True, "Student updated successfully!"
    except sqlite3.IntegrityError:
        return False, "Student ID already exists!"
    finally:
        conn.close()

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]
    cursor.execute(
        "SELECT department, COUNT(*) FROM students "
        "GROUP BY department")
    dept_counts = cursor.fetchall()
    cursor.execute(
        "SELECT AVG(CAST(earned_credit AS FLOAT)) FROM students")
    avg_credit = cursor.fetchone()[0] or 0
    conn.close()
    return total, dept_counts, avg_credit