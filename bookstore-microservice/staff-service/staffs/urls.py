from django.urls import path
from .views import StaffListCreate, StaffDetail, StaffProfile

urlpatterns = [
    path("staffs/", StaffListCreate.as_view(), name="staffs"),
    path("staffs/profile/", StaffProfile.as_view(), name="staff-profile"),
    path("staffs/<int:staff_id>/", StaffDetail.as_view(), name="staff-detail"),
]
