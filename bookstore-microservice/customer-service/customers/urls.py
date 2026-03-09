from django.urls import path
from .views import CustomerListCreate, LoginView, RegisterView

urlpatterns = [
    path("customers/", CustomerListCreate.as_view(), name="customers"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
]
