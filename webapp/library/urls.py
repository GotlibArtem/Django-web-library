"""
URL configuration for library of webapp project.
"""

from django.urls import path
from . import views


app_name = "library"

urlpatterns = [
    path('all_books', views.book_catalog, name='book_catalog'),
    path('book/<int:book_id>/', views.book_info, name='book_info')
]
