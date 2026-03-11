# Django Admin Panels - Quick Access Guide

## Tài Khoản Admin (Dùng Chung Cho Tất Cả Services)

- **Username:** admin
- **Password:** admin14

⚠️ **LƯU Ý:** Đổi mật khẩu ngay lập tức trong môi trường production!

---

## 🔗 Danh Sách Admin Panels

### Customer Service - Quản Lý Users & Khách Hàng

**URL:** http://localhost:8001/admin/

**Quản lý:**

- Users (Tài khoản người dùng)
- Customers (Khách hàng)
- User Profiles (Hồ sơ người dùng)

**Chức năng:**

- Tạo user với role tùy chỉnh (Customer/Staff/Manager)
- Xem thông tin khách hàng
- Quản lý profile và permissions

---

### Book Service - Quản Lý Sách

**URL:** http://localhost:8002/admin/

**Quản lý:**

- Books (Sách)

**Thông tin sách:**

- Title (Tên sách)
- Author (Tác giả)
- Price (Giá)
- Stock (Số lượng tồn kho)

---

### Cart Service - Quản Lý Giỏ Hàng

**URL:** http://localhost:8003/admin/

**Quản lý:**

- Carts (Giỏ hàng)
- Cart Items (Sản phẩm trong giỏ)

**Chức năng:**

- Xem giỏ hàng của khách hàng
- Quản lý items (inline editing)
- Theo dõi số lượng sản phẩm

---

### Catalog Service - Danh Mục Sản Phẩm

**URL:** http://localhost:8004/admin/

**Quản lý:**

- Products (Sản phẩm)

**Thông tin sản phẩm:**

- Name (Tên)
- Category (Danh mục)
- Price (Giá)
- Stock (Kho)
- Image URL

---

### Order Service - Quản Lý Đơn Hàng

**URL:** http://localhost:8005/admin/

**Quản lý:**

- Orders (Đơn hàng)
- Order Items (Chi tiết đơn hàng)

**Chức năng:**

- Xem tất cả đơn hàng
- Cập nhật trạng thái đơn hàng
- Xem chi tiết sản phẩm (inline)
- Theo dõi tổng tiền và địa chỉ giao hàng

---

### Staff Service - Quản Lý Nhân Viên

**URL:** http://localhost:8006/admin/

**Quản lý:**

- Staffs (Nhân viên)

**Thông tin nhân viên:**

- Name (Tên)
- Email
- Department (Phòng ban)
- Position (Chức vụ)
- Is Active (Trạng thái hoạt động)

---

### Ship Service - Quản Lý Vận Chuyển

**URL:** http://localhost:8008/admin/

**Quản lý:**

- Shipments (Đơn vận chuyển)

**Chức năng:**

- Cập nhật trạng thái vận chuyển
- Quản lý tracking code
- Theo dõi địa chỉ giao hàng
- Liên kết với order ID

---

### Pay Service - Quản Lý Thanh Toán

**URL:** http://localhost:8009/admin/

**Quản lý:**

- Payments (Giao dịch thanh toán)

**Thông tin thanh toán:**

- Order ID
- Amount (Số tiền)
- Method (Phương thức: COD, Card, E-wallet)
- Status (Trạng thái)
- Transaction ID

**Lọc theo:**

- Payment method
- Payment status
- Created date

---

### Comment-Rate Service - Quản Lý Đánh Giá

**URL:** http://localhost:8010/admin/

**Quản lý:**

- Reviews (Đánh giá sản phẩm)

**Thông tin đánh giá:**

- Customer ID
- Product ID
- Rating (Điểm: 1-5 sao)
- Comment (Bình luận)

**Lọc theo:**

- Rating
- Created date

---

## 🗄️ Phân Chia Database

### MySQL Services (localhost:3306)

- customer-service → customer_db
- cart-service → cart_db
- staff-service → staff_db
- ship-service → ship_db

### PostgreSQL Services (localhost:5432)

- book-service → book_db
- catalog-service → catalog_db
- order-service → order_db
- pay-service → pay_db
- comment-rate-service → comment_rate_db

---

## 🚀 Quick Start

1. Đảm bảo tất cả services đang chạy:

   ```bash
   docker compose ps
   ```

2. Mở trình duyệt và truy cập URL admin panel tương ứng

3. Đăng nhập với:
   - Username: `admin`
   - Password: `admin14`

4. Bắt đầu quản lý dữ liệu!

---

## 🔧 Troubleshooting

### Không truy cập được Admin Panel

1. Kiểm tra service đang chạy:

   ```bash
   docker compose ps [service-name]
   ```

2. Xem logs để debug:

   ```bash
   docker logs [service-name]
   ```

3. Verify admin user đã được tạo:
   ```bash
   docker logs [service-name] | grep -i "admin"
   ```
   Kết quả mong đợi: `Successfully created admin user "admin" for [service-name]`

### Reset Admin Password

```bash
docker exec -it [service-name] python manage.py changepassword admin
```

---

## 📝 Ghi Chú

- Mỗi service có Django Admin độc lập với database riêng
- Tài khoản admin được tạo tự động khi service khởi động
- Nếu admin đã tồn tại, sẽ không tạo lại
- Tất cả admin panels sử dụng cùng một tài khoản admin/admin14

**Xem chi tiết hơn trong:** [USER-MANAGEMENT.md](USER-MANAGEMENT.md)
