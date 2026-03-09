import base64
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
import requests

CUSTOMER_SERVICE_URL = "http://customer-service:8000"
BOOK_SERVICE_URL = "http://book-service:8000"
CART_SERVICE_URL = "http://cart-service:8000"
STAFF_SERVICE_URL = "http://staff-service:8000"
MANAGER_SERVICE_URL = "http://manager-service:8000"
CATALOG_SERVICE_URL = "http://catalog-service:8000"
ORDER_SERVICE_URL = "http://order-service:8000"
SHIP_SERVICE_URL = "http://ship-service:8000"
PAY_SERVICE_URL = "http://pay-service:8000"
COMMENT_RATE_SERVICE_URL = "http://comment-rate-service:8000"
RECOMMENDER_SERVICE_URL = "http://recommender-ai-service:8000"
LOGIN_TEMPLATE = "auth_login.html"
REGISTER_TEMPLATE = "auth_register.html"
CART_UNAVAILABLE_MESSAGE = "Cart service is unavailable."


def _decode_jwt_payload(token):
    try:
        payload_segment = token.split(".")[1]
        padding = "=" * (-len(payload_segment) % 4)
        decoded = base64.urlsafe_b64decode(payload_segment + padding)
        return json.loads(decoded.decode("utf-8"))
    except (IndexError, ValueError):
        return {}


def _auth_headers(request):
    token = request.session.get("access_token")
    if not token:
        return None
    return {"Authorization": f"Bearer {token}"}


def _session_user(request):
    return {
        "is_authenticated": bool(request.session.get("access_token")),
        "username": request.session.get("username"),
        "role": request.session.get("role"),
        "customer_id": request.session.get("customer_id"),
    }


def _login_required(request):
    if not request.session.get("access_token"):
        messages.warning(request, "Please login first.")
        return redirect("login")
    return None


def _is_role(request, roles):
    return request.session.get("role") in roles


def home(request):
    if not request.session.get("access_token"):
        return redirect("login")
    return render(request, "home.html", {"session_user": _session_user(request)})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        try:
            resp = requests.post(
                f"{CUSTOMER_SERVICE_URL}/auth/login/",
                json={"username": username, "password": password},
                timeout=5,
            )
            data = resp.json()
        except requests.RequestException:
            messages.error(request, "Auth service is unavailable.")
            return render(request, LOGIN_TEMPLATE, {})
        except ValueError:
            data = {}

        if resp.status_code != 200:
            messages.error(request, data.get("detail", "Invalid username or password."))
            return render(request, LOGIN_TEMPLATE, {})

        payload = _decode_jwt_payload(data.get("access", ""))
        request.session["access_token"] = data.get("access")
        request.session["refresh_token"] = data.get("refresh")
        request.session["role"] = payload.get("role")
        request.session["customer_id"] = payload.get("customer_id")
        request.session["username"] = payload.get("username") or username
        messages.success(request, "Login successful.")
        return redirect("home")

    return render(request, LOGIN_TEMPLATE, {})


def register_view(request):
    if request.method == "POST":
        payload = {
            "username": request.POST.get("username", "").strip(),
            "password": request.POST.get("password", ""),
            "email": request.POST.get("email", "").strip(),
            "name": request.POST.get("name", "").strip(),
            "role": request.POST.get("role", "customer"),
        }
        try:
            resp = requests.post(
                f"{CUSTOMER_SERVICE_URL}/auth/register/",
                json=payload,
                timeout=5,
            )
            data = resp.json()
        except requests.RequestException:
            messages.error(request, "Register failed because auth service is unavailable.")
            return render(request, REGISTER_TEMPLATE, {})
        except ValueError:
            data = {}

        if resp.status_code != 201:
            messages.error(request, data.get("error", "Register failed."))
            return render(request, REGISTER_TEMPLATE, {})

        messages.success(request, "Register successful. Please login.")
        return redirect("login")

    return render(request, REGISTER_TEMPLATE, {})


def logout_view(request):
    request.session.flush()
    messages.info(request, "You are logged out.")
    return redirect("login")


