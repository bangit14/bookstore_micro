from django.urls import path
from .views import RecommendView
urlpatterns = [path("recommendations/<int:customer_id>/", RecommendView.as_view(), name="recommendations")]
