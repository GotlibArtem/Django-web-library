"""
Admin settings for library section tables.
"""

from django.contrib import admin
from .models import Book, Book_Category
from .models import School_Class, Store_Fiction_Book, Store_Study_Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Описание админки для таблицы книг (каталог)
    """
    list_display = ('book_category', 'book_name', 'book_author',
                    'year_publish', 'num_copies',
                    'book_study_class', 'book_image')
    search_fields = ['book_name', 'book_author', 'year_publish']
    list_filter = ('book_category', 'book_study_class',)
    list_per_page = 5
    autocomplete_fields = ['book_category']
    fieldsets = [('Каталог книг',
                  {'fields':
                   ['book_category', 'book_name', 'book_author',
                    'year_publish', 'num_copies',
                    'book_study_class', 'book_image']}
                  )]


@admin.register(Book_Category)
class BookCategoryAdmin(admin.ModelAdmin):
    """
    Описание админки для таблицы категории книг
    """
    list_display = ('name_category',)
    search_fields = ['name_category']
    list_filter = ('name_category', )
    fieldsets = [('Категории книг',
                  {'fields': ['name_category']})]


@admin.register(School_Class)
class SchoolClassAdmin(admin.ModelAdmin):
    """
    Описание админки для таблицы школьных классов
    """
    list_display = ('class_number', 'class_letter')
    search_fields = ['class_number']
    list_per_page = 10
    list_filter = ('class_number', )
    fieldsets = [('Школьные классы',
                  {'fields':
                   ['class_number', 'class_letter']
                   })]


@admin.register(Store_Fiction_Book)
class StoreFictionBookAdmin(admin.ModelAdmin):
    """
    Описание админки для таблицы хранения художественных книг
    """
    list_display = ('reader', 'book', 'num_books', 'issue_day',
                    'planned_return_day', 'return_day', 'status_store')
    autocomplete_fields = ['reader', 'book']
    search_fields = ['reader', 'book']
    list_per_page = 5
    list_filter = ('reader', )
    fieldsets = [('Учет художественной литературы',
                  {'fields':
                   ['reader', 'book', 'issue_day', 'planned_return_day']
                   })]


@admin.register(Store_Study_Book)
class StoreStudyBookAdmin(admin.ModelAdmin):
    """
    Описание админки для таблицы хранения учебных книг
    """
    list_display = ('school_class', 'book', 'num_books', 'issue_day',
                    'planned_return_day', 'return_day', 'status_store')
    autocomplete_fields = ['school_class', 'book']
    search_fields = ['school_class', 'book']
    list_per_page = 5
    list_filter = ('school_class', )
    fieldsets = [('Учет учебной литературы',
                  {'fields':
                   ['school_class', 'book', 'num_books', 'issue_day',
                    'planned_return_day', 'status_store']
                   })]


admin.site.site_header = 'Администрирование библиотеки'
admin.site.index_title = '''Добро пожаловать в раздел ''' \
                         '''администрирования библиотеки!'''
