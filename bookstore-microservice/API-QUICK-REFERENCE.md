# Quick Reference - Role-Based URLs

## 🔑 Login để lấy JWT Token

```bash
# Login as Customer
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "customer1", "password": "password"}'

# Login as Staff
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "staff1", "password": "password"}'

# Login as Manager
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin14"}'
```

**Response:**

```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "role": "manager"
}
```

---

## 📱 CUSTOMER APIs

### Xem Sản Phẩm

```bash
# Xem danh sách sách
curl http://localhost:8002/books/ \
  -H "Authorization: Bearer <customer_token>"

# Xem danh sách sản phẩm
curl http://localhost:8006/products/ \
  -H "Authorization: Bearer <customer_token>"
```

### Giỏ Hàng

```bash
# Thêm vào giỏ
curl -X POST http://localhost:8003/carts/items/ \
  -H "Authorization: Bearer <customer_token>" \
  -H "Content-Type: application/json" \
  -d '{"cart": 1, "book_id": 1, "quantity": 2}'

# Xem giỏ hàng
curl http://localhost:8003/carts/<customer_id>/ \
  -H "Authorization: Bearer <customer_token>"
```

### Đặt Hàng

```bash
# Tạo đơn hàng
curl -X POST http://localhost:8007/orders/ \
  -H "Authorization: Bearer <customer_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "total_amount": 500000,
    "shipping_address": "123 Nguyen Hue, HCMC",
    "payment_method": "cod"
  }'

# Xem đơn hàng của tôi
curl http://localhost:8007/orders/ \
  -H "Authorization: Bearer <customer_token>"
```

### Đánh Giá

```bash
# Viết đánh giá
curl -X POST http://localhost:8010/reviews/ \
  -H "Authorization: Bearer <customer_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "product_id": 5,
    "rating": 5,
    "comment": "Sản phẩm rất tốt!"
  }'

# Xem đánh giá (không cần token)
curl http://localhost:8010/reviews/
```

---

## 👔 STAFF APIs

**Staff có TẤT CẢ quyền Customer + thêm:**

### Quản Lý Sản Phẩm

```bash
# Thêm sách mới
curl -X POST http://localhost:8002/books/ \
  -H "Authorization: Bearer <staff_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn Django",
    "author": "John Doe",
    "price": 299000,
    "stock": 50
  }'

# Thêm sản phẩm mới
curl -X POST http://localhost:8006/products/ \
  -H "Authorization: Bearer <staff_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python Book",
    "description": "Advanced Python",
    "category": "Programming",
    "price": 399000,
    "stock": 30
  }'
```

### Xử Lý Đơn Hàng

```bash
# Xem tất cả đơn hàng
curl http://localhost:8007/orders/ \
  -H "Authorization: Bearer <staff_token>"
```

### Quản Lý Vận Chuyển

```bash
# Xem tất cả vận chuyển
curl http://localhost:8008/shipments/ \
  -H "Authorization: Bearer <staff_token>"

# Tạo đơn vận chuyển
curl -X POST http://localhost:8008/shipments/ \
  -H "Authorization: Bearer <staff_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "shipping_address": "123 Main St",
    "status": "shipping"
  }'
```

### Xem Thanh Toán

```bash
# Xem tất cả thanh toán
curl http://localhost:8009/payments/ \
  -H "Authorization: Bearer <staff_token>"
```

---

## 👨‍💼 MANAGER APIs

**Manager có TẤT CẢ quyền Staff + Customer + thêm:**

### Quản Lý Nhân Viên

```bash
# Xem danh sách nhân viên
curl http://localhost:8004/staffs/ \
  -H "Authorization: Bearer <manager_token>"

# Tạo nhân viên mới
curl -X POST http://localhost:8004/staffs/ \
  -H "Authorization: Bearer <manager_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nguyen Van A",
    "email": "nva@bookstore.com",
    "department": "Sales",
    "position": "Nhân viên bán hàng",
    "is_active": true
  }'
```

### Dashboard

```bash
# Xem dashboard tổng quan
curl http://localhost:8005/dashboard/ \
  -H "Authorization: Bearer <manager_token>"
```

---

## ❌ Test Permissions (Expected Errors)

### Customer không thể thêm sách

```bash
curl -X POST http://localhost:8002/books/ \
  -H "Authorization: Bearer <customer_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "author": "Test", "price": 100, "stock": 10}'
```

**Expected Response: 403 Forbidden**

```json
{
  "error": "Permission denied",
  "detail": "This endpoint requires one of these roles: staff, manager. Your role: customer"
}
```

### Staff không thể quản lý nhân viên

```bash
curl http://localhost:8004/staffs/ \
  -H "Authorization: Bearer <staff_token>"
```

**Expected Response: 403 Forbidden**

```json
{
  "error": "Permission denied",
  "detail": "This endpoint requires one of these roles: manager. Your role: staff"
}
```

### Không có token

```bash
curl http://localhost:8002/books/
```

**Expected Response: 401 Unauthorized**

```json
{
  "error": "Authentication required",
  "detail": "Valid JWT token not provided"
}
```

---

## 📊 Bảng Tóm Tắt URLs

| Endpoint             | Customer | Staff    | Manager  |
| -------------------- | -------- | -------- | -------- |
| `GET /books/`        | ✅       | ✅       | ✅       |
| `POST /books/`       | ❌       | ✅       | ✅       |
| `GET /products/`     | ✅       | ✅       | ✅       |
| `POST /products/`    | ❌       | ✅       | ✅       |
| `POST /carts/items/` | ✅       | ✅       | ✅       |
| `POST /orders/`      | ✅       | ✅       | ✅       |
| `GET /orders/`       | ✅ (own) | ✅ (all) | ✅ (all) |
| `GET /shipments/`    | ❌       | ✅       | ✅       |
| `POST /shipments/`   | ❌       | ✅       | ✅       |
| `GET /payments/`     | ✅ (own) | ✅ (all) | ✅ (all) |
| `POST /reviews/`     | ✅       | ✅       | ✅       |
| `GET /staffs/`       | ❌       | ❌       | ✅       |
| `POST /staffs/`      | ❌       | ❌       | ✅       |
| `GET /dashboard/`    | ❌       | ❌       | ✅       |

---

## 🔧 Troubleshooting

### Lấy role từ token

```bash
# Decode JWT token (paste your token)
echo "eyJhbGci..." | cut -d'.' -f2 | base64 -d 2>/dev/null | python -m json.tool
```

### Test với curl verbose

```bash
curl -v http://localhost:8002/books/ \
  -H "Authorization: Bearer <token>"
```

### Check service logs

```bash
docker logs book-service --tail 50
docker logs order-service --tail 50
```

---

**Xem chi tiết đầy đủ:** [ROLE-BASED-ACCESS-CONTROL.md](ROLE-BASED-ACCESS-CONTROL.md)
