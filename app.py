import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.utils import secure_filename

# =========================================================
# PERBAIKAN PATH: Mengunci lokasi folder agar tidak berpindah
# =========================================================
# Ambil lokasi folder tempat file app.py ini berada
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'),
            static_url_path='/static')

app.secret_key = 'kunci_rahasia_work_hive_sukses'

# Konfigurasi folder upload foto secara absolut
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'img', 'profiles')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder static/img/profiles tercipta di dalam folder project
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="work_hive"
    )

# =========================
# LOGIN & REGISTER
# =========================
@app.route('/')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/auth_login', methods=['POST'])
def auth_login():
    email = request.form['email']
    password = request.form['password']

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()

    if user:
        session['user_id'] = user['id']
        session['nama'] = user['nama_lengkap']
        session['foto'] = user['foto_profil']
        return redirect(url_for('dashboard'))

    return "Login gagal"

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/auth_register', methods=['POST'])
def auth_register():
    nama = request.form['nama']
    email = request.form['email']
    password = request.form['password']
    telp = request.form['telp']

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO users (nama_lengkap, email, password, no_telp, foto_profil)
        VALUES (%s, %s, %s, %s, %s)
    """, (nama, email, password, telp, 'default.png'))
    db.commit()

    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# =========================
# DASHBOARD & LAMARAN
# =========================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lowongan")
    data = cursor.fetchall()
    return render_template('dashboard.html', lowongan=data)

@app.route('/daftar/<int:id>')
def pendaftaran(id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lowongan WHERE id=%s", (id,))
    job = cursor.fetchone()

    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user_data = cursor.fetchone()

    return render_template('form_pendaftaran.html', job=job, user=user_data)

@app.route('/submit_lamaran', methods=['POST'])
def submit_lamaran():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO lamaran (nama_lengkap, jurusan, tamatan_sekolah, jenis_kelamin, perusahaan)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        request.form['nama'],
        request.form['jurusan'],
        request.form['tamatan_sekolah'],
        request.form['jk'],
        request.form['perusahaan']
    ))
    db.commit()
    return redirect(url_for('lamaran_anda'))

@app.route('/lamaran')
def lamaran_anda():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lamaran")
    data = cursor.fetchall()
    return render_template('lamaran.html', lamaran=data)

# =========================
# PROFILE SECTION
# =========================
@app.route('/profile')
def profile_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user_data = cursor.fetchone()

    return render_template('profile.html', user=user_data)

@app.route('/edit_profile')
def edit_profile_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user_data = cursor.fetchone()

    return render_template('form_update_profile.html', user=user_data)

# =========================
# UPDATE PROFILE ACTION
# =========================
@app.route('/update_profile_action', methods=['POST'])
def update_profile_action():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    nama = request.form.get('nama')
    telp = request.form.get('telp')
    tamatan_sekolah = request.form.get('tamatan_sekolah')
    jurusan = request.form.get('jurusan')
    jk = request.form.get('jk')
    file = request.files.get('foto')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT foto_profil FROM users WHERE id=%s", (session['user_id'],))
    user_lama = cursor.fetchone()
    filename = user_lama['foto_profil'] 

    if file and file.filename != '' and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        new_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Simpan file ke folder upload yang sudah dikunci secara absolut
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
        
        if user_lama['foto_profil'] and user_lama['foto_profil'] != 'default.png':
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], user_lama['foto_profil'])
            if os.path.exists(old_path):
                os.remove(old_path)
        
        filename = new_filename

    tamatan_sekolah = request.form.get('tamatan_sekolah')

    cursor.execute("""
    UPDATE users SET
        nama_lengkap=%s,
        no_telp=%s,
        tamatan_sekolah=%s,
        jurusan=%s,
        jenis_kelamin=%s,
        foto_profil=%s
    WHERE id=%s
""", (nama, telp, tamatan_sekolah, jurusan, jk, filename, session['user_id']))

    db.commit()
    
    session['foto'] = filename
    session['nama'] = nama

    return redirect(url_for('profile_page'))

# =========================================================
# ROUTE BARU: HAPUS LAMARAN (Agar tombol hapus berfungsi)
# =========================================================
@app.route('/hapus_lamaran/<int:id>', methods=['POST'])
def hapus_lamaran(id):
    if 'user_id' not in session:
        return "Unauthorized", 401
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM lamaran WHERE id = %s", (id,))
        db.commit()
        return "Success", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(debug=True)