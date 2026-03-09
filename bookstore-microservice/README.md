# BookStore Microservice (Django)

He thong gom day du cac microservice theo tai lieu:

- customer-service
- book-service
- cart-service
- api-gateway
- staff-service
- manager-service
- catalog-service
- order-service
- ship-service
- pay-service
- comment-rate-service
- recommender-ai-service

## Chay bang Docker

```bash
docker compose up --build
```

## Endpoint nhanh

- API Gateway: `http://localhost:8000/`
- Customer service: `http://localhost:8001/customers/`
- Register: `POST http://localhost:8001/auth/register/`
- Login (JWT): `POST http://localhost:8001/auth/login/`
- Book service: `http://localhost:8002/books/`
- Cart create: `POST http://localhost:8003/carts/`
- Cart add item: `POST http://localhost:8003/carts/items/`
- Cart view theo customer: `GET http://localhost:8003/carts/<customer_id>/`
- Staff service: `http://localhost:8004/staffs/`
- Manager dashboard: `http://localhost:8005/manager/dashboard/`
- Catalog service: `http://localhost:8006/products/`
- Order service: `http://localhost:8007/orders/`
- Ship service: `http://localhost:8008/shipments/`
- Pay service: `http://localhost:8009/payments/`
- Comment-rate service: `http://localhost:8010/reviews/`
- Recommender service: `http://localhost:8011/recommendations/<customer_id>/`

## Giao dien web (api-gateway)

Sau khi chay docker, mo cac trang sau:

- Dashboard: `http://localhost:8000/`
- Login: `http://localhost:8000/login/`
- Register: `http://localhost:8000/register/`
- Books UI: `http://localhost:8000/books/`
- Customers UI: `http://localhost:8000/customers/`
- Cart UI: `http://localhost:8000/cart/`
- Staff UI: `http://localhost:8000/staff/`
- Catalog UI: `http://localhost:8000/catalog/`
- Orders UI (kem payment/shipment theo order): `http://localhost:8000/orders/`
- Reviews UI: `http://localhost:8000/reviews/`
- Recommender UI: `http://localhost:8000/recommender/`
- Manager Dashboard UI: `http://localhost:8000/manager-dashboard/`

Ghi chu:

- Giao dien luu JWT trong session cua gateway.
- Chuc nang hien/cho phep theo role (`manager/staff/customer`).
- Form them item vao gio hien tai can `cart id` theo thiet ke endpoint cua `cart-service`.

## JWT va Role

Role ho tro: `manager`, `staff`, `customer`.

- `book-service`
  - `GET /books/`: can token hop le (tat ca role)
  - `POST /books/`: chi `manager` hoac `staff`
- `cart-service`
  - `POST /carts/`: `manager/staff` hoac internal token (duoc customer-service dung)
  - `POST /carts/items/`: `manager/staff/customer`
  - `GET /carts/<customer_id>/`: `manager/staff/customer`
- `customer-service`
  - `GET/POST /customers/`: `manager/staff`
  - `POST /auth/register/`, `POST /auth/login/`: public

### Vi du register

```bash
curl -X POST http://localhost:8001/auth/register/ \
	-H "Content-Type: application/json" \
	-d '{
		"username":"manager1",
		"password":"secret123",
		"email":"manager1@example.com",
		"name":"Manager One",
		"role":"manager"
	}'
```

### Vi du login

```bash
curl -X POST http://localhost:8001/auth/login/ \
	-H "Content-Type: application/json" \
	-d '{"username":"manager1","password":"secret123"}'
```

Lay `access` token tra ve va truyen vao header:

```bash
Authorization: Bearer <access_token>
```

## Luong co ban

1. Tao customer qua customer-service.
2. customer-service goi cart-service de tao gio hang.
3. Tao book qua book-service.
4. Them book vao gio qua cart-service.
5. Mo API gateway de xem danh sach sach.

## Luong dat hang moi

1. Tao don tai `order-service` qua `POST /orders/`.
2. `order-service` tu dong goi `pay-service` tao giao dich.
3. `order-service` tu dong goi `ship-service` tao van don.
4. `manager-service` tong hop so lieu tu staff/order/payment/shipment/catalog/review.
