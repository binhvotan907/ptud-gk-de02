-- Tạo bảng Users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) NOT NULL UNIQUE,
    password VARCHAR(120) NOT NULL,
    avatar VARCHAR(200),
    is_admin BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tạo bảng Categories
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tạo bảng Tasks
CREATE TABLE tasks (
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
);

-- Thêm dữ liệu mẫu

-- Thêm users (password là "admin123" và "user123" đã được hash)
INSERT INTO users (username, password, is_admin, is_active) VALUES
('admin', 'pbkdf2:sha256:260000$7NEeGIQRqjvjJHSg$4b6a3a6c886f74b0412a5e5f0e24d21147642d8b94ed1207739562ddcfd37f33', 1, 1),
('user1', 'pbkdf2:sha256:260000$9NEeGIQRqjvjJHSg$5b6a3a6c886f74b0412a5e5f0e24d21147642d8b94ed1207739562ddcfd37f44', 0, 1),
('user2', 'pbkdf2:sha256:260000$8NEeGIQRqjvjJHSg$6b6a3a6c886f74b0412a5e5f0e24d21147642d8b94ed1207739562ddcfd37f55', 0, 1);

-- Thêm categories
INSERT INTO categories (name, description) VALUES
('Công việc', 'Các task liên quan đến công việc'),
('Học tập', 'Các task liên quan đến học tập'),
('Cá nhân', 'Các task cá nhân'),
('Dự án', 'Các task thuộc dự án');

-- Thêm tasks
INSERT INTO tasks (title, description, status, user_id, category_id) VALUES
('Hoàn thành báo cáo', 'Hoàn thành báo cáo quý 1', 'pending', 2, 1),
('Học Flask', 'Học framework Flask của Python', 'in_progress', 2, 2),
('Họp team', 'Họp team review công việc', 'completed', 1, 1),
('Đọc sách', 'Đọc sách về Python', 'pending', 3, 3),
('Phát triển website', 'Phát triển website quản lý task', 'in_progress', 1, 4);

-- Tạo index để tối ưu truy vấn
CREATE INDEX idx_tasks_user ON tasks(user_id);
CREATE INDEX idx_tasks_category ON tasks(category_id);
CREATE INDEX idx_tasks_status ON tasks(status); 