def books_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)
    role = request.session.get("role")
    can_create = role in {"manager", "staff"}

    if request.method == "POST":
        if not can_create:
            messages.error(request, "Only manager/staff can add books.")
            return redirect("books")

        payload = {
            "title": request.POST.get("title", "").strip(),
            "author": request.POST.get("author", "").strip(),
            "price": request.POST.get("price", "0").strip(),
            "stock": request.POST.get("stock", "0").strip(),
        }
        try:
            resp = requests.post(f"{BOOK_SERVICE_URL}/books/", json=payload, headers=headers, timeout=5)
        except requests.RequestException:
            messages.error(request, "Book service is unavailable.")
            return redirect("books")

        if resp.status_code == 201:
            messages.success(request, "Book created.")
        else:
            try:
                err = resp.json()
            except ValueError:
                err = {}
            messages.error(request, f"Create book failed: {err}")
        return redirect("books")

    books = []
    try:
        r = requests.get(f"{BOOK_SERVICE_URL}/books/", headers=headers, timeout=5)
        r.raise_for_status()
        books = r.json()
    except requests.RequestException:
        messages.error(request, "Cannot load books from book-service.")

    return render(
        request,
        "books.html",
        {
            "books": books,
            "session_user": _session_user(request),
            "can_create": can_create,
        },
    )


def customers_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    role = request.session.get("role")
    if role not in {"manager", "staff"}:
        messages.error(request, "Only manager/staff can manage customers.")
        return redirect("home")

    headers = _auth_headers(request)

    if request.method == "POST":
        payload = {
            "name": request.POST.get("name", "").strip(),
            "email": request.POST.get("email", "").strip(),
        }
        try:
            resp = requests.post(
                f"{CUSTOMER_SERVICE_URL}/customers/",
                json=payload,
                headers=headers,
                timeout=5,
            )
            if resp.status_code in {200, 201}:
                messages.success(request, "Customer created.")
            else:
                messages.error(request, f"Create customer failed: {resp.text}")
        except requests.RequestException:
            messages.error(request, "Customer service is unavailable.")
        return redirect("customers")

    customers = []
    try:
        resp = requests.get(f"{CUSTOMER_SERVICE_URL}/customers/", headers=headers, timeout=5)
        if resp.status_code == 200:
            customers = resp.json()
        else:
            messages.error(request, f"Cannot load customers: {resp.text}")
    except requests.RequestException:
        messages.error(request, "Customer service is unavailable.")

    return render(
        request,
        "customers.html",
        {
            "customers": customers,
            "session_user": _session_user(request),
        },
    )


def _handle_create_cart(request, headers):
    payload = {"customer_id": request.POST.get("customer_id")}
    try:
        resp = requests.post(f"{CART_SERVICE_URL}/carts/", json=payload, headers=headers, timeout=5)
        if resp.status_code == 201:
            messages.success(request, "Cart created.")
        else:
            messages.error(request, f"Create cart failed: {resp.text}")
    except requests.RequestException:
        messages.error(request, CART_UNAVAILABLE_MESSAGE)


def _handle_add_item(request, headers):
    payload = {
        "cart": request.POST.get("cart"),
        "book_id": request.POST.get("book_id"),
        "quantity": request.POST.get("quantity", "1"),
    }
    try:
        resp = requests.post(f"{CART_SERVICE_URL}/carts/items/", json=payload, headers=headers, timeout=5)
        if resp.status_code == 201:
            messages.success(request, "Item added to cart.")
        else:
            messages.error(request, f"Add item failed: {resp.text}")
    except requests.RequestException:
        messages.error(request, CART_UNAVAILABLE_MESSAGE)


