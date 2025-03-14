from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
import statistics

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
UPLOAD_FOLDER = 'static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
DATABASE = 'database.db'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Hàm khởi tạo database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Tạo bảng users
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(80) NOT NULL UNIQUE,
        password VARCHAR(120) NOT NULL,
        avatar VARCHAR(200),
        is_admin BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tạo bảng categories
    c.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tạo bảng tasks
    c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(100) NOT NULL,
        description TEXT,
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        finished_at TIMESTAMP,
        user_id INTEGER,
        category_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    ''')

    # Thêm tài khoản admin mặc định nếu chưa tồn tại
    c.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not c.fetchone():
        admin_password = generate_password_hash('admin123')
        c.execute('''
        INSERT INTO users (username, password, is_admin, is_active)
        VALUES (?, ?, 1, 1)
        ''', ('admin', admin_password))

    # Thêm tài khoản user mẫu nếu chưa tồn tại
    c.execute('SELECT * FROM users WHERE username = ?', ('user1',))
    if not c.fetchone():
        user_password = generate_password_hash('user123')
        c.execute('''
        INSERT INTO users (username, password, is_admin, is_active)
        VALUES (?, ?, 0, 1)
        ''', ('user1', user_password))

    # Thêm categories mẫu
    categories = [
        ('Công việc', 'Các task liên quan đến công việc'),
        ('Học tập', 'Các task liên quan đến học tập'),
        ('Cá nhân', 'Các task cá nhân'),
        ('Dự án', 'Các task thuộc dự án')
    ]

    for name, desc in categories:
        c.execute('SELECT * FROM categories WHERE name = ?', (name,))
        if not c.fetchone():
            c.execute('INSERT INTO categories (name, description) VALUES (?, ?)', 
                     (name, desc))

    conn.commit()
    conn.close()

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    # Enable foreign key support
    db.execute('PRAGMA foreign_keys = ON')
    return db

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Khởi tạo database khi khởi động ứng dụng
with app.app_context():
    init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('user_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password) and user['is_active']:
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']
            if user['is_admin']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    
    db = get_db()
    user_id = session['user_id']
    
    # Lấy thông tin user
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    # Lấy danh sách task và category
    tasks = db.execute('''
        SELECT t.*, c.name as category_name 
        FROM tasks t 
        LEFT JOIN categories c ON t.category_id = c.id 
        WHERE t.user_id = ?
        ORDER BY t.created_at DESC
    ''', (user_id,)).fetchall()
    
    categories = db.execute('SELECT * FROM categories').fetchall()
    
    # Thống kê task
    task_stats = {
        'total': len(tasks),
        'pending': len([t for t in tasks if t['status'] == 'pending']),
        'in_progress': len([t for t in tasks if t['status'] == 'in_progress']),
        'completed': len([t for t in tasks if t['status'] == 'completed'])
    }
    
    return render_template('user/dashboard.html', 
                         user=user, 
                         tasks=tasks, 
                         categories=categories, 
                         task_stats=task_stats)

@app.route('/task/add', methods=['POST'])
def add_task():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect(url_for('login'))
    
    title = request.form['title']
    description = request.form['description']
    category_id = request.form['category_id']
    
    db = get_db()
    db.execute('''
        INSERT INTO tasks (title, description, user_id, category_id, status, created_at)
        VALUES (?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
    ''', (title, description, session['user_id'], category_id))
    db.commit()
    
    flash('Task added successfully')
    return redirect(url_for('user_dashboard'))

@app.route('/task/<int:task_id>/update', methods=['POST'])
def update_task():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect(url_for('login'))
    
    task_id = request.form['task_id']
    new_status = request.form['status']
    
    db = get_db()
    if new_status == 'completed':
        db.execute('''
            UPDATE tasks 
            SET status = ?, finished_at = CURRENT_TIMESTAMP 
            WHERE id = ? AND user_id = ?
        ''', (new_status, task_id, session['user_id']))
    else:
        db.execute('''
            UPDATE tasks 
            SET status = ?, finished_at = NULL 
            WHERE id = ? AND user_id = ?
        ''', (new_status, task_id, session['user_id']))
    
    db.commit()
    return redirect(url_for('user_dashboard'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', 
                     (session['user_id'],)).fetchone()
    
    if request.method == 'POST':
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                db.execute('UPDATE users SET avatar = ? WHERE id = ?',
                          (filename, session['user_id']))
                db.commit()
                flash('Profile updated successfully')
                
    return render_template('profile.html', user=user)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('user_dashboard'))
    
    db = get_db()
    # Thống kê tổng quan
    stats = {
        'total_users': db.execute('SELECT COUNT(*) as count FROM users WHERE is_admin = 0').fetchone()['count'],
        'total_tasks': db.execute('SELECT COUNT(*) as count FROM tasks').fetchone()['count'],
        'active_tasks': db.execute('SELECT COUNT(*) as count FROM tasks WHERE status != "completed"').fetchone()['count'],
        'completed_tasks': db.execute('SELECT COUNT(*) as count FROM tasks WHERE status = "completed"').fetchone()['count']
    }
    
    # Lấy danh sách user
    users = db.execute('''
        SELECT u.*, 
               COUNT(t.id) as task_count,
               SUM(CASE WHEN t.status = "completed" THEN 1 ELSE 0 END) as completed_tasks
        FROM users u
        LEFT JOIN tasks t ON u.id = t.user_id
        WHERE u.is_admin = 0
        GROUP BY u.id
    ''').fetchall()
    
    return render_template('admin/dashboard.html', stats=stats, users=users)

@app.route('/admin/user/<int:user_id>')
def admin_user_detail(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('user_dashboard'))
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    tasks = db.execute('''
        SELECT t.*, c.name as category_name 
        FROM tasks t 
        LEFT JOIN categories c ON t.category_id = c.id 
        WHERE t.user_id = ?
    ''', (user_id,)).fetchall()
    
    return render_template('admin/user_detail.html', user=user, tasks=tasks)

@app.route('/admin/user/<int:user_id>/reset_password', methods=['POST'])
def admin_reset_password(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('user_dashboard'))
    
    new_password = request.form['new_password']
    db = get_db()
    
    db.execute('''
        UPDATE users 
        SET password = ? 
        WHERE id = ? AND is_admin = 0
    ''', (generate_password_hash(new_password), user_id))
    db.commit()
    
    flash('Password has been reset successfully')
    return redirect(url_for('admin_user_detail', user_id=user_id))

@app.route('/admin/user/<int:user_id>/toggle', methods=['POST'])
def admin_toggle_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('user_dashboard'))
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user and not user['is_admin']:
        new_status = 0 if user['is_active'] else 1
        db.execute('UPDATE users SET is_active = ? WHERE id = ?', (new_status, user_id))
        db.commit()
        
    return redirect(url_for('admin_user_detail', user_id=user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        db = get_db()
        
        # Kiểm tra username đã tồn tại chưa
        user = db.execute('SELECT * FROM users WHERE username = ?', 
                         (username,)).fetchone()
        
        if user:
            flash('Username already exists')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return redirect(url_for('register'))
        
        # Tạo tài khoản mới
        hashed_password = generate_password_hash(password)
        db.execute('''
            INSERT INTO users (username, password, is_admin, is_active)
            VALUES (?, ?, 0, 1)
        ''', (username, hashed_password))
        db.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

if __name__ == '__main__':
    init_db()  # Khởi tạo database khi chạy app
    app.run(debug=True) 