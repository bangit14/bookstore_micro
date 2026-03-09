from django.urls import path
from .views import DashboardView
urlpatterns = [path("manager/dashboard/", DashboardView.as_view(), name="manager-dashboard")]
