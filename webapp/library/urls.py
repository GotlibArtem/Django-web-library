"""
URL configuration for library of webapp project.
"""

from django.urls import path
from . import views


app_name = "library"

urlpatterns = [
    path('all_books',
         views.book_catalog,
         name='book_catalog'),
    path('book/<int:book_id>/',
         views.book_info,
         name='book_info'),
    path('change_book/<int:book_id>/',
         views.change_book_info,
         name='change_book'),
    path('add_book',
         views.select_category,
         name='select_category'),
    path('add_book/<int:book_category_id>',
         views.add_book,
         name='add_book'),
    path('give_book', views.give_book, name='give_book')
]
