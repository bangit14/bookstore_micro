# Hướng Dẫn Quản Lý User và Roles

## Tài Khoản Admin Mặc Định

Hệ thống tự động tạo một tài khoản admin khi khởi động:

- **Username:** `admin`
- **Password:** `admin14`
- **Role:** Manager (Quản lý)

Tài khoản này có đầy đủ quyền quản trị và có thể truy cập Django Admin Panel.

## Đăng Ký Tài Khoản Thông Thường

Khi người dùng đăng ký tài khoản qua giao diện web tại `/register/`:

- Role tự động được gán là **Customer (Khách hàng)**
- Người dùng không thể chọn role khi đăng ký
- Tự động tạo profile và cart cho khách hàng

## Quản Lý Users qua Django Admin

### Truy cập Django Admin:

1. Mở trình duyệt và truy cập: http://localhost:8001/admin/
2. Đăng nhập với tài khoản admin:
   - Username: `admin`
   - Password: `admin14`

### Tạo User Mới với Role Tùy Chỉnh:

1. Vào **Users** → **Add User**
2. Nhập username và password
3. Click **Save and continue editing**
4. Trong phần **Profile**, chọn Role:
   - **Customer** - Khách hàng (mặc định)
   - **Staff** - Nhân viên
   - **Manager** - Quản lý
5. Nếu chọn role "Customer", có thể liên kết với Customer record
6. Click **Save**

### Sửa Role của User Hiện Tại:

1. Vào **Users** → Chọn user cần sửa
2. Kéo xuống phần **Profile**
3. Thay đổi **Role**
4. Click **Save**

## Truy Cập Django Admin Các Microservices

Mỗi microservice đều có Django Admin Panel riêng để quản lý dữ liệu của service đó. Tất cả đều sử dụng cùng một tài khoản admin:

- **Username:** `admin`
- **Password:** `admin14`

### Danh Sách Admin Panels:

| Service                  | URL                          | Quản Lý Đối Tượng               |
| ------------------------ | ---------------------------- | ------------------------------- |
| **Customer Service**     | http://localhost:8001/admin/ | Users, Customers, User Profiles |
| **Book Service**         | http://localhost:8002/admin/ | Books (Sách)                    |
| **Cart Service**         | http://localhost:8003/admin/ | Carts, Cart Items (Giỏ hàng)    |
| **Catalog Service**      | http://localhost:8004/admin/ | Products (Danh mục sản phẩm)    |
| **Order Service**        | http://localhost:8005/admin/ | Orders, Order Items (Đơn hàng)  |
| **Staff Service**        | http://localhost:8006/admin/ | Staffs (Nhân viên)              |
| **Ship Service**         | http://localhost:8008/admin/ | Shipments (Vận chuyển)          |
| **Pay Service**          | http://localhost:8009/admin/ | Payments (Thanh toán)           |
| **Comment-Rate Service** | http://localhost:8010/admin/ | Reviews (Đánh giá)              |

### Hướng Dẫn Sử Dụng:

**Quản lý Book (Sách):**

- Vào http://localhost:8002/admin/
- Chọn **Books** → **Add Book**
- Nhập: Title (Tên sách), Author (Tác giả), Price (Giá), Stock (Kho)

**Quản lý Orders (Đơn hàng):**

- Vào http://localhost:8005/admin/
- Chọn **Orders** để xem tất cả đơn hàng
- Click vào đơn hàng để xem chi tiết và cập nhật trạng thái
- Order Items được hiển thị inline trong đơn hàng

**Quản lý Payments (Thanh toán):**

- Vào http://localhost:8009/admin/
- Chọn **Payments** để xem lịch sử giao dịch
- Có thể lọc theo method (phương thức), status (trạng thái)

**Quản lý Shipments (Vận chuyển):**

- Vào http://localhost:8008/admin/
- Chọn **Shipments** để quản lý đơn vận chuyển
- Cập nhật tracking code và status

**Quản lý Reviews (Đánh giá):**

- Vào http://localhost:8010/admin/
- Chọn **Reviews** để xem đánh giá của khách hàng
- Có thể lọc theo rating (điểm đánh giá)

### Lưu Ý:

⚠️ Mỗi service có database riêng biệt:

- **MySQL Services:** Customer, Cart, Staff, Manager, Ship
- **PostgreSQL Services:** Book, Catalog, Order, Pay, Comment-Rate, Recommender-AI

Do đó, cần truy cập admin panel của từng service để quản lý dữ liệu tương ứng.

## Phân Quyền Theo Role

### Customer (Khách hàng)

- Xem và mua sách
- Quản lý giỏ hàng cá nhân
- Đặt hàng và theo dõi đơn hàng
- Viết đánh giá sản phẩm

### Staff (Nhân viên)

- Tất cả quyền của Customer
- Thêm/sửa sách trong hệ thống
- Xem danh sách khách hàng
- Quản lý đơn hàng

### Manager (Quản lý)

- Tất cả quyền của Staff
- Xem dashboard quản lý
- Quản lý nhân viên
- Truy cập tất cả chức năng hệ thống

## Lưu Ý Bảo Mật

⚠️ **QUAN TRỌNG:**

1. **Đổi mật khẩu admin ngay lập tức** trong môi trường production
2. Không chia sẻ tài khoản admin với nhiều người
3. Tạo tài khoản riêng cho từng quản lý/nhân viên
4. Sử dụng mật khẩu mạnh (ít nhất 12 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt)

### Đổi Mật Khẩu Admin:

**Qua Django Admin:**

1. Đăng nhập vào http://localhost:8001/admin/
2. Click vào username ở góc phải → **Change password**
3. Nhập mật khẩu mới và xác nhận
4. Click **Change password**

**Qua Command Line:**

```bash
docker exec -it customer-service python manage.py changepassword admin
```

## API Endpoints

### Đăng Nhập

```bash
POST http://localhost:8001/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin14"
}
```

**Response:**

```json
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc..."
}
```

### Đăng Ký (Public - Role mặc định: Customer)

```bash
POST http://localhost:8001/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "password": "password123",
  "email": "user@example.com",
  "name": "Full Name"
}
```

**Response:**

```json
{
  "id": 2,
  "username": "newuser",
  "email": "user@example.com",
  "role": "customer",
  "customer_id": 1
}
```

## Troubleshooting

### Admin không thể đăng nhập

1. Kiểm tra customer-service đang chạy:
   ```bash
   docker compose ps customer-service
   ```
2. Xem logs để kiểm tra lỗi:
   ```bash
   docker compose logs customer-service --tail=50
   ```
3. Tạo lại admin user:
   ```bash
   docker exec -it customer-service python manage.py create_admin
   ```

### User đăng ký không có role customer

- Kiểm tra api-gateway đã restart chưa
- Xem logs api-gateway để debug
- Verify code trong `gateway/views.py` → `register_view()`

### Không thể truy cập Django Admin

- Đảm bảo truy cập đúng URL: http://localhost:8001/admin/
- Kiểm tra port của customer-service: `docker compose ps`
- Verify admin user đã được tạo trong database
