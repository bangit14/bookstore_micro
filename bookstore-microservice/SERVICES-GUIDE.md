# Hướng Dẫn Kiến Trúc & Vận Hành Microservices

## Tổng Quan

Hệ thống BookStore được xây dựng theo kiến trúc **microservices** gồm **12 service** độc lập, giao tiếp với nhau qua HTTP, dùng chung một MySQL server nhưng mỗi service có **database riêng biệt**.

```
Trình duyệt
    ↓
API Gateway (:8000)  ←── Web UI (HTML/JS)
    ↓ proxy HTTP
┌───────────────────────────────────────────────────────────────┐
│  customer  book  cart  catalog  order  pay  ship  staff  ...  │
│  :8001    :8002  :8003  :8006  :8007 :8009 :8008  :8004  ...  │
└───────────────────────────────┬───────────────────────────────┘
                                ↓
                          MySQL :3306
```

---

## Cách Chạy Hệ Thống

### Yêu cầu

- Docker Desktop đang chạy
- Git

### Khởi động toàn bộ

```bash
cd bookstore-microservice
docker compose up -d --build
```

### Kiểm tra trạng thái

```bash
docker compose ps
docker compose logs -f api-gateway        # xem log API Gateway
docker compose logs -f order-service      # xem log 1 service cụ thể
```

### Dừng hệ thống

```bash
docker compose down          # dừng, giữ data
docker compose down -v       # dừng, xóa cả volume (reset DB)
```

### Truy cập

| URL                                       | Mô tả                |
| ----------------------------------------- | -------------------- |
| http://localhost:8000/home/               | Trang chủ (public)   |
| http://localhost:8000/login/              | Đăng nhập            |
| http://localhost:8000/register/           | Đăng ký khách hàng   |
| http://localhost:8000/customer/dashboard/ | Dashboard khách hàng |
| http://localhost:8000/staff/dashboard/    | Dashboard nhân viên  |
| http://localhost:8000/manager/dashboard/  | Dashboard quản lý    |

---

## Thứ Tự Khởi Động (Dependency Chain)

Docker Compose tự động xử lý thứ tự dựa vào `depends_on`:

```
mysql-db (health check)
    ↓
cart-service, book-service, catalog-service, pay-service, ship-service
    ↓
customer-service   (cần cart-service để tạo giỏ hàng tự động)
order-service      (cần pay-service + ship-service)
staff-service
comment-rate-service
    ↓
manager-service    (tổng hợp từ nhiều service)
recommender-ai-service
    ↓
api-gateway        (gateway cuối cùng, cần tất cả)
```

---

## Chi Tiết Từng Service

---

### 1. API Gateway — Port 8000

**Vai trò:** Cổng vào duy nhất của hệ thống. Phục vụ giao diện web HTML/JS và đóng vai trò **proxy** — nhận request từ trình duyệt, gắn thêm JWT header, chuyển tiếp đến đúng service backend.

**Không có database riêng** (dùng SQLite nhỏ cho Django admin).

**Cách hoạt động:**

1. Người dùng đăng nhập → Gateway gọi `customer-service /auth/login/` → nhận JWT
2. JWT được lưu trong **Django session** (server-side)
3. Mọi request tiếp theo → Gateway lấy JWT từ session, thêm vào header `Authorization: Bearer <token>`, gọi service tương ứng
4. Kết quả trả về được render ra HTML hoặc trả JSON cho JavaScript

**Các nhóm route:**

| Nhóm      | Đường dẫn                                                      | Mô tả                   |
| --------- | -------------------------------------------------------------- | ----------------------- |
| Auth      | `/login/`, `/register/`, `/logout/`                            | Xác thực                |
| Customer  | `/customer/dashboard/`, `/customer/cart/`, `/customer/orders/` | Trang khách hàng        |
| Staff     | `/staff/dashboard/`, `/staff/products/`, `/staff/orders/`      | Trang nhân viên         |
| Manager   | `/manager/dashboard/`, `/manager/staff/`, `/manager/orders/`   | Trang quản lý           |
| API Proxy | `/api/books/`, `/api/orders/`, `/api/payments/`, ...           | JSON API cho JavaScript |

**File quan trọng:**

- `gateway/views.py` — toàn bộ logic proxy
- `gateway/urls.py` — bảng route
- `gateway/settings.py` — URL của các service (SERVICE_URL)

---

### 2. Customer Service — Port 8001

**Vai trò:** Quản lý tài khoản người dùng, đăng ký, đăng nhập, phân quyền.

