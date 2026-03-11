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
        "staff_position": request.session.get("staff_position"),
    }


def _login_required(request):
    if not request.session.get("access_token"):
        messages.warning(request, "Please login first.")
        return redirect("login")


def _safe_json(resp):
    """Return (data, error_response) from a requests.Response.
    Handles cases where the downstream service returns non-JSON (e.g. HTML 500 page).
    """
    try:
        return resp.json(), None
    except Exception:
        return None, JsonResponse(
            {"error": f"Service returned non-JSON response (HTTP {resp.status_code})"},
            status=502,
        )
    return None


def _is_role(request, roles):
    return request.session.get("role") in roles


def landing_page(request):
    """Landing page - shows public books and 5-star reviews"""
    books = []
    star_reviews = []
    book_map = {}
    try:
        b_resp = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
        if b_resp.status_code == 200:
            all_books = b_resp.json()
            book_map = {b['id']: b for b in all_books}
            books = all_books[:8]
    except Exception:
        pass
    try:
        r_resp = requests.get(f"{COMMENT_RATE_SERVICE_URL}/reviews/", timeout=5)
        if r_resp.status_code == 200:
            all_reviews = r_resp.json()
            for r in all_reviews:
                if r.get('rating') == 5:
                    book = book_map.get(r.get('product_id'))
                    r['book_title'] = book['title'] if book else f"Sách #{r.get('product_id')}"
                    star_reviews.append(r)
                    if len(star_reviews) >= 6:
                        break
    except Exception:
        pass
    return render(request, "landing.html", {"books": books, "star_reviews": star_reviews})


def home(request):
    if not request.session.get("access_token"):
        return redirect("landing")
    
    # Redirect to appropriate dashboard based on role
    role = request.session.get("role")
    if role == "customer":
        return redirect("customer_dashboard")
    elif role == "staff":
        return redirect("staff_dashboard")
    elif role == "manager":
        return redirect("manager_dashboard_new")
    
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

        return redirect("home")

    return render(request, LOGIN_TEMPLATE, {})


def register_view(request):
    if request.method == "POST":
        payload = {
            "username": request.POST.get("username", "").strip(),
            "password": request.POST.get("password", ""),
            "email": request.POST.get("email", "").strip(),
            "name": request.POST.get("name", "").strip(),
            "role": "customer",  # Force role to customer for public registration
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
    messages.success(request, "Đã đăng xuất thành công. Hẹn gặp lại!")
    return redirect("landing")


# Book views - separated into list, create, and update
def book_list_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)
    role = request.session.get("role")
    can_create = role in {"manager", "staff"}

    books = []
    try:
        r = requests.get(f"{BOOK_SERVICE_URL}/books/", headers=headers, timeout=5)
        r.raise_for_status()
        books = r.json()
    except requests.RequestException:
        messages.error(request, "Cannot load books from book-service.")

    return render(
        request,
        "book_list.html",
        {
            "books": books,
            "session_user": _session_user(request),
            "can_create": can_create,
        },
    )


def book_create_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    role = request.session.get("role")
    if role not in {"manager", "staff"}:
        messages.error(request, "Only manager/staff can add books.")
        return redirect("book_list")

    if request.method == "POST":
        headers = _auth_headers(request)
        payload = {
            "title": request.POST.get("title", "").strip(),
            "author": request.POST.get("author", "").strip(),
            "image_url": request.POST.get("image_url", "").strip(),
            "price": request.POST.get("price", "0").strip(),
            "stock": request.POST.get("stock", "0").strip(),
        }
        try:
            resp = requests.post(f"{BOOK_SERVICE_URL}/books/", json=payload, headers=headers, timeout=5)
            if resp.status_code == 201:
                messages.success(request, "Book created successfully.")
                return redirect("book_list")
            else:
                try:
                    err = resp.json()
                except ValueError:
                    err = {}
                messages.error(request, f"Create book failed: {err}")
        except requests.RequestException:
            messages.error(request, "Book service is unavailable.")

    return render(request, "book_create.html", {"session_user": _session_user(request)})


