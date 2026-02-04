from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
from datetime import date

app = Flask(__name__)
DATABASE = "attendance.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

HOME_HTML = """
<h1>Student Attendance System</h1>
<a href="/add">Add Student</a> | <a href="/mark">Mark Attendance</a>
<hr>
<ul>
{% for s in students %}
  <li>{{ s.name }}</li>
{% endfor %}
</ul>
"""

ADD_HTML = """
<h2>Add Student</h2>
<form method="post">
  <input name="name" required>
  <button>Add</button>
</form>
<a href="/">Back</a>
"""

MARK_HTML = """
<h2>Mark Attendance</h2>
<form method="post">
{% for s in students %}
  {{ s.name }}
  <select name="{{ s.id }}">
    <option>Present</option>
    <option>Absent</option>
  </select><br><br>
{% endfor %}
<button>Submit</button>
</form>
<a href="/">Back</a>
"""

@app.route("/")
def index():
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template_string(HOME_HTML, students=students)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        conn = get_db()
        conn.execute("INSERT INTO students (name) VALUES (?)", (request.form["name"],))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template_string(ADD_HTML)

@app.route("/mark", methods=["GET", "POST"])
def mark():
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()

    if request.method == "POST":
        today = str(date.today())
        for s in students:
            conn.execute(
                "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                (s["id"], today, request.form[str(s["id"])])
            )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn.close()
    return render_template_string(MARK_HTML, students=students)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