**Database:** `customer_db`

**Models:**

| Model         | Các trường chính                                                          |
| ------------- | ------------------------------------------------------------------------- |
| `Customer`    | name, email, phone, address                                               |
| `UserProfile` | user (FK→Django User), customer (FK), role (`manager`/`staff`/`customer`) |

**Endpoints:**

| Method | URL                                | Quyền                    | Mô tả                                              |
| ------ | ---------------------------------- | ------------------------ | -------------------------------------------------- |
| POST   | `/auth/register/`                  | Public                   | Đăng ký → tạo User + Customer + UserProfile + Cart |
| POST   | `/auth/login/`                     | Public                   | Đăng nhập → trả JWT (access + refresh)             |
| GET    | `/customers/`                      | Manager/Staff            | Danh sách khách hàng                               |
| POST   | `/customers/`                      | Manager/Staff            | Tạo khách hàng + tự động tạo giỏ hàng              |
| GET    | `/customers/<id>/`                 | Chủ sở hữu/Staff/Manager | Chi tiết                                           |
| PATCH  | `/customers/<id>/`                 | Chủ sở hữu/Staff/Manager | Cập nhật                                           |
| DELETE | `/customers/<id>/`                 | Manager                  | Xóa                                                |
| POST   | `/customers/<id>/change-password/` | Chủ sở hữu               | Đổi mật khẩu                                       |

**Luồng đăng ký:**

```
POST /auth/register/
    → Tạo Django User (username, password)
    → Tạo Customer (name, email, phone)
    → Tạo UserProfile (role=customer)
    → Gọi cart-service POST /carts/ (tạo giỏ hàng rỗng)
    → Trả về thông tin tài khoản
```

**JWT Payload:**

```json
{ "username": "user1", "role": "customer", "customer_id": 5, "email": "..." }
```

---

### 3. Book Service — Port 8002

**Vai trò:** Quản lý danh mục sách.

**Database:** `book_db`

**Models:**

| Model  | Các trường chính                                          |
| ------ | --------------------------------------------------------- |
| `Book` | title, author, isbn, image_url, price, stock, description |

**Endpoints:**

| Method    | URL            | Quyền         | Mô tả          |
| --------- | -------------- | ------------- | -------------- |
| GET       | `/books/`      | Public        | Danh sách sách |
| POST      | `/books/`      | Staff/Manager | Thêm sách      |
| GET       | `/books/<id>/` | Đăng nhập     | Chi tiết sách  |
| PUT/PATCH | `/books/<id>/` | Staff/Manager | Cập nhật       |
| DELETE    | `/books/<id>/` | Staff/Manager | Xóa            |

> GET danh sách sách là **public** — không cần đăng nhập, dùng cho trang chủ.

---

### 4. Cart Service — Port 8003

**Vai trò:** Quản lý giỏ hàng của từng khách hàng.

**Database:** `cart_db`

**Models:**

| Model      | Các trường chính             |
| ---------- | ---------------------------- |
| `Cart`     | customer_id (unique)         |
| `CartItem` | cart (FK), book_id, quantity |

**Endpoints:**

| Method | URL                         | Quyền                    | Mô tả                             |
| ------ | --------------------------- | ------------------------ | --------------------------------- |
| GET    | `/carts/`                   | Staff/Manager/Internal   | Danh sách giỏ hàng                |
| POST   | `/carts/`                   | Staff/Manager/Internal   | Tạo giỏ hàng (hoặc lấy nếu đã có) |
| GET    | `/carts/<customer_id>/`     | Chủ sở hữu/Staff/Manager | Giỏ hàng theo khách               |
| GET    | `/cart-items/?cart_id=<id>` | Đăng nhập                | Danh mục món trong giỏ            |
| POST   | `/cart-items/`              | Đăng nhập                | Thêm món vào giỏ                  |
| PATCH  | `/cart-items/<id>/`         | Đăng nhập                | Cập nhật số lượng                 |
| DELETE | `/cart-items/<id>/`         | Đăng nhập                | Xóa món khỏi giỏ                  |

**Logic đặc biệt:**

- Nếu thêm sản phẩm đã có trong giỏ → tự động **cộng thêm số lượng** thay vì báo lỗi
- Khi tạo giỏ hàng (POST `/carts/`): gọi sang book-service để kiểm tra sách tồn tại

---

### 5. Catalog Service — Port 8006

**Vai trò:** Quản lý sản phẩm không phải sách (phụ kiện, văn phòng phẩm...).

**Database:** `catalog_db`

**Models:**