def book_update_view(request, book_id):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    role = request.session.get("role")
    if role not in {"manager", "staff"}:
        messages.error(request, "Only manager/staff can update books.")
        return redirect("book_list")

    headers = _auth_headers(request)

    # Get book details
    book = None
    try:
        resp = requests.get(f"{BOOK_SERVICE_URL}/books/{book_id}/", headers=headers, timeout=5)
        if resp.status_code == 200:
            book = resp.json()
        else:
            messages.error(request, "Book not found.")
            return redirect("book_list")
    except requests.RequestException:
        messages.error(request, "Book service is unavailable.")
        return redirect("book_list")

    if request.method == "POST":
        payload = {
            "title": request.POST.get("title", "").strip(),
            "author": request.POST.get("author", "").strip(),
            "image_url": request.POST.get("image_url", "").strip(),
            "price": request.POST.get("price", "0").strip(),
            "stock": request.POST.get("stock", "0").strip(),
        }
        try:
            resp = requests.put(f"{BOOK_SERVICE_URL}/books/{book_id}/", json=payload, headers=headers, timeout=5)
            if resp.status_code == 200:
                messages.success(request, "Book updated successfully.")
                return redirect("book_list")
            else:
                messages.error(request, f"Update book failed: {resp.text}")
        except requests.RequestException:
            messages.error(request, "Book service is unavailable.")

    return render(request, "book_update.html", {"session_user": _session_user(request), "book": book})


# Customer views - separated into list and create
def customer_list_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    role = request.session.get("role")
    if role not in {"manager", "staff"}:
        messages.error(request, "Only manager/staff can manage customers.")
        return redirect("home")

    headers = _auth_headers(request)
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
        "customer_list.html",
        {
            "customers": customers,
            "session_user": _session_user(request),
        },
    )


def customer_create_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    role = request.session.get("role")
    if role not in {"manager", "staff"}:
        messages.error(request, "Only manager/staff can create customers.")
        return redirect("home")

    if request.method == "POST":
        headers = _auth_headers(request)
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
                messages.success(request, "Customer created successfully.")
                return redirect("customer_list")
            else:
                messages.error(request, f"Create customer failed: {resp.text}")
        except requests.RequestException:
            messages.error(request, "Customer service is unavailable.")

    return render(request, "customer_create.html", {"session_user": _session_user(request)})


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


# Cart views - separated for clarity
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

    cart_items = _load_cart_items(request, headers, selected_customer_id)

    return render(
        request,
        "cart_view.html",
        {
            "session_user": _session_user(request),
            "selected_customer_id": selected_customer_id,
            "cart_items": cart_items,
        },
    )


def cart_add_item_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)

    if request.method == "POST":
        payload = {
            "cart": request.POST.get("cart"),
            "book_id": request.POST.get("book_id"),
            "quantity": request.POST.get("quantity", "1"),
        }
        try:
            resp = requests.post(f"{CART_SERVICE_URL}/carts/items/", json=payload, headers=headers, timeout=5)
            if resp.status_code == 201:
                messages.success(request, "Item added to cart successfully.")
                return redirect("cart_view")
            else:
                messages.error(request, f"Add item failed: {resp.text}")
        except requests.RequestException:
            messages.error(request, CART_UNAVAILABLE_MESSAGE)

    books = _load_books(headers)
    return render(request, "cart_add_item.html", {"session_user": _session_user(request), "books": books})


# Staff views - separated into list and create
def staff_list_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)
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
        "staff_list.html",
        {
            "session_user": _session_user(request),
            "staffs": staffs,
            "can_create": _is_role(request, {"manager"}),
        },
    )


def staff_create_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    if not _is_role(request, {"manager"}):
        messages.error(request, "Only manager can create staff users.")
        return redirect("staff_list")

    if request.method == "POST":
        headers = _auth_headers(request)
        payload = {
            "username": request.POST.get("username", "").strip(),
            "name": request.POST.get("name", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "password": request.POST.get("password", "").strip(),
            "department": "Nhân viên",
            "position": "Nhân viên",
        }
        try:
            resp = requests.post(f"{STAFF_SERVICE_URL}/staffs/", json=payload, headers=headers, timeout=5)
            if resp.status_code == 201:
                messages.success(request, "Staff created successfully.")
                return redirect("staff_list")
            else:
                messages.error(request, f"Create staff failed: {resp.text}")
        except requests.RequestException:
            messages.error(request, "Staff service is unavailable.")

    return render(request, "staff_create.html", {"session_user": _session_user(request)})


# Catalog views - separated into list and create
def catalog_list_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)
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
        "catalog_list.html",
        {
            "session_user": _session_user(request),
            "products": products,
            "can_create": _is_role(request, {"manager", "staff"}),
        },
    )