def _load_cart_items(request, headers, customer_id):
    if not customer_id:
        return []
    try:
        resp = requests.get(
            f"{CART_SERVICE_URL}/carts/{customer_id}/",
            headers=headers,
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
        messages.warning(request, f"Cannot load cart: {resp.text}")
        return []
    except requests.RequestException:
        messages.error(request, CART_UNAVAILABLE_MESSAGE)
        return []


def _load_books(headers):
    try:
        resp = requests.get(f"{BOOK_SERVICE_URL}/books/", headers=headers, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        return []
    return []


def cart_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    role = request.session.get("role")
    session_customer_id = request.session.get("customer_id")
    headers = _auth_headers(request)

    selected_customer_id = request.GET.get("customer_id") or session_customer_id
    if role == "customer":
        selected_customer_id = session_customer_id

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create_cart":
            if role not in {"manager", "staff"}:
                messages.error(request, "Only manager/staff can create cart manually.")
                return redirect("cart")
            _handle_create_cart(request, headers)
            return redirect("cart")

        if action == "add_item":
            _handle_add_item(request, headers)
            if selected_customer_id:
                return redirect(f"/cart/?customer_id={selected_customer_id}")
            return redirect("cart")

    cart_items = _load_cart_items(request, headers, selected_customer_id)
    books = _load_books(headers)

    return render(
        request,
        "cart.html",
        {
            "session_user": _session_user(request),
            "selected_customer_id": selected_customer_id,
            "cart_items": cart_items,
            "books": books,
            "can_create_cart": role in {"manager", "staff"},
        },
    )


def staff_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)
    if request.method == "POST":
        if not _is_role(request, {"manager"}):
            messages.error(request, "Only manager can create staff users.")
            return redirect("staff")
        payload = {
            "name": request.POST.get("name", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "role": request.POST.get("role", "support").strip(),
        }
        try:
            resp = requests.post(f"{STAFF_SERVICE_URL}/staffs/", json=payload, headers=headers, timeout=5)
            if resp.status_code == 201:
                messages.success(request, "Staff created.")
            else:
                messages.error(request, f"Create staff failed: {resp.text}")
        except requests.RequestException:
            messages.error(request, "Staff service is unavailable.")
        return redirect("staff")

    staffs = []
    try:
        resp = requests.get(f"{STAFF_SERVICE_URL}/staffs/", headers=headers, timeout=5)
        if resp.status_code == 200:
            staffs = resp.json()
        else:
            messages.error(request, f"Cannot load staff list: {resp.text}")
    except requests.RequestException:
        messages.error(request, "Staff service is unavailable.")

    return render(
        request,
        "staff.html",
        {
            "session_user": _session_user(request),
            "staffs": staffs,
            "can_create": _is_role(request, {"manager"}),
        },
    )


def catalog_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)
    if request.method == "POST":
        if not _is_role(request, {"manager", "staff"}):
            messages.error(request, "Only manager/staff can create catalog products.")
            return redirect("catalog")
        payload = {
            "name": request.POST.get("name", "").strip(),
            "description": request.POST.get("description", "").strip(),
            "price": request.POST.get("price", "0").strip(),
            "stock": request.POST.get("stock", "0").strip(),
            "image_url": request.POST.get("image_url", "").strip(),
        }
        try:
            resp = requests.post(f"{CATALOG_SERVICE_URL}/products/", json=payload, headers=headers, timeout=5)
            if resp.status_code == 201:
                messages.success(request, "Catalog product created.")
            else:
                messages.error(request, f"Create product failed: {resp.text}")
        except requests.RequestException:
            messages.error(request, "Catalog service is unavailable.")
        return redirect("catalog")

    products = []
    try:
        resp = requests.get(f"{CATALOG_SERVICE_URL}/products/", headers=headers, timeout=5)
        if resp.status_code == 200:
            products = resp.json()
        else:
            messages.error(request, f"Cannot load products: {resp.text}")
    except requests.RequestException:
        messages.error(request, "Catalog service is unavailable.")

    return render(
        request,
        "catalog.html",
        {
            "session_user": _session_user(request),
            "products": products,
            "can_create": _is_role(request, {"manager", "staff"}),
        },
    )


def reviews_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)
    if request.method == "POST":
        customer_id = request.session.get("customer_id") or request.POST.get("customer_id")
        payload = {
            "customer_id": customer_id,
            "product_id": request.POST.get("product_id", "").strip(),
            "rating": request.POST.get("rating", "5").strip(),
            "comment": request.POST.get("comment", "").strip(),
        }
        try:
            resp = requests.post(f"{COMMENT_RATE_SERVICE_URL}/reviews/", json=payload, headers=headers, timeout=5)
            if resp.status_code == 201:
                messages.success(request, "Review submitted.")
            else:
                messages.error(request, f"Submit review failed: {resp.text}")
        except requests.RequestException:
            messages.error(request, "Comment-rate service is unavailable.")
        return redirect("reviews")

    reviews = []
    try:
        resp = requests.get(f"{COMMENT_RATE_SERVICE_URL}/reviews/", headers=headers, timeout=5)
        if resp.status_code == 200:
            reviews = resp.json()
        else:
            messages.error(request, f"Cannot load reviews: {resp.text}")
    except requests.RequestException:
        messages.error(request, "Comment-rate service is unavailable.")

    return render(
        request,
        "reviews.html",
        {
            "session_user": _session_user(request),
            "reviews": reviews,
        },
    )