| Model     | Các trường chính                                     |
| --------- | ---------------------------------------------------- |
| `Product` | name, description, category, price, stock, image_url |

**Endpoints:**

| Method | URL          | Quyền         | Mô tả              |
| ------ | ------------ | ------------- | ------------------ |
| GET    | `/products/` | Đăng nhập     | Danh sách sản phẩm |
| POST   | `/products/` | Staff/Manager | Thêm sản phẩm      |

---

### 6. Order Service — Port 8007

**Vai trò:** Tạo và quản lý đơn hàng. Khi tạo đơn hàng, tự động tạo thanh toán và vận đơn ở các service khác.

**Database:** `order_db`

**Models:**

| Model       | Các trường chính                                                |
| ----------- | --------------------------------------------------------------- |
| `Order`     | customer_id, total_amount, status, shipping_address, created_at |
| `OrderItem` | order (FK), product_id, quantity, unit_price                    |

**Status đơn hàng:** `pending` → `created` → `processing` → `paid` → `shipping` → `completed` / `cancelled`

**Endpoints:**

| Method | URL             | Quyền     | Mô tả                                                 |
| ------ | --------------- | --------- | ----------------------------------------------------- |
| GET    | `/orders/`      | Đăng nhập | Danh sách (Manager/Staff: tất cả; Customer: của mình) |
| POST   | `/orders/`      | Đăng nhập | Tạo đơn hàng                                          |
| GET    | `/orders/<id>/` | Đăng nhập | Chi tiết đơn + items                                  |
| PATCH  | `/orders/<id>/` | Đăng nhập | Cập nhật trạng thái                                   |

**Luồng tạo đơn hàng:**

```
POST /orders/
    → Tạo Order + OrderItems trong DB
    → Gọi pay-service POST /payments/  (X-Internal-Token)
    → Gọi ship-service POST /shipments/ (X-Internal-Token)
    → Nếu payment OK → order.status = "paid"
    → Nếu shipment OK → order.status = "shipping"
    → Trả về order đã tạo
```

---

### 7. Pay Service — Port 8009

**Vai trò:** Ghi nhận và theo dõi thanh toán.

**Database:** `pay_db`

**Models:**

| Model     | Các trường chính                                                                                                    |
| --------- | ------------------------------------------------------------------------------------------------------------------- |
| `Payment` | order_id, amount, method (cod/card/bank_transfer/cash), status (pending/success/failed), transaction_id, created_at |

**Endpoints:**

| Method | URL                           | Quyền          | Mô tả                                 |
| ------ | ----------------------------- | -------------- | ------------------------------------- |
| GET    | `/payments/`                  | Staff/Manager  | Danh sách thanh toán                  |
| POST   | `/payments/`                  | Internal Token | Tạo thanh toán (gọi từ order-service) |
| GET    | `/payments/order/<order_id>/` | Staff/Manager  | Thanh toán theo đơn hàng              |

> POST `/payments/` được gọi **nội bộ** từ order-service, dùng header `X-Internal-Token` thay vì JWT.

---

### 8. Ship Service — Port 8008

**Vai trò:** Tạo và theo dõi vận đơn giao hàng.

**Database:** `ship_db`

**Models:**

| Model      | Các trường chính                                                                                  |
| ---------- | ------------------------------------------------------------------------------------------------- |
| `Shipment` | order_id, shipping_address, status (pending/shipping/delivered/failed), tracking_code, created_at |

**Endpoints:**

| Method | URL                            | Quyền          | Mô tả                              |
| ------ | ------------------------------ | -------------- | ---------------------------------- |
| GET    | `/shipments/`                  | Staff/Manager  | Danh sách vận đơn                  |
| POST   | `/shipments/`                  | Internal Token | Tạo vận đơn (gọi từ order-service) |
| GET    | `/shipments/order/<order_id>/` | Staff/Manager  | Vận đơn theo đơn hàng              |

> Tương tự pay-service — được tạo tự động khi order-service tạo đơn hàng.

---

### 9. Staff Service — Port 8004

**Vai trò:** Quản lý thông tin nhân viên (chỉ Manager mới có quyền).

**Database:** `staff_db`

**Models:**

| Model   | Các trường chính                                       |
| ------- | ------------------------------------------------------ |
| `Staff` | username, name, email, department, position, is_active |

**Endpoints:**