def catalog_create_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    if not _is_role(request, {"manager", "staff"}):
        messages.error(request, "Only manager/staff can create catalog products.")
        return redirect("catalog_list")

    if request.method == "POST":
        headers = _auth_headers(request)
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
                messages.success(request, "Catalog product created successfully.")
                return redirect("catalog_list")
            else:
                messages.error(request, f"Create product failed: {resp.text}")
        except requests.RequestException:
            messages.error(request, "Catalog service is unavailable.")

    return render(request, "catalog_create.html", {"session_user": _session_user(request)})


# Review views - separated into list and create
def review_list_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)
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
        "review_list.html",
        {
            "session_user": _session_user(request),
            "reviews": reviews,
        },
    )


def review_create_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    if request.method == "POST":
        headers = _auth_headers(request)
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
                messages.success(request, "Review submitted successfully.")
                return redirect("review_list")
            else:
                messages.error(request, f"Submit review failed: {resp.text}")
        except requests.RequestException:
            messages.error(request, "Comment-rate service is unavailable.")

    return render(request, "review_create.html", {"session_user": _session_user(request)})


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


# Order views - separated into create, list, and detail
def order_create_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    if request.method == "POST":
        headers = _auth_headers(request)
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
                messages.success(request, "Order created successfully.")
                return redirect("order_list")
            else:
                messages.error(request, f"Create order failed: {resp.text}")
        except requests.RequestException:
            messages.error(request, "Order service is unavailable.")

    return render(request, "order_create.html", {"session_user": _session_user(request)})


def order_list_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)
    orders = _load_orders(request, headers)

    return render(
        request,
        "order_list.html",
        {
            "session_user": _session_user(request),
            "orders": orders,
        },
    )


def order_detail_view(request, order_id):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    headers = _auth_headers(request)
    payments, shipments = _load_order_ops(request, headers, order_id)

    return render(
        request,
        "order_detail.html",
        {
            "session_user": _session_user(request),
            "order_id": order_id,
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


# ========== NEW ROLE-BASED DASHBOARD VIEWS ==========

# Customer Dashboard & Pages
def customer_dashboard_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"customer"}):
        messages.error(request, "Customer access only.")
        return redirect("home")
    
    return render(request, "customer_dashboard.html", {"session_user": _session_user(request)})


def customer_products_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"customer"}):
        messages.error(request, "Customer access only.")
        return redirect("home")
    
    return render(request, "customer_products.html", {"session_user": _session_user(request)})


def customer_cart_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"customer"}):
        messages.error(request, "Customer access only.")
        return redirect("home")
    
    return render(request, "customer_cart.html", {"session_user": _session_user(request)})


def customer_orders_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"customer"}):
        messages.error(request, "Customer access only.")
        return redirect("home")
    
    return render(request, "customer_orders.html", {"session_user": _session_user(request)})


def customer_profile_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"customer"}):
        messages.error(request, "Customer access only.")
        return redirect("home")
    
    return render(request, "customer_profile.html", {"session_user": _session_user(request)})


def customer_reviews_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    if not _is_role(request, {"customer"}):
        messages.error(request, "Customer access only.")
        return redirect("home")

    return render(request, "customer_reviews.html", {"session_user": _session_user(request)})


def customer_recommendations_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect

    if not _is_role(request, {"customer"}):
        messages.error(request, "Customer access only.")
        return redirect("home")

    return render(request, "customer_recommendations.html", {"session_user": _session_user(request)})


# Staff Dashboard & Pages
def staff_dashboard_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Staff or manager access only.")
        return redirect("home")
    
    return render(request, "staff_dashboard.html", {"session_user": _session_user(request)})


def staff_products_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Staff or manager access only.")
        return redirect("home")
    
    return render(request, "staff_products.html", {"session_user": _session_user(request)})


