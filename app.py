from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_university_key_2026'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

DEPARTMENTS = {
    'Computer Science': 'fa-laptop-code',
    'Data Science': 'fa-database',
    'Artificial Intelligence': 'fa-robot',
    'Cyber Security': 'fa-shield-halved'
}

SUBJECTS = {
    'Calculus': 'fa-calculator',
    'OOP': 'fa-code',
    'Internet Technology': 'fa-globe',
    'Probability & Statistics': 'fa-chart-pie',
    'Islamic Creed': 'fa-book-quran',
    'Management and Innovation': 'fa-lightbulb',
    'Operating Systems': 'fa-server'
}

def get_db_connection():
    conn = sqlite3.connect('university.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            department TEXT NOT NULL,
            subject TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Insert a dummy doctor for testing if it doesn't exist
    doctor = conn.execute("SELECT * FROM doctors WHERE email = 'doctor@univ.edu'").fetchone()
    if not doctor:
        conn.execute("INSERT INTO doctors (email, password) VALUES ('doctor@univ.edu', 'password123')")
    
    conn.commit()
    conn.close()

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('departments.html', departments=DEPARTMENTS)

@app.route('/subjects/<department>')
def subjects(department):
    if department not in DEPARTMENTS:
        return "Department not found", 404
    return render_template('index.html', subjects=SUBJECTS, department=department)

@app.route('/subject/<department>/<name>')
def subject(department, name):
    if department not in DEPARTMENTS:
        return "Department not found", 404
    if name not in SUBJECTS:
        return "Subject not found", 404
    conn = get_db_connection()
    files = conn.execute('SELECT * FROM files WHERE department = ? AND subject = ? ORDER BY upload_date DESC', (department, name)).fetchall()
    conn.close()
    return render_template('subject.html', department=department, subject=name, files=files, icon=SUBJECTS[name])



@app.route('/download/<int:file_id>')
def download(file_id):
    conn = get_db_connection()
    file = conn.execute('SELECT * FROM files WHERE id = ?', (file_id,)).fetchone()
    conn.close()
    if file:
        return send_from_directory(app.config['UPLOAD_FOLDER'], file['filename'], as_attachment=True, download_name=file['original_filename'])
    return "File not found", 404

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        doctor = conn.execute('SELECT * FROM doctors WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()
        
        if doctor:
            session['doctor_id'] = doctor['id']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('doctor_id', None)
    return redirect(url_for('login'))

@app.route('/dashboard', methods=('GET', 'POST'))
def dashboard():
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        department = request.form.get('department')
        subject = request.form.get('subject')
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if file and department in DEPARTMENTS and subject in SUBJECTS:
            original_filename = file.filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            
            conn.execute('INSERT INTO files (filename, original_filename, department, subject) VALUES (?, ?, ?, ?)',
                         (unique_filename, original_filename, department, subject))
            conn.commit()
            flash('File uploaded successfully', 'success')
            return redirect(url_for('dashboard'))
            
    files = conn.execute('SELECT * FROM files ORDER BY upload_date DESC').fetchall()
    conn.close()
    return render_template('dashboard.html', files=files, departments=DEPARTMENTS.keys(), subjects=SUBJECTS.keys())

@app.route('/delete/<int:file_id>', methods=('POST',))
def delete_file(file_id):
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    file = conn.execute('SELECT * FROM files WHERE id = ?', (file_id,)).fetchone()
    
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file['filename'])
        if os.path.exists(file_path):
            os.remove(file_path)
            
        conn.execute('DELETE FROM files WHERE id = ?', (file_id,))
        conn.commit()
        flash('File deleted successfully', 'success')
        
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/replace/<int:file_id>', methods=('POST',))
def replace_file(file_id):
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
        
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('dashboard'))
        
    new_file = request.files['file']
    if new_file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('dashboard'))
        
    conn = get_db_connection()
    file_record = conn.execute('SELECT * FROM files WHERE id = ?', (file_id,)).fetchone()
    
    if file_record and new_file:
        old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_record['filename'])
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except Exception as e:
                print(f"Error removing old file: {e}")
            
        original_filename = new_file.filename
        filename = secure_filename(new_file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        
        new_file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        
        conn.execute('UPDATE files SET filename = ?, original_filename = ?, upload_date = CURRENT_TIMESTAMP WHERE id = ?',
                     (unique_filename, original_filename, file_id))
        conn.commit()
        flash('File replaced successfully', 'success')
        
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port , debug=False)
