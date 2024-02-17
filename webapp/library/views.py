"""
Library's views for webapp project.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
from django.http import HttpResponse
from .models import Book, Book_Category
from django import template
from django.contrib.auth.models import Group


@login_required
def book_catalog(request):
    """
    Каталог книг
    """
    all_books = Book.objects.all()
    search_term = ''
    if 'book_name' in request.GET:
        all_books = all_books.order_by('book_name')

    if 'num_copies' in request.GET:
        all_books = all_books.order_by('num_copies')

    if 'search' in request.GET:
        search_term = request.GET['search']
        all_books = all_books.filter(book_name__icontains=search_term)

    paginator = Paginator(all_books, 5)
    page = request.GET.get('page')
    books = paginator.get_page(page)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()

    context = {
        'books': books,
        'params': params,
        'search_term': search_term,
    }
    return render(request, 'library/books.html', context)


@login_required
def book_info(request, book_id):
    """
    Информация по выбранной книге

    :param book_id: id книги
    """
    try:
        book = get_object_or_404(Book, pk=book_id)
    except Book.DoesNotExist:
        messages.error(request,
                       'Книга не найдена!',
                       extra_tags='''alert alert-warning'''
                                  '''alert-dismissible fade show'''
                       )
        return redirect('library:book_catalog')

    context = {
        'book': book
    }
    return render(request, 'library/book_info.html', context)
