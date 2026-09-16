import sqlite3
import re
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "vsb_secret_key_2026"

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    if search_query:
        students = conn.execute(
            "SELECT * FROM students WHERE name LIKE ? OR roll_number LIKE ? OR department LIKE ?", 
            (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template('index.html', students=students, search_query=search_query)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name'].strip()
        roll_number = request.form['roll_number'].strip()
        email = request.form['email'].strip()
        department = request.form['department'].strip()

        if not name or not roll_number or not email or not department:
            flash("All fields are mandatory!", "danger")
            return redirect(url_for('add_student'))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format!", "danger")
            return redirect(url_for('add_student'))

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO students (name, roll_number, email, department) VALUES (?, ?, ?, ?)",
                (name, roll_number, email, department)
            )
            conn.commit()
            flash("Student added successfully!", "success")
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash("Roll Number already exists!", "danger")
        finally:
            conn.close()

    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name'].strip()
        roll_number = request.form['roll_number'].strip()
        email = request.form['email'].strip()
        department = request.form['department'].strip()

        if not name or not roll_number or not email or not department:
            flash("All fields are mandatory!", "danger")
            return redirect(url_for('edit_student', id=id))

        try:
            conn.execute(
                "UPDATE students SET name = ?, roll_number = ?, email = ?, department = ? WHERE id = ?",
                (name, roll_number, email, department, id)
            )
            conn.commit()
            flash("Student updated successfully!", "success")
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash("Roll Number already exists for another student!", "danger")
        finally:
            conn.close()

    conn.close()
    return render_template('edit.html', student=student)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_student(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Student deleted successfully!", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)