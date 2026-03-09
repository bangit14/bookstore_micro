from django.contrib import admin
from django.urls import path
from .views import (
    books_view,
    catalog_view,
    cart_view,
    customers_view,
    health,
    home,
    login_view,
    manager_dashboard_view,
    orders_view,
    recommender_view,
    reviews_view,
    logout_view,
    register_view,
    staff_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("books/", books_view, name="books"),
    path("customers/", customers_view, name="customers"),
    path("cart/", cart_view, name="cart"),
    path("staff/", staff_view, name="staff"),
    path("catalog/", catalog_view, name="catalog"),
    path("orders/", orders_view, name="orders"),
    path("reviews/", reviews_view, name="reviews"),
    path("recommender/", recommender_view, name="recommender"),
    path("manager-dashboard/", manager_dashboard_view, name="manager-dashboard"),
    path("health/", health, name="health"),
]