| Method    | URL                | Quyền              | Mô tả               |
| --------- | ------------------ | ------------------ | ------------------- |
| GET       | `/staffs/`         | Manager            | Danh sách nhân viên |
| POST      | `/staffs/`         | Manager            | Thêm nhân viên      |
| GET       | `/staffs/profile/` | Staff (chính mình) | Xem profile         |
| GET       | `/staffs/<id>/`    | Manager            | Chi tiết            |
| PUT/PATCH | `/staffs/<id>/`    | Manager            | Cập nhật            |
| DELETE    | `/staffs/<id>/`    | Manager            | Xóa                 |

---

### 10. Manager Service — Port 8005

**Vai trò:** Tổng hợp dữ liệu thống kê từ các service khác cho dashboard quản lý.

**Database:** `manager_db` (không có model, chỉ dùng DB cho Django)

**Hoạt động:**

- Không có dữ liệu riêng
- Khi gọi `GET /manager/dashboard/`, service này đồng thời gọi tới:
  - staff-service → đếm nhân viên
  - order-service → đếm đơn hàng
  - pay-service → đếm thanh toán
  - ship-service → đếm vận đơn
  - catalog-service → đếm sản phẩm
  - comment-rate-service → đếm đánh giá
- Tổng hợp lại thành 1 response JSON

---

### 11. Comment Rate Service — Port 8010

**Vai trò:** Lưu trữ đánh giá (review) và xếp hạng (rating) của sản phẩm.

**Database:** `comment_rate_db`

**Models:**

| Model    | Các trường chính                                           |
| -------- | ---------------------------------------------------------- |
| `Review` | customer_id, product_id, rating (1-5), comment, created_at |

**Endpoints:**

| Method | URL         | Quyền     | Mô tả              |
| ------ | ----------- | --------- | ------------------ |
| GET    | `/reviews/` | Public    | Danh sách đánh giá |
| POST   | `/reviews/` | Đăng nhập | Tạo đánh giá       |

> GET reviews là **public** — dùng cho trang chủ hiển thị đánh giá 5 sao.

---

### 12. Recommender AI Service — Port 8011

**Vai trò:** Đề xuất sản phẩm cá nhân hóa dựa trên lịch sử đánh giá.

**Database:** `recommender_ai_db` (không có model thực sự)

**Hoạt động:**

1. Nhận `GET /recommendations/<customer_id>/`
2. Gọi comment-rate-service lấy toàn bộ reviews
3. Tính **trung bình có trọng số** (weighted average) cho từng `product_id`
4. Xếp hạng và trả về **top 5 sản phẩm**
5. Nếu không có đánh giá nào → fallback gọi book-service lấy top 5 sách mới nhất

**Endpoints:**

| Method | URL                               | Quyền     | Mô tả          |
| ------ | --------------------------------- | --------- | -------------- |
| GET    | `/recommendations/<customer_id>/` | Đăng nhập | Gợi ý sản phẩm |

---

## Xác Thực & Phân Quyền

### JWT Token

Tất cả service đều **ký và xác minh JWT bằng cùng 1 secret key** (`bookstore-shared-jwt-secret`), nên token tạo từ customer-service được chấp nhận ở mọi service khác mà không cần gọi lại.

**Cấu trúc payload:**

```json
{
  "username": "nguyen_van_a",
  "role": "customer",
  "customer_id": 5,
  "email": "a@example.com"
}
```

**Phân quyền theo role:**

| Quyền                   | customer      | staff | manager |
| ----------------------- | ------------- | ----- | ------- |
| Xem sách/sản phẩm       | ✅            | ✅    | ✅      |
| Đặt hàng                | ✅            | ✅    | ✅      |
| Quản lý giỏ hàng        | ✅ (của mình) | ✅    | ✅      |
| Xem tất cả đơn hàng     | ❌            | ✅    | ✅      |
| Cập nhật trạng thái đơn | ❌            | ✅    | ✅      |
| Quản lý nhân viên       | ❌            | ❌    | ✅      |
| Xem thanh toán/vận đơn  | ❌            | ✅    | ✅      |
| Thêm/sửa/xóa sản phẩm   | ❌            | ✅    | ✅      |

### Internal Token

Các service giao tiếp nội bộ (không qua người dùng) dùng header:

```
X-Internal-Token: bookstore-internal-token
```

Dùng cho:

- order-service → pay-service (tạo thanh toán)
- order-service → ship-service (tạo vận đơn)
- customer-service → cart-service (tạo giỏ hàng)

---

## Biến Môi Trường Quan Trọng

Được định nghĩa trong `docker-compose.yml`, áp dụng cho tất cả service:

