from django.contrib import admin
from django.urls import path
from .views import (
    # Auth views
    login_view,
    logout_view,
    register_view,
    # Home and utility
    landing_page,
    home,
    health,
    # Book views
    book_list_view,
    book_create_view,
    book_update_view,
    # Customer views
    customer_list_view,
    customer_create_view,
    # Cart views
    cart_view,
    cart_add_item_view,
    # Staff views
    staff_list_view,
    staff_create_view,
    # Catalog views
    catalog_list_view,
    catalog_create_view,
    # Review views
    review_list_view,
    review_create_view,
    # Order views
    order_create_view,
    order_list_view,
    order_detail_view,
    # Manager and recommender
    manager_dashboard_view,
    recommender_view,
    # New role-based views
    customer_dashboard_view,
    customer_products_view,
    customer_cart_view,
    customer_orders_view,
    customer_profile_view,
    customer_reviews_view,
    customer_recommendations_view,
    staff_dashboard_view,
    staff_products_view,
    staff_orders_view,
    staff_inventory_view,
    staff_shipments_view,
    staff_customers_view,
    staff_reviews_view,
    # Warehouse staff views
    warehouse_dashboard_view,
    warehouse_products_view,
    warehouse_shipments_view,
    # Sales staff views
    sales_dashboard_view,
    sales_orders_view,
    sales_customers_view,
    sales_reviews_view,
    manager_dashboard_new_view,
    manager_staff_view,
    manager_reports_view,
    manager_products_view,
    manager_orders_view,
    manager_payments_view,
    manager_shipments_view,
    manager_reviews_view,
    manager_system_view,
    # API Proxy endpoints
    api_manager_dashboard,
    api_books,
    api_orders,
    api_payments,
    api_staff,
    api_carts,
    api_cart_by_customer,
    api_cart_items,
    api_products,
    api_shipments,
    api_reviews,
    api_customers,
    api_recommendations,
    api_change_password,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("home/", landing_page, name="landing"),
    # Auth URLs
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    # Book URLs
    path("books/", book_list_view, name="book_list"),
    path("books/create/", book_create_view, name="book_create"),
    path("books/<int:book_id>/update/", book_update_view, name="book_update"),
    # Customer URLs
    path("customers/", customer_list_view, name="customer_list"),
    path("customers/create/", customer_create_view, name="customer_create"),
    # Cart URLs
    path("cart/", cart_view, name="cart_view"),
    path("cart/add/", cart_add_item_view, name="cart_add_item"),
    # Staff URLs
    path("staff/", staff_list_view, name="staff_list"),
    path("staff/create/", staff_create_view, name="staff_create"),
    # Catalog URLs
    path("catalog/", catalog_list_view, name="catalog_list"),
    path("catalog/create/", catalog_create_view, name="catalog_create"),
    # Review URLs
    path("reviews/", review_list_view, name="review_list"),
    path("reviews/create/", review_create_view, name="review_create"),
    # Order URLs
    path("orders/", order_list_view, name="order_list"),
    path("orders/create/", order_create_view, name="order_create"),
    path("orders/<int:order_id>/", order_detail_view, name="order_detail"),
    # Manager and Recommender
    path("recommender/", recommender_view, name="recommender"),
    path("manager-dashboard/", manager_dashboard_view, name="manager-dashboard"),
    
    # ========== NEW ROLE-BASED URLS ==========
    # Customer Pages
    path("customer/dashboard/", customer_dashboard_view, name="customer_dashboard"),
    path("customer/products/", customer_products_view, name="customer_products"),
    path("customer/cart/", customer_cart_view, name="customer_cart"),
    path("customer/orders/", customer_orders_view, name="customer_orders"),
    path("customer/profile/", customer_profile_view, name="customer_profile"),
    path("customer/reviews/", customer_reviews_view, name="customer_reviews"),
    path("customer/recommendations/", customer_recommendations_view, name="customer_recommendations"),
    
    # Staff Pages
    path("staff/dashboard/", staff_dashboard_view, name="staff_dashboard"),
    path("staff/products/", staff_products_view, name="staff_products"),
    path("staff/orders/", staff_orders_view, name="staff_orders"),
    path("staff/inventory/", staff_inventory_view, name="staff_inventory"),
    path("staff/shipments/", staff_shipments_view, name="staff_shipments"),
    path("staff/customers/", staff_customers_view, name="staff_customers"),
    path("staff/reviews/", staff_reviews_view, name="staff_reviews"),

    # Warehouse Staff Pages
    path("staff/warehouse/", warehouse_dashboard_view, name="warehouse_dashboard"),
    path("staff/warehouse/products/", warehouse_products_view, name="warehouse_products"),
    path("staff/warehouse/shipments/", warehouse_shipments_view, name="warehouse_shipments"),

    # Sales Staff Pages
    path("staff/sales/", sales_dashboard_view, name="sales_dashboard"),
    path("staff/sales/orders/", sales_orders_view, name="sales_orders"),
    path("staff/sales/customers/", sales_customers_view, name="sales_customers"),
    path("staff/sales/reviews/", sales_reviews_view, name="sales_reviews"),

    # Manager Pages
    path("manager/dashboard/", manager_dashboard_new_view, name="manager_dashboard_new"),
    path("manager/staff/", manager_staff_view, name="manager_staff"),
    path("manager/reports/", manager_reports_view, name="manager_reports"),
    path("manager/products/", manager_products_view, name="manager_products"),
    path("manager/orders/", manager_orders_view, name="manager_orders"),
    path("manager/payments/", manager_payments_view, name="manager_payments"),
    path("manager/shipments/", manager_shipments_view, name="manager_shipments"),
    path("manager/reviews/", manager_reviews_view, name="manager_reviews"),
    path("manager/system/", manager_system_view, name="manager_system"),
    
    # ========== API PROXY ENDPOINTS ==========
    path("api/manager/dashboard/", api_manager_dashboard, name="api_manager_dashboard"),
    path("api/books/", api_books, name="api_books"),
    path("api/books/<int:book_id>/", api_books, name="api_book_detail"),
    path("api/orders/", api_orders, name="api_orders"),
    path("api/orders/<int:order_id>/", api_orders, name="api_orders_detail"),
    path("api/payments/", api_payments, name="api_payments"),
    path("api/staff/", api_staff, name="api_staff_list"),
    path("api/staff/<int:staff_id>/", api_staff, name="api_staff_detail"),
    path("api/carts/", api_carts, name="api_carts_list"),
    path("api/carts/customer/<int:customer_id>/", api_cart_by_customer, name="api_cart_by_customer"),
    path("api/carts/<int:cart_id>/", api_carts, name="api_carts_detail"),
    path("api/cart-items/", api_cart_items, name="api_cart_items_list"),
    path("api/cart-items/<int:item_id>/", api_cart_items, name="api_cart_items_detail"),
    path("api/products/", api_products, name="api_products_list"),
    path("api/products/<int:product_id>/", api_products, name="api_products_detail"),
    path("api/shipments/", api_shipments, name="api_shipments_list"),
    path("api/shipments/<int:shipment_id>/", api_shipments, name="api_shipments_detail"),
    path("api/reviews/", api_reviews, name="api_reviews_list"),
    path("api/reviews/<int:review_id>/", api_reviews, name="api_reviews_detail"),
    path("api/customers/", api_customers, name="api_customers_list"),
    path("api/customers/<int:customer_id>/", api_customers, name="api_customers_detail"),
    path("api/customers/<int:customer_id>/change-password/", api_change_password, name="api_change_password"),
    path("api/recommendations/<int:customer_id>/", api_recommendations, name="api_recommendations"),
    
    # Health check
    path("health/", health, name="health"),
]
