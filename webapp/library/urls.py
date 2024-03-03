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
    path('my_books',
         views.get_my_books,
         name='my_books'),
    path('change_book/<int:book_id>/',
         views.change_book_info,
         name='change_book'),
    path('add_book',
         views.select_category,
         name='select_category'),
    path('add_book/<int:book_category_id>',
         views.add_book,
         name='add_book'),
    path('select_reader_for_book_issuer',
         views.select_reader_for_book_issuer,
         name='select_reader'),
    path('reader_books/<int:reader_id>',
         views.get_reader_books,
         name='reader_books'),
    path('give_fiction_book/<int:reader_id>',
         views.give_fiction_book,
         name='give_fiction_book'),
    path('select_class_for_book_issuer',
         views.select_class_for_book_issuer,
         name='select_class'),
    path('class_books/<int:class_id>',
         views.get_class_books,
         name='class_books'),
    path('give_study_book/<int:class_id>',
         views.give_study_book,
         name='give_study_book'),
    path('generate_csv_report/<int:class_id>',
         views.generate_csv_report,
         name='generate_csv_report'),
]
