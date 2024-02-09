"""
URL configuration for library of webapp project.
"""

from django.urls import path
from . import views


app_name = "library"

urlpatterns = [
    path('books', views.book_catalog, name='book_catalog'),
]