| Biến                     | Giá trị                       | Mục đích                            |
| ------------------------ | ----------------------------- | ----------------------------------- |
| `JWT_SIGNING_KEY`        | `bookstore-shared-jwt-secret` | Ký/xác minh JWT                     |
| `INTERNAL_SERVICE_TOKEN` | `bookstore-internal-token`    | Gọi nội bộ giữa service             |
| `DJANGO_SECRET_KEY`      | (riêng mỗi service)           | Bảo mật Django session/CSRF         |
| `DB_HOST`                | `mysql-db`                    | Hostname MySQL trong Docker network |
| `DB_PORT`                | `3306`                        | Port MySQL                          |
| `DB_USER`                | `root`                        | User MySQL                          |
| `DB_PASSWORD`            | `rootpassword`                | Mật khẩu MySQL                      |
| `DB_NAME`                | (riêng mỗi service)           | Tên database riêng                  |

---

## Luồng Hoạt Động Điển Hình

### Khách hàng đặt hàng

```
1. Khách đăng nhập: POST /login/
   → Gateway gọi customer-service /auth/login/
   → Nhận JWT, lưu vào session

2. Xem sản phẩm: GET /customer/products/
   → Gateway gọi book-service + catalog-service
   → Hiển thị danh sách

3. Thêm vào giỏ: POST /api/cart-items/
   → Gateway gọi cart-service /cart-items/
   → Lưu CartItem

4. Đặt hàng: POST /api/orders/
   → Gateway gọi order-service /orders/
   → order-service tạo Order + OrderItems
   → order-service gọi pay-service (X-Internal-Token) → tạo Payment
   → order-service gọi ship-service (X-Internal-Token) → tạo Shipment
   → Trả về đơn hàng đã tạo

5. Xem đơn hàng: GET /customer/orders/
   → Gateway gọi order-service /orders/
   → Hiển thị danh sách đơn
```

### Manager quản lý nhân viên

```
1. Đăng nhập với role=manager
2. Vào /manager/staff/ → Gateway gọi staff-service /staffs/
3. Tạo nhân viên mới: POST /api/staff/
   → staff-service tạo Staff record
4. Cập nhật: PATCH /api/staff/<id>/
5. Xóa: DELETE /api/staff/<id>/
```

### Manager cập nhật trạng thái đơn hàng

```
1. Vào /manager/orders/ → load danh sách đơn hàng
2. Click vào đơn → modal hiện chi tiết + dropdown trạng thái
3. Chọn trạng thái mới → PATCH /api/orders/<id>/ {status: "delivered"}
   → Gateway gọi order-service PATCH /orders/<id>/
   → Cập nhật trong DB
   → Trả về đơn hàng mới
4. Table tự cập nhật, statistics cards tự cập nhật
```

---

## Cấu Trúc Thư Mục

```
bookstore-microservice/
├── docker-compose.yml          # Định nghĩa toàn bộ service
├── init-mysql.sql              # Tạo databases MySQL khi khởi động
│
├── api-gateway/                # Port 8000 — Web UI + Proxy
│   ├── gateway/
│   │   ├── views.py            # Toàn bộ logic proxy + view
│   │   ├── urls.py             # Bảng route
│   │   └── settings.py        # Cấu hình + SERVICE URLs
│   └── templates/             # HTML templates
│
├── customer-service/           # Port 8001
├── book-service/               # Port 8002
├── cart-service/               # Port 8003
├── staff-service/              # Port 8004
├── manager-service/            # Port 8005
├── catalog-service/            # Port 8006
├── order-service/              # Port 8007
├── ship-service/               # Port 8008
├── pay-service/                # Port 8009
├── comment-rate-service/       # Port 8010
└── recommender-ai-service/     # Port 8011
```

Mỗi service có cấu trúc Django chuẩn:

```
<service>/
├── Dockerfile
├── requirements.txt
├── manage.py
├── <service_name>/             # Django project (settings, urls)
└── <app>/                      # Django app (models, views, serializers)
```

---

## Ghi Chú Kỹ Thuật

- **Framework:** Django 5.0.7 + Django REST Framework cho tất cả service
- **JWT Library:** `djangorestframework-simplejwt`
- **HTTP Client:** `requests` (gọi giữa các service)
- **Database:** MySQL 8.0 (shared server, isolated databases)
- **Container:** `python:3.12-slim` base image
- **Mạng Docker:** Các service giao tiếp qua tên service (ví dụ: `http://book-service:8000`), không cần IP
- **Timeout:** Mọi HTTP call giữa service đều có timeout 5-6 giây để tránh treo