def _create_order(request, headers):
    customer_id = request.session.get("customer_id") or request.POST.get("customer_id")
    payload = {
        "customer_id": customer_id,
        "shipping_address": request.POST.get("shipping_address", "").strip(),
        "status": request.POST.get("status", "pending").strip(),
        "total_amount": request.POST.get("total_amount", "0").strip(),
    }
    try:
        resp = requests.post(f"{ORDER_SERVICE_URL}/orders/", json=payload, headers=headers, timeout=8)
        if resp.status_code == 201:
            messages.success(request, "Order created.")
        else:
            messages.error(request, f"Create order failed: {resp.text}")
    except requests.RequestException:
        messages.error(request, "Order service is unavailable.")


def _load_orders(request, headers):
    try:
        resp = requests.get(f"{ORDER_SERVICE_URL}/orders/", headers=headers, timeout=5)
        if resp.status_code == 200:
            orders = resp.json()
        else:
            messages.error(request, f"Cannot load orders: {resp.text}")
            orders = []
    except requests.RequestException:
        messages.error(request, "Order service is unavailable.")
        orders = []

    if request.session.get("role") == "customer":
        cid = request.session.get("customer_id")
        return [o for o in orders if str(o.get("customer_id")) == str(cid)]
    return orders


def _load_order_ops(request, headers, selected_order_id):
    payments = []
    shipments = []
    if not selected_order_id:
        return payments, shipments

    try:
        payment_resp = requests.get(
            f"{PAY_SERVICE_URL}/payments/order/{selected_order_id}/",
            headers=headers,
            timeout=5,
        )
        if payment_resp.status_code == 200:
            payments = payment_resp.json()
    except requests.RequestException:
        messages.warning(request, "Cannot load payments for selected order.")

    try:
        ship_resp = requests.get(
            f"{SHIP_SERVICE_URL}/shipments/order/{selected_order_id}/",
            headers=headers,
            timeout=5,
        )
        if ship_resp.status_code == 200:
            shipments = ship_resp.json()
    except requests.RequestException:
        messages.warning(request, "Cannot load shipments for selected order.")

    return payments, shipments


def orders_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)
    if request.method == "POST":
        _create_order(request, headers)
        return redirect("orders")

    orders = _load_orders(request, headers)
    selected_order_id = request.GET.get("order_id")
    payments, shipments = _load_order_ops(request, headers, selected_order_id)

    return render(
        request,
        "orders.html",
        {
            "session_user": _session_user(request),
            "orders": orders,
            "selected_order_id": selected_order_id,
            "payments": payments,
            "shipments": shipments,
        },
    )


def manager_dashboard_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    if not _is_role(request, {"manager"}):
        messages.error(request, "Only manager can access this dashboard.")
        return redirect("home")

    headers = _auth_headers(request)
    stats = {}
    try:
        resp = requests.get(f"{MANAGER_SERVICE_URL}/manager/dashboard/", headers=headers, timeout=5)
        if resp.status_code == 200:
            stats = resp.json()
        else:
            messages.error(request, f"Cannot load manager dashboard: {resp.text}")
    except requests.RequestException:
        messages.error(request, "Manager service is unavailable.")

    return render(
        request,
        "manager_dashboard.html",
        {
            "session_user": _session_user(request),
            "stats": stats,
        },
    )


def recommender_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)
    customer_id = request.GET.get("customer_id") or request.session.get("customer_id")
    recommendations = {}
    if customer_id:
        try:
            resp = requests.get(
                f"{RECOMMENDER_SERVICE_URL}/recommendations/{customer_id}/",
                headers=headers,
                timeout=6,
            )
            if resp.status_code == 200:
                recommendations = resp.json()
            else:
                messages.error(request, f"Cannot load recommendations: {resp.text}")
        except requests.RequestException:
            messages.error(request, "Recommender service is unavailable.")

    return render(
        request,
        "recommender.html",
        {
            "session_user": _session_user(request),
            "selected_customer_id": customer_id,
            "recommendations": recommendations,
        },
    )


def health(_request):
    return JsonResponse({"status": "ok"})
