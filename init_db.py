import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    # Kết nối đến database
    conn = sqlite3.connect('database.db')
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

    # Thêm tài khoản admin mặc định
    admin_password = generate_password_hash('admin123')
    try:
        c.execute('''
        INSERT INTO users (username, password, is_admin, is_active)
        VALUES (?, ?, 1, 1)
        ''', ('admin', admin_password))
    except sqlite3.IntegrityError:
        print("Admin account already exists")

    # Thêm tài khoản user mẫu
    user_password = generate_password_hash('user123')
    try:
        c.execute('''
        INSERT INTO users (username, password, is_admin, is_active)
        VALUES (?, ?, 0, 1)
        ''', ('user1', user_password))
    except sqlite3.IntegrityError:
        print("User1 account already exists")

    # Thêm categories mẫu
    categories = [
        ('Công việc', 'Các task liên quan đến công việc'),
        ('Học tập', 'Các task liên quan đến học tập'),
        ('Cá nhân', 'Các task cá nhân'),
        ('Dự án', 'Các task thuộc dự án')
    ]

    for category in categories:
        try:
            c.execute('''
            INSERT INTO categories (name, description)
            VALUES (?, ?)
            ''', category)
        except sqlite3.IntegrityError:
            print(f"Category {category[0]} already exists")

    # Commit các thay đổi và đóng kết nối
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!") 