def staff_orders_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Staff or manager access only.")
        return redirect("home")
    
    return render(request, "staff_orders.html", {"session_user": _session_user(request)})


def staff_inventory_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Staff or manager access only.")
        return redirect("home")
    return render(request, "staff_inventory.html", {"session_user": _session_user(request)})


def staff_shipments_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Staff or manager access only.")
        return redirect("home")
    return render(request, "staff_shipments.html", {"session_user": _session_user(request)})


def staff_customers_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Staff or manager access only.")
        return redirect("home")
    return render(request, "staff_customers.html", {"session_user": _session_user(request)})


def staff_reviews_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Staff or manager access only.")
        return redirect("home")
    return render(request, "staff_reviews.html", {"session_user": _session_user(request)})


# =============== WAREHOUSE STAFF VIEWS (kept for backward compat) ===============
def warehouse_dashboard_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Chỉ nhân viên kho được phép truy cập.")
        return redirect("home")
    return render(request, "warehouse_dashboard.html", {"session_user": _session_user(request)})


def warehouse_products_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Chỉ nhân viên kho được phép truy cập.")
        return redirect("home")
    return render(request, "warehouse_products.html", {"session_user": _session_user(request)})


def warehouse_shipments_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Chỉ nhân viên kho được phép truy cập.")
        return redirect("home")
    return render(request, "warehouse_shipments.html", {"session_user": _session_user(request)})


# =============== SALES STAFF VIEWS ===============
def sales_dashboard_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Chỉ nhân viên bán hàng được phép truy cập.")
        return redirect("home")
    return render(request, "sales_dashboard.html", {"session_user": _session_user(request)})


def sales_orders_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Chỉ nhân viên bán hàng được phép truy cập.")
        return redirect("home")
    return render(request, "sales_orders.html", {"session_user": _session_user(request)})


def sales_customers_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Chỉ nhân viên bán hàng được phép truy cập.")
        return redirect("home")
    return render(request, "sales_customers.html", {"session_user": _session_user(request)})


def sales_reviews_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    if not _is_role(request, {"staff", "manager"}):
        messages.error(request, "Chỉ nhân viên bán hàng được phép truy cập.")
        return redirect("home")
    return render(request, "sales_reviews.html", {"session_user": _session_user(request)})


# Manager Dashboard & Pages
def manager_dashboard_new_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"manager"}):
        messages.error(request, "Manager access only.")
        return redirect("home")
    
    return render(request, "manager_dashboard_new.html", {"session_user": _session_user(request)})


def manager_staff_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"manager"}):
        messages.error(request, "Manager access only.")
        return redirect("home")
    
    return render(request, "manager_staff.html", {"session_user": _session_user(request)})


def manager_reports_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"manager"}):
        messages.error(request, "Manager access only.")
        return redirect("home")
    
    return render(request, "manager_reports.html", {"session_user": _session_user(request)})


def manager_products_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"manager"}):
        messages.error(request, "Manager access only.")
        return redirect("home")
    
    return render(request, "manager_products.html", {"session_user": _session_user(request)})


def manager_orders_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"manager"}):
        messages.error(request, "Manager access only.")
        return redirect("home")
    
    return render(request, "manager_orders.html", {"session_user": _session_user(request)})


def manager_payments_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"manager"}):
        messages.error(request, "Manager access only.")
        return redirect("home")
    
    return render(request, "manager_payments.html", {"session_user": _session_user(request)})


def manager_shipments_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"manager"}):
        messages.error(request, "Manager access only.")
        return redirect("home")
    
    return render(request, "manager_shipments.html", {"session_user": _session_user(request)})


def manager_reviews_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"manager"}):
        messages.error(request, "Manager access only.")
        return redirect("home")
    
    return render(request, "manager_reviews.html", {"session_user": _session_user(request)})


def manager_system_view(request):
    login_redirect = _login_required(request)
    if login_redirect:
        return login_redirect
    
    if not _is_role(request, {"manager"}):
        messages.error(request, "Manager access only.")
        return redirect("home")
    
    return render(request, "manager_system.html", {"session_user": _session_user(request)})


