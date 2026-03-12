from django.urls import path
from .views import (
    BookListCreate, BookDetail,
    PublisherListCreate, PublisherDetail,
    CategoryListCreate, CategoryDetail
)

urlpatterns = [
    # Books
    path("books/", BookListCreate.as_view(), name="books"),
    path("books/<int:book_id>/", BookDetail.as_view(), name="book-detail"),
    
    # Publishers
    path("publishers/", PublisherListCreate.as_view(), name="publishers"),
    path("publishers/<int:publisher_id>/", PublisherDetail.as_view(), name="publisher-detail"),
    
    # Categories
    path("categories/", CategoryListCreate.as_view(), name="categories"),
    path("categories/<int:category_id>/", CategoryDetail.as_view(), name="category-detail"),
]
