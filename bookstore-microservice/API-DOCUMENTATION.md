# BookStore API Documentation

**Base URL:** `http://localhost:8000`  
**Auth:** Session-based (cookie). Login via `POST /login/` to receive session.  
**API Proxy Auth:** All `/api/*` endpoints require active session (JWT stored server-side).

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [Books API](#2-books-api)
3. [Orders API](#3-orders-api)
4. [Cart API](#4-cart-api)
5. [Customers API](#5-customers-api)
6. [Staff API](#6-staff-api)
7. [Payments API](#7-payments-api)
8. [Shipments API](#8-shipments-api)
9. [Reviews API](#9-reviews-api)
10. [Products (Catalog) API](#10-products-catalog-api)
11. [Recommendations API](#11-recommendations-api)
12. [Manager Dashboard API](#12-manager-dashboard-api)
13. [UI Pages](#13-ui-pages)

---

## 1. Authentication

### POST `/login/`

Login and create session.

**Request Body (form):**

```
username=john_doe&password=secret123
```

**Response:** Redirects to role dashboard (`/customer/dashboard/`, `/staff/dashboard/`, `/manager/dashboard/`)

**Session stores:** `access_token`, `username`, `role`, `customer_id`, `staff_position`

---

### POST `/register/`

Register new customer account.

**Request Body (form):**

```
username=john&password=secret&email=john@example.com&name=John Doe&phone=0901234567&address=Hanoi
```

**Response:** Redirects to `/login/`

---

### GET `/logout/`

Destroy session and redirect to `/home/`.

---

### POST `/api/customers/<id>/change-password/`

Change password for a customer.

**Headers:** Session cookie required  
**Request Body (JSON):**

```json
{
  "old_password": "current_pass",
  "new_password": "new_pass"
}
```

**Response:**

```json
{ "message": "Password changed successfully" }
```

---

## 2. Books API

### GET `/api/books/`

Get all books. **Public — no auth required.**

**Response:**

```json
[
  {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "image_url": "https://...",
    "price": "299000.00",
    "stock": 50,
    "description": "...",
    "publisher": 1,
    "category": 2,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
  }
]
```

---

### GET `/api/books/<id>/`

Get single book detail. **Requires auth.**

**Response:** Single book object (same schema as above)

---

### POST `/api/books/`

Create a new book. **Requires staff/manager role.**

**Request Body (JSON):**

```json
{
  "title": "Book Title",
  "author": "Author Name",
  "isbn": "1234567890",
  "image_url": "https://example.com/cover.jpg",
  "price": "150000.00",
  "stock": 100,
  "description": "Book description",
  "publisher": 1,
  "category": 1
}
```

**Response:** `201 Created` with book object

---

### PUT `/api/books/<id>/`

Update a book. **Requires staff/manager role.**

**Request Body (JSON):** Same fields as POST (partial update supported)

**Response:** Updated book object

---

### DELETE `/api/books/<id>/`

Delete a book. **Requires staff/manager role.**

**Response:** `204 No Content`

---

## 3. Orders API

### GET `/api/orders/`

Get all orders. **Requires auth.**

- Customer: sees only their own orders
- Staff/Manager: sees all orders

**Response:**

```json
[
  {
    "id": 1,
    "customer_id": 42,
    "total_amount": "450000.00",
    "status": "pending",
    "shipping_address": "123 Main St, Hanoi",
    "created_at": "2026-03-01T10:00:00Z",
    "items": [
      {
        "id": 1,
        "product_id": 5,
        "quantity": 2,
        "unit_price": "150000.00"
      }
    ]
  }
]
```

**Status values:** `pending` · `created` · `processing` · `paid` · `shipping` · `completed` · `cancelled`

---

### POST `/api/orders/`

Create a new order. **Requires customer role.**

**Request Body (JSON):**

```json
{
  "customer_id": 42,
  "total_amount": "450000.00",
  "shipping_address": "123 Main St, Hanoi",
  "items": [{ "product_id": 5, "quantity": 2, "unit_price": "150000.00" }]
}
```

**Response:** `201 Created` with order object

---

### GET `/api/orders/<id>/`

Get single order detail. **Requires auth.**

**Response:** Single order object (same schema as above)

---

### PATCH `/api/orders/<id>/`

Update order status. **Requires staff/manager role.**

**Request Body (JSON):**

```json
{ "status": "processing" }
```

**Response:** Updated order object

---

### DELETE `/api/orders/<id>/`

Delete an order. **Requires manager role.**

**Response:** `204 No Content`

---

## 4. Cart API

### GET `/api/carts/`

Get all carts. **Requires auth.**

**Response:**

```json
[
  {
    "id": 1,
    "customer_id": 42,
    "items": [{ "id": 1, "book_id": 3, "quantity": 2 }]
  }
]
```

---

### GET `/api/carts/customer/<customer_id>/`

Get cart for a specific customer. **Requires auth.**

**Response:** Single cart object

---

### POST `/api/carts/`

Create a new cart. **Requires auth.**

**Request Body (JSON):**

```json
{ "customer_id": 42 }
```

---

### GET `/api/cart-items/`

Get all cart items. **Requires auth.**

---

### POST `/api/cart-items/`

Add item to cart. **Requires auth.**

**Request Body (JSON):**

```json
{
  "cart": 1,
  "book_id": 5,
  "quantity": 2
}
```

**Response:** `201 Created` with cart item object

---

### PUT `/api/cart-items/<id>/`

Update cart item quantity. **Requires auth.**

**Request Body (JSON):**

```json
{ "quantity": 3 }
```

---

### DELETE `/api/cart-items/<id>/`

Remove item from cart. **Requires auth.**

**Response:** `204 No Content`

---

## 5. Customers API

### GET `/api/customers/`

Get all customers. **Requires staff/manager role.**

**Response:**

```json
[
  {
    "id": 1,
    "name": "Nguyen Van A",
    "email": "nguyenvana@example.com",
    "phone": "0901234567",
    "address": "Hanoi, Vietnam"
  }
]
```

---

### GET `/api/customers/<id>/`

Get single customer. **Requires auth.**

**Response:** Single customer object

---

### PUT `/api/customers/<id>/`

Update customer profile. **Requires auth (own profile) or manager.**

**Request Body (JSON):**

```json
{
  "name": "Updated Name",
  "phone": "0987654321",
  "address": "New Address"
}
```

---

### DELETE `/api/customers/<id>/`

Delete customer. **Requires manager role.**

**Response:** `204 No Content`

---

## 6. Staff API

### GET `/api/staff/`

Get all staff members. **Requires manager role.**

**Response:**

```json
[
  {
    "id": 1,
    "username": "staff_user",
    "email": "staff@example.com",
    "department": "Sales",
    "position": "sales"
  }
]
```

---

### GET `/api/staff/<id>/`

Get single staff member. **Requires manager role.**

---

### POST `/api/staff/`

Create new staff. **Requires manager role.**

**Request Body (JSON):**

```json
{
  "username": "new_staff",
  "email": "staff@example.com",
  "password": "pass123",
  "department": "Warehouse",
  "position": "warehouse"
}
```

---

### PUT `/api/staff/<id>/`

Update staff. **Requires manager role.**

---

### DELETE `/api/staff/<id>/`

Delete staff. **Requires manager role.**

**Response:** `204 No Content`

---

## 7. Payments API

### GET `/api/payments/`

Get all payments. **Requires staff/manager role.**

**Response:**

```json
[
  {
    "id": 1,
    "order_id": 5,
    "amount": "450000.00",
    "method": "cod",
    "status": "pending",
    "transaction_id": "",
    "created_at": "2026-03-01T10:00:00Z"
  }
]
```

**Method values:** `cod` · `bank_transfer` · `credit_card` · `momo` · `zalopay`  
**Status values:** `pending` · `completed` · `failed` · `refunded`

---

### POST `/api/payments/`

Create a payment. **Requires auth.**

**Request Body (JSON):**

```json
{
  "order_id": 5,
  "amount": "450000.00",
  "method": "cod"
}
```

**Response:** `201 Created` with payment object

---

## 8. Shipments API

### GET `/api/shipments/`

Get all shipments. **Requires staff/manager role.**

**Response:**

```json
[
  {
    "id": 1,
    "order_id": 5,
    "shipping_address": "123 Main St, Hanoi",
    "status": "pending",
    "tracking_code": "VN123456789",
    "created_at": "2026-03-01T10:00:00Z"
  }
]
```

**Status values:** `pending` · `processing` · `shipped` · `delivered` · `cancelled`

---

### GET `/api/shipments/<id>/`

Get single shipment. **Requires auth.**

---

### POST `/api/shipments/`

Create a shipment. **Requires staff/manager role.**

**Request Body (JSON):**

```json
{
  "order_id": 5,
  "shipping_address": "123 Main St, Hanoi"
}
```

---

### PATCH `/api/shipments/<id>/`

Update shipment status or tracking code. **Requires staff/manager role.**

**Request Body (JSON):**

```json
{
  "status": "shipped",
  "tracking_code": "VN123456789"
}
```

---

## 9. Reviews API

### GET `/api/reviews/`

Get all reviews. **Public — no auth required.**

**Response:**

```json
[
  {
    "id": 1,
    "customer_id": 42,
    "product_id": 3,
    "rating": 5,
    "comment": "Great book!",
    "created_at": "2026-03-01T10:00:00Z"
  }
]
```

---

### POST `/api/reviews/`

Create a review. **Requires auth.**

**Request Body (JSON):**

```json
{
  "customer_id": 42,
  "product_id": 3,
  "rating": 5,
  "comment": "Excellent read, highly recommended!"
}
```

**Response:** `201 Created` with review object

---

### GET `/api/reviews/<id>/`

Get single review. **Requires auth.**

---

### PUT `/api/reviews/<id>/`

Update a review. **Requires auth (own review only).**

---

### DELETE `/api/reviews/<id>/`

Delete a review. **Requires auth.**

**Response:** `204 No Content`

---

## 10. Products (Catalog) API

### GET `/api/products/`

Get all catalog products. **Requires auth.**

**Response:**

```json
[
  {
    "id": 1,
    "name": "Product Name",
    "description": "...",
    "price": "150000.00",
    "stock": 100,
    "is_active": true
  }
]
```

---

### POST `/api/products/`

Create catalog product. **Requires staff/manager role.**

---

### GET `/api/products/<id>/`

Get single product. **Requires auth.**

---

### PUT `/api/products/<id>/`

Update product. **Requires staff/manager role.**

---

### DELETE `/api/products/<id>/`

Delete product. **Requires manager role.**

---

## 11. Recommendations API

### GET `/api/recommendations/<customer_id>/`

Get AI-powered book recommendations for a customer. **Requires auth.**

**Response:**

```json
[
  {
    "id": 3,
    "title": "The Pragmatic Programmer",
    "author": "David Thomas",
    "price": "250000.00",
    "score": 0.92
  }
]
```

---

## 12. Manager Dashboard API

### GET `/api/manager/dashboard/`

Get aggregated statistics. **Requires manager role.**

**Response:**

```json
{
  "total_orders": 150,
  "total_revenue": "45000000.00",
  "total_customers": 320,
  "total_books": 12,
  "orders_by_status": {
    "pending": 10,
    "processing": 25,
    "completed": 100,
    "cancelled": 15
  },
  "recent_orders": []
}
```

---

## 13. UI Pages

### Public Pages (no login required)

| URL              | Description                       |
| ---------------- | --------------------------------- |
| `GET /home/`     | Landing page with books & reviews |
| `GET /login/`    | Login page                        |
| `GET /register/` | Register page                     |

---

### Customer Pages (role: customer)

| URL                              | Description             |
| -------------------------------- | ----------------------- |
| `GET /customer/dashboard/`       | Customer home dashboard |
| `GET /customer/products/`        | Browse all books        |
| `GET /customer/cart/`            | View shopping cart      |
| `GET /customer/orders/`          | View order history      |
| `GET /customer/profile/`         | View/edit profile       |
| `GET /customer/reviews/`         | Manage own reviews      |
| `GET /customer/recommendations/` | AI book recommendations |

---

### Staff Pages (role: staff)

| URL                               | Description            |
| --------------------------------- | ---------------------- |
| `GET /staff/dashboard/`           | Staff home dashboard   |
| `GET /staff/products/`            | Manage books/products  |
| `GET /staff/orders/`              | View & process orders  |
| `GET /staff/inventory/`           | Manage inventory/stock |
| `GET /staff/shipments/`           | Manage shipments       |
| `GET /staff/customers/`           | View customers         |
| `GET /staff/reviews/`             | Moderate reviews       |
| `GET /staff/warehouse/`           | Warehouse dashboard    |
| `GET /staff/warehouse/products/`  | Warehouse product view |
| `GET /staff/warehouse/shipments/` | Warehouse shipments    |
| `GET /staff/sales/`               | Sales dashboard        |
| `GET /staff/sales/orders/`        | Sales orders           |
| `GET /staff/sales/customers/`     | Sales customers        |
| `GET /staff/sales/reviews/`       | Sales reviews          |

---

### Manager Pages (role: manager)

| URL                       | Description                |
| ------------------------- | -------------------------- |
| `GET /manager/dashboard/` | Manager dashboard + stats  |
| `GET /manager/staff/`     | Staff management (CRUD)    |
| `GET /manager/products/`  | Product management         |
| `GET /manager/orders/`    | All orders + status update |
| `GET /manager/payments/`  | Payment overview           |
| `GET /manager/shipments/` | Shipment tracking          |
| `GET /manager/reviews/`   | Review moderation          |
| `GET /manager/reports/`   | Reports & analytics        |
| `GET /manager/system/`    | System settings            |

---

## HTTP Status Codes

| Code                      | Meaning                       |
| ------------------------- | ----------------------------- |
| `200 OK`                  | Success                       |
| `201 Created`             | Resource created              |
| `204 No Content`          | Deleted successfully          |
| `400 Bad Request`         | Invalid request data          |
| `401 Unauthorized`        | Missing or invalid JWT        |
| `403 Forbidden`           | Insufficient role permissions |
| `404 Not Found`           | Resource not found            |
| `503 Service Unavailable` | Downstream microservice down  |

---

## Error Response Format

```json
{
  "error": "Description of the error"
}
```

or DRF default:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Health Check

### GET `/health/`

Check if API Gateway is running.

**Response:**

```json
{ "status": "ok" }
```
