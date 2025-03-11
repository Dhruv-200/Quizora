from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Hardcoded credentials for demo purposes
USERS = {
    "admin@example.com": {"password": "password", "role": "admin"},
    "student1@example.com": {"password": "password", "role": "student"},
    "student2@example.com": {"password": "password", "role": "student"}
}

def init_db():
    conn = sqlite3.connect('quiz_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS quizzes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS questions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  quiz_id INTEGER,
                  question_text TEXT NOT NULL,
                  FOREIGN KEY (quiz_id) REFERENCES quizzes(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS options
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  question_id INTEGER,
                  option_text TEXT NOT NULL,
                  is_correct BOOLEAN,
                  FOREIGN KEY (question_id) REFERENCES questions(id))''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if email in USERS and USERS[email]['password'] == password:
        session['email'] = email
        session['role'] = USERS[email]['role']
        
        if USERS[email]['role'] == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('student'))
    else:
        flash('Invalid email or password')
        return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        flash('Unauthorized access')
        return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/student')
def student():
    if session.get('role') != 'student':
        flash('Unauthorized access')
        return redirect(url_for('index'))
    return render_template('student.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if session.get('role') != 'admin':
        flash('Unauthorized access')
        return redirect(url_for('index'))

    if request.method == 'POST':
        quiz_title = request.form.get('quiz-title')
        conn = sqlite3.connect('quiz_system.db')
        c = conn.cursor()

        c.execute("INSERT INTO quizzes (title) VALUES (?)", (quiz_title,))
        quiz_id = c.lastrowid

        for i in range(1, 11):  # Assuming 10 questions
            question_text = request.form.get(f'question-{i}-text')
            c.execute("INSERT INTO questions (quiz_id, question_text) VALUES (?, ?)", (quiz_id, question_text))
            question_id = c.lastrowid

            for j in range(1, 5):  # 4 options per question
                option_text = request.form.get(f'question-{i}-option-{j}')
                is_correct = request.form.get(f'question-{i}-correct') == str(j)
                c.execute("INSERT INTO options (question_id, option_text, is_correct) VALUES (?, ?, ?)",
                          (question_id, option_text, is_correct))

        conn.commit()
        conn.close()

        return jsonify({"success": True})

    return render_template('create_quiz.html')

@app.route('/available_quizzes')
def available_quizzes():
    if session.get('role') != 'student':
        flash('Unauthorized access')
        return redirect(url_for('index'))

    conn = sqlite3.connect('quiz_system.db')
    c = conn.cursor()
    c.execute("SELECT id, title FROM quizzes")
    quizzes = c.fetchall()
    conn.close()

    return render_template('available_quizzes.html', quizzes=quizzes)

@app.route('/take_quiz/<int:quiz_id>')
def take_quiz(quiz_id):
    if session.get('role') != 'student':
        flash('Unauthorized access')
        return redirect(url_for('index'))

    conn = sqlite3.connect('quiz_system.db')
    c = conn.cursor()
    
    c.execute("SELECT title FROM quizzes WHERE id = ?", (quiz_id,))
    quiz_title = c.fetchone()[0]

    c.execute("SELECT id, question_text FROM questions WHERE quiz_id = ?", (quiz_id,))
    questions = c.fetchall()

    quiz = {
        "id": quiz_id,
        "title": quiz_title,
        "questions": []
    }

    for question in questions:
        c.execute("SELECT id, option_text FROM options WHERE question_id = ?", (question[0],))
        options = c.fetchall()
        quiz["questions"].append({
            "id": question[0],
            "text": question[1],
            "options": options
        })

    conn.close()

    return render_template('take_quiz.html', quiz=quiz)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if session.get('role') != 'student':
        return jsonify({"success": False, "error": "Unauthorized access"})

    answers = request.form
    conn = sqlite3.connect('quiz_system.db')
    c = conn.cursor()

    results = []

    for question_id, selected_option_id in answers.items():
        question_id = question_id.split('-')[1]
        c.execute("SELECT id FROM options WHERE question_id = ? AND is_correct = 1", (question_id,))
        correct_option_id = c.fetchone()[0]
        
        is_correct = int(selected_option_id) == correct_option_id
        results.append({
            "question_id": question_id,
            "selected_option": int(selected_option_id),
            "correct_option": correct_option_id,
            "is_correct": is_correct
        })

    conn.close()

    return jsonify({"success": True, "results": results})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)