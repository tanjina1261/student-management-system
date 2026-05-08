import sqlite3

def get_connection():
    conn = sqlite3.connect("students.db")
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            cgpa TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_student(name, student_id, department, email, phone, cgpa):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO students (name, student_id, department, email, phone, cgpa)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, student_id, department, email, phone, cgpa))
        conn.commit()
        return True, "Student added successfully!"
    except sqlite3.IntegrityError:
        return False, "Student ID already exists!"
    finally:
        conn.close()

def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY id DESC")
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
    conn.close()

def update_student(id, name, student_id, department, email, phone, cgpa):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE students
            SET name=?, student_id=?, department=?, email=?, phone=?, cgpa=?
            WHERE id=?
        """, (name, student_id, department, email, phone, cgpa, id))
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
    cursor.execute("SELECT department, COUNT(*) FROM students GROUP BY department")
    dept_counts = cursor.fetchall()
    conn.close()
    return total, dept_counts