# API Proxy Endpoints for AJAX calls
def api_manager_dashboard(request):
    """Proxy for manager-service dashboard API"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    headers = _auth_headers(request)
    try:
        resp = requests.get(f"{MANAGER_SERVICE_URL}/dashboard/", headers=headers, timeout=5)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Manager service unavailable", "detail": str(e)}, status=503)


def api_books(request, book_id=None):
    """Proxy for book-service books API - supports GET, POST, PUT, PATCH, DELETE"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    headers = _auth_headers(request)

    try:
        if request.method == "GET":
            if book_id:
                resp = requests.get(f"{BOOK_SERVICE_URL}/books/{book_id}/", headers=headers, timeout=5)
            else:
                resp = requests.get(f"{BOOK_SERVICE_URL}/books/", headers=headers, timeout=5)

        elif request.method == "POST":
            payload = json.loads(request.body) if request.body else {}
            resp = requests.post(f"{BOOK_SERVICE_URL}/books/", json=payload, headers=headers, timeout=5)

        elif request.method in ["PUT", "PATCH"]:
            if not book_id:
                return JsonResponse({"error": "Book ID required"}, status=400)
            payload = json.loads(request.body) if request.body else {}
            method = requests.patch if request.method == "PATCH" else requests.put
            resp = method(f"{BOOK_SERVICE_URL}/books/{book_id}/", json=payload, headers=headers, timeout=5)

        elif request.method == "DELETE":
            if not book_id:
                return JsonResponse({"error": "Book ID required"}, status=400)
            resp = requests.delete(f"{BOOK_SERVICE_URL}/books/{book_id}/", headers=headers, timeout=5)

        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)

        if resp.status_code == 204:
            return JsonResponse({"success": True}, status=200)

        return JsonResponse(resp.json(), safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Book service unavailable", "detail": str(e)}, status=503)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def api_orders(request, order_id=None):
    """Proxy for order-service orders API"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    headers = _auth_headers(request)
    try:
        if request.method == "GET":
            if order_id:
                resp = requests.get(f"{ORDER_SERVICE_URL}/orders/{order_id}/", headers=headers, timeout=5)
            else:
                resp = requests.get(f"{ORDER_SERVICE_URL}/orders/", headers=headers, timeout=5)
        elif request.method == "POST":
            payload = json.loads(request.body) if request.body else {}
            resp = requests.post(f"{ORDER_SERVICE_URL}/orders/", json=payload, headers=headers, timeout=5)
        elif request.method in ["PUT", "PATCH"]:
            if not order_id:
                return JsonResponse({"error": "Order ID required"}, status=400)
            payload = json.loads(request.body) if request.body else {}
            method = requests.patch if request.method == "PATCH" else requests.put
            resp = method(f"{ORDER_SERVICE_URL}/orders/{order_id}/", json=payload, headers=headers, timeout=5)
        elif request.method == "DELETE":
            if not order_id:
                return JsonResponse({"error": "Order ID required"}, status=400)
            resp = requests.delete(f"{ORDER_SERVICE_URL}/orders/{order_id}/", headers=headers, timeout=5)
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)

        if resp.status_code == 204:
            return JsonResponse({"success": True}, status=200)
        data, err = _safe_json(resp)
        if err:
            return err
        return JsonResponse(data, safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Order service unavailable", "detail": str(e)}, status=503)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def api_payments(request):
    """Proxy for pay-service payments API"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    headers = _auth_headers(request)
    try:
        resp = requests.get(f"{PAY_SERVICE_URL}/payments/", headers=headers, timeout=5)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Payment service unavailable", "detail": str(e)}, status=503)


def api_staff(request, staff_id=None):
    """Proxy for staff-service staff API - supports GET, POST, PUT, PATCH, DELETE"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    headers = _auth_headers(request)
    
    try:
        if request.method == "GET":
            if staff_id:
                # Get single staff member
                resp = requests.get(f"{STAFF_SERVICE_URL}/staffs/{staff_id}/", headers=headers, timeout=5)
            else:
                # Get all staff
                resp = requests.get(f"{STAFF_SERVICE_URL}/staffs/", headers=headers, timeout=5)
        
        elif request.method == "POST":
            if not _is_role(request, {"manager"}):
                return JsonResponse({"error": "Only managers can create staff"}, status=403)
            payload = json.loads(request.body) if request.body else {}
            resp = requests.post(f"{STAFF_SERVICE_URL}/staffs/", json=payload, headers=headers, timeout=5)
        
        elif request.method in ["PUT", "PATCH"]:
            if not _is_role(request, {"manager"}):
                return JsonResponse({"error": "Only managers can update staff"}, status=403)
            payload = json.loads(request.body) if request.body else {}
            if not staff_id:
                return JsonResponse({"error": "Staff ID required"}, status=400)
            # Use same method as request (PUT or PATCH)
            method = requests.patch if request.method == "PATCH" else requests.put
            resp = method(f"{STAFF_SERVICE_URL}/staffs/{staff_id}/", json=payload, headers=headers, timeout=5)
        
        elif request.method == "DELETE":
            if not _is_role(request, {"manager"}):
                return JsonResponse({"error": "Only managers can delete staff"}, status=403)
            if not staff_id:
                return JsonResponse({"error": "Staff ID required"}, status=400)
            resp = requests.delete(f"{STAFF_SERVICE_URL}/staffs/{staff_id}/", headers=headers, timeout=5)
        
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)
        
        if resp.status_code == 204:  # DELETE success with no content
            return JsonResponse({"success": True}, status=200)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Staff service unavailable", "detail": str(e)}, status=503)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def api_carts(request, cart_id=None):
    """Proxy for cart-service carts API"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    headers = _auth_headers(request)
    try:
        if request.method == "GET":
            if cart_id:
                resp = requests.get(f"{CART_SERVICE_URL}/carts/{cart_id}/", headers=headers, timeout=5)
            else:
                resp = requests.get(f"{CART_SERVICE_URL}/carts/", headers=headers, timeout=5)
        elif request.method == "POST":
            payload = json.loads(request.body) if request.body else {}
            resp = requests.post(f"{CART_SERVICE_URL}/carts/", json=payload, headers=headers, timeout=5)
        elif request.method in ["PUT", "PATCH"]:
            payload = json.loads(request.body) if request.body else {}
            if not cart_id:
                return JsonResponse({"error": "Cart ID required"}, status=400)
            method = requests.patch if request.method == "PATCH" else requests.put
            resp = method(f"{CART_SERVICE_URL}/carts/{cart_id}/", json=payload, headers=headers, timeout=5)
        elif request.method == "DELETE":
            if not cart_id:
                return JsonResponse({"error": "Cart ID required"}, status=400)
            resp = requests.delete(f"{CART_SERVICE_URL}/carts/{cart_id}/", headers=headers, timeout=5)
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)
        
        if resp.status_code == 204:
            return JsonResponse({"success": True}, status=200)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Cart service unavailable", "detail": str(e)}, status=503)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def api_cart_items(request, item_id=None):
    """Proxy for cart-service cart-items API"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    headers = _auth_headers(request)
    try:
        if request.method == "GET":
            # Support query params like ?cart_id=123
            query_string = request.META.get('QUERY_STRING', '')
            url = f"{CART_SERVICE_URL}/cart-items/"
            if query_string:
                url += f"?{query_string}"
            resp = requests.get(url, headers=headers, timeout=5)
        elif request.method == "POST":
            payload = json.loads(request.body) if request.body else {}
            resp = requests.post(f"{CART_SERVICE_URL}/cart-items/", json=payload, headers=headers, timeout=5)
        elif request.method in ["PUT", "PATCH"]:
            payload = json.loads(request.body) if request.body else {}
            if not item_id:
                return JsonResponse({"error": "Item ID required"}, status=400)
            method = requests.patch if request.method == "PATCH" else requests.put
            resp = method(f"{CART_SERVICE_URL}/cart-items/{item_id}/", json=payload, headers=headers, timeout=5)
        elif request.method == "DELETE":
            if not item_id:
                return JsonResponse({"error": "Item ID required"}, status=400)
            resp = requests.delete(f"{CART_SERVICE_URL}/cart-items/{item_id}/", headers=headers, timeout=5)
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)
        
        if resp.status_code == 204:
            return JsonResponse({"success": True}, status=200)
        data, err = _safe_json(resp)
        if err:
            return err
        return JsonResponse(data, safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Cart service unavailable", "detail": str(e)}, status=503)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def api_products(request, product_id=None):
    """Proxy for catalog-service products API"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    headers = _auth_headers(request)
    try:
        if request.method == "GET":
            if product_id:
                resp = requests.get(f"{CATALOG_SERVICE_URL}/products/{product_id}/", headers=headers, timeout=5)
            else:
                resp = requests.get(f"{CATALOG_SERVICE_URL}/products/", headers=headers, timeout=5)
        elif request.method == "POST":
            if not _is_role(request, {"manager", "staff"}):
                return JsonResponse({"error": "Only staff/manager can create products"}, status=403)
            payload = json.loads(request.body) if request.body else {}
            resp = requests.post(f"{CATALOG_SERVICE_URL}/products/", json=payload, headers=headers, timeout=5)
        elif request.method in ["PUT", "PATCH"]:
            if not _is_role(request, {"manager", "staff"}):
                return JsonResponse({"error": "Only staff/manager can update products"}, status=403)
            payload = json.loads(request.body) if request.body else {}
            if not product_id:
                return JsonResponse({"error": "Product ID required"}, status=400)
            method = requests.patch if request.method == "PATCH" else requests.put
            resp = method(f"{CATALOG_SERVICE_URL}/products/{product_id}/", json=payload, headers=headers, timeout=5)
        elif request.method == "DELETE":
            if not _is_role(request, {"manager", "staff"}):
                return JsonResponse({"error": "Only staff/manager can delete products"}, status=403)
            if not product_id:
                return JsonResponse({"error": "Product ID required"}, status=400)
            resp = requests.delete(f"{CATALOG_SERVICE_URL}/products/{product_id}/", headers=headers, timeout=5)
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)
        
        if resp.status_code == 204:
            return JsonResponse({"success": True}, status=200)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Catalog service unavailable", "detail": str(e)}, status=503)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def api_shipments(request, shipment_id=None):
    """Proxy for ship-service shipments API"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    headers = _auth_headers(request)
    try:
        if request.method == "GET":
            if shipment_id:
                resp = requests.get(f"{SHIP_SERVICE_URL}/shipments/{shipment_id}/", headers=headers, timeout=5)
            else:
                resp = requests.get(f"{SHIP_SERVICE_URL}/shipments/", headers=headers, timeout=5)
        elif request.method == "POST":
            if not _is_role(request, {"manager", "staff"}):
                return JsonResponse({"error": "Only staff/manager can create shipments"}, status=403)
            payload = json.loads(request.body) if request.body else {}
            resp = requests.post(f"{SHIP_SERVICE_URL}/shipments/", json=payload, headers=headers, timeout=5)
        elif request.method in ["PUT", "PATCH"]:
            if not _is_role(request, {"manager", "staff"}):
                return JsonResponse({"error": "Only staff/manager can update shipments"}, status=403)
            payload = json.loads(request.body) if request.body else {}
            if not shipment_id:
                return JsonResponse({"error": "Shipment ID required"}, status=400)
            method = requests.patch if request.method == "PATCH" else requests.put
            resp = method(f"{SHIP_SERVICE_URL}/shipments/{shipment_id}/", json=payload, headers=headers, timeout=5)
        elif request.method == "DELETE":
            if not _is_role(request, {"manager", "staff"}):
                return JsonResponse({"error": "Only staff/manager can delete shipments"}, status=403)
            if not shipment_id:
                return JsonResponse({"error": "Shipment ID required"}, status=400)
            resp = requests.delete(f"{SHIP_SERVICE_URL}/shipments/{shipment_id}/", headers=headers, timeout=5)
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)
        
        if resp.status_code == 204:
            return JsonResponse({"success": True}, status=200)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Ship service unavailable", "detail": str(e)}, status=503)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def api_reviews(request, review_id=None):
    """Proxy for comment-rate-service reviews API"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    headers = _auth_headers(request)
    try:
        if request.method == "GET":
            if review_id:
                resp = requests.get(f"{COMMENT_RATE_SERVICE_URL}/reviews/{review_id}/", headers=headers, timeout=5)
            else:
                resp = requests.get(f"{COMMENT_RATE_SERVICE_URL}/reviews/", headers=headers, timeout=5)
        elif request.method == "POST":
            payload = json.loads(request.body) if request.body else {}
            resp = requests.post(f"{COMMENT_RATE_SERVICE_URL}/reviews/", json=payload, headers=headers, timeout=5)
        elif request.method in ["PUT", "PATCH"]:
            payload = json.loads(request.body) if request.body else {}
            if not review_id:
                return JsonResponse({"error": "Review ID required"}, status=400)
            method = requests.patch if request.method == "PATCH" else requests.put
            resp = method(f"{COMMENT_RATE_SERVICE_URL}/reviews/{review_id}/", json=payload, headers=headers, timeout=5)
        elif request.method == "DELETE":
            if not review_id:
                return JsonResponse({"error": "Review ID required"}, status=400)
            resp = requests.delete(f"{COMMENT_RATE_SERVICE_URL}/reviews/{review_id}/", headers=headers, timeout=5)
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)
        
        if resp.status_code == 204:
            return JsonResponse({"success": True}, status=200)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Review service unavailable", "detail": str(e)}, status=503)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def api_customers(request, customer_id=None):
    """Proxy for customer-service customers API"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    headers = _auth_headers(request)
    try:
        if request.method == "GET":
            if customer_id:
                resp = requests.get(f"{CUSTOMER_SERVICE_URL}/customers/{customer_id}/", headers=headers, timeout=5)
            else:
                resp = requests.get(f"{CUSTOMER_SERVICE_URL}/customers/", headers=headers, timeout=5)
        elif request.method == "POST":
            if not _is_role(request, {"manager", "staff"}):
                return JsonResponse({"error": "Only staff/manager can create customers"}, status=403)
            payload = json.loads(request.body) if request.body else {}
            resp = requests.post(f"{CUSTOMER_SERVICE_URL}/customers/", json=payload, headers=headers, timeout=5)
        elif request.method in ["PUT", "PATCH"]:
            payload = json.loads(request.body) if request.body else {}
            if not customer_id:
                return JsonResponse({"error": "Customer ID required"}, status=400)
            # Customers can only update their own profile
            session_customer_id = request.session.get("customer_id")
            role = request.session.get("role")
            if role == "customer" and str(session_customer_id) != str(customer_id):
                return JsonResponse({"error": "You can only update your own profile"}, status=403)
            method = requests.patch if request.method == "PATCH" else requests.put
            resp = method(f"{CUSTOMER_SERVICE_URL}/customers/{customer_id}/", json=payload, headers=headers, timeout=5)
        elif request.method == "DELETE":
            if not _is_role(request, {"manager"}):
                return JsonResponse({"error": "Only managers can delete customers"}, status=403)
            if not customer_id:
                return JsonResponse({"error": "Customer ID required"}, status=400)
            resp = requests.delete(f"{CUSTOMER_SERVICE_URL}/customers/{customer_id}/", headers=headers, timeout=5)
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)
        
        if resp.status_code == 204:
            return JsonResponse({"success": True}, status=200)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Customer service unavailable", "detail": str(e)}, status=503)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


def api_recommendations(request, customer_id):
    """Proxy for recommender AI service recommendations API"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    headers = _auth_headers(request)
    try:
        resp = requests.get(f"{RECOMMENDER_SERVICE_URL}/recommendations/{customer_id}/", headers=headers, timeout=5)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Recommender service unavailable", "detail": str(e)}, status=503)


def api_change_password(request, customer_id):
    """Proxy for customer change-password endpoint"""
    if not request.session.get("access_token"):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    session_customer_id = request.session.get("customer_id")
    if str(session_customer_id) != str(customer_id):
        return JsonResponse({"error": "You can only change your own password"}, status=403)

    headers = _auth_headers(request)
    try:
        payload = json.loads(request.body) if request.body else {}
        resp = requests.post(
            f"{CUSTOMER_SERVICE_URL}/customers/{customer_id}/change-password/",
            json=payload,
            headers=headers,
            timeout=5,
        )
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)
    except requests.RequestException as e:
        return JsonResponse({"error": "Customer service unavailable", "detail": str(e)}, status=503)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
