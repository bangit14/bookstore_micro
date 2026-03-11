from django.urls import path
from .views import CustomerListCreate, CustomerDetail, ChangePasswordView, LoginView, RegisterView

urlpatterns = [
    path("customers/", CustomerListCreate.as_view(), name="customers"),
    path("customers/<int:customer_id>/", CustomerDetail.as_view(), name="customer-detail"),
    path("customers/<int:customer_id>/change-password/", ChangePasswordView.as_view(), name="customer-change-password"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
]
