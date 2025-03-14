# ptud-gk-de02
  
### 1. Thông tin cá nhân
👤 **Võ Tấn Bình** -  **MSSV: 22665691**  

### 2. Mô tả dự án
Ứng dụng quản lý công việc là một hệ thống giúp người dùng tạo và quản lý các công việc cá nhân hoặc nhóm một cách hiệu quả. Ứng dụng cho phép người dùng phân loại công việc, theo dõi tiến độ (status), thời gian tạo, thời gian hoàn thành, và hỗ trợ tải lên hình đại diện (avatar) cá nhân. Ngoài ra, hệ thống phân quyền thành Admin và User, giúp kiểm soát và quản lý công việc rõ ràng.

2.1. Xây dựng ứng dụng thành công, cho phép user upload avatar (hình đại diện):
Đăng ký tài khoản (Register):
Người dùng khi đăng ký có thể tải lên hình đại diện (avatar). Hình ảnh sẽ được lưu vào thư mục static/uploads/ và hiển thị ở thông tin cá nhân và danh sách công việc.
Đăng nhập (Login):
Hệ thống cho phép người dùng đăng nhập bằng tài khoản đã đăng ký.
Thông tin tài khoản:
Sau khi đăng nhập, người dùng có thể xem và cập nhật ảnh đại diện.

2.2 Hiển thị công việc theo dạng thẻ (card):
Mỗi công việc là một thẻ riêng biệt, thể hiện:
Tiêu đề công việc.
Mô tả ngắn.
Trạng thái (status) dưới dạng nhãn màu (pending, in progress, completed).
Danh mục công việc (category) dưới dạng badge (nhãn nhỏ).
Thời gian tạo và thời gian hoàn thành.
Tên người tạo (nếu là admin): 
+ Username: admin
+ Password: admin123

2.3. Quản lý danh mục công việc (Category):
Khi tạo công việc mới, người dùng chọn danh mục (category) cho công việc.
Hiển thị theo danh mục:
Công việc được gắn danh mục cụ thể giúp dễ theo dõi theo loại công việc (ví dụ: Học tập, Công việc, Giải trí,...).

2.4. Quản lý công việc với trạng thái, thời gian tạo và hoàn thành:
a. Quản lý tình trạng công việc (status):
Mỗi công việc có các trạng thái:
Pending (Chưa bắt đầu)
In Progress (Đang thực hiện)
Completed (Hoàn thành)
Người dùng có thể thay đổi trạng thái công việc bằng menu thả (select).
b. Thời gian tạo và hoàn thành:
Mỗi công việc khi được tạo sẽ lưu lại thời gian tạo (created_at).
Khi chuyển trạng thái sang Completed, hệ thống tự động ghi lại thời gian hoàn thành (finished_at).

### 🛠 Công nghệ sử dụng
- **Backend**: Flask, Flask-Login, SQLAlchemy
- **Frontend**: HTML, CSS, Bootstrap
- **Database**: SQLite 

---

## 3. Hướng dẫn Cài đặt
### 🔹 Bước 1: Clone Repository
```sh
git clone git clone https://github.com/binhvotan907/ptud-gk-de02
cd ptud-gk-de-02

```

### 🔹 Bước 2: Thiết lập Database
```sh
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 🔹 Bước 3: Chạy Ứng Dụng
```sh
flask run
```

Ứng dụng sẽ chạy tại: `http://127.0.0.1:5000/`
