"""
Library's views for webapp project.
"""

import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.contrib import messages
from django.conf import settings
from .models import Book, Book_Category
from .forms import BookForm, BookCategoryForm


def check_group(request, group_name) -> bool:
    """
    Проверка, что пользователь принадлежит к группе Reader

    :param group_name: имя группы
    """
    user = request.user
    group = Group.objects.get(name=group_name)
    if user.groups.filter(name=group.name).exists():
        return True
    return False


@login_required(login_url='/home')
def book_catalog(request):
    """
    Каталог книг
    """
    if check_group(request, group_name='Reader'):
        all_books = Book.objects.filter(book_category_id=1)
    else:
        all_books = Book.objects.all()

    search_term = ''
    if 'book_name_asc' in request.GET:
        all_books = all_books.order_by('book_name')
    if 'book_name_desc' in request.GET:
        all_books = all_books.order_by('-book_name')

    if 'year_publish_asc' in request.GET:
        all_books = all_books.order_by('year_publish')
    if 'year_publish_desc' in request.GET:
        all_books = all_books.order_by('-year_publish')

    if 'search' in request.GET:
        search_term = request.GET['search']
        all_books = (all_books.filter(book_name__icontains=search_term) |
                     all_books.filter(book_author__icontains=search_term) |
                     all_books.filter(year_publish__icontains=search_term))

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


@login_required(login_url='/home')
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


@permission_required('library.add_book', login_url='/library/all_books')
def select_category(request):
    """
    Выбор категории литературы перед добавление новой книги
    """
    if request.method == 'POST':
        form = BookCategoryForm(data=request.POST)
        if form.is_valid():
            book_category = Book_Category.objects.get(
                name_category=str(form.cleaned_data.get('book_category'))
            )
            if book_category:
                return redirect('library:add_book', book_category.id)
            messages.error(request,
                           f'''Категория "{book_category}" не найдена,'''
                           f''' обратитесь к администратору!''',
                           extra_tags='''alert alert-warning'''
                                      '''alert-dismissible fade show''')
            return redirect('library:select_category')
    form = BookCategoryForm()

    return render(request, 'library/select_category.html', {'form': form})


@permission_required('library.add_book', login_url='/library/all_books')
def add_book(request, book_category_id):
    """
    Добавление новой книги
    """
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book_name = form.cleaned_data.get('book_name')
            book_author = form.cleaned_data.get('book_author')
            year_publish = form.cleaned_data.get('year_publish')
            book_description = form.cleaned_data.get('book_description')
            num_copies = form.cleaned_data.get('num_copies')
            book_study_class = form.cleaned_data.get('book_study_class')
            if form.cleaned_data.get('book_image'):
                book_image = request.FILES['book_image']
            else:
                book_image = None

            Book.objects.create(
                book_category_id=book_category_id,
                book_name=book_name,
                book_author=book_author,
                year_publish=year_publish,
                book_description=book_description,
                num_copies=num_copies,
                book_study_class=book_study_class,
                book_image=book_image
            )

            book_category = get_object_or_404(
                Book_Category, pk=book_category_id
            )
            messages.success(
                request,
                f'{book_category.name_category} литература успешно добавлена!',
                extra_tags='alert alert-success alert-dismissible fade show'
            )
            return redirect('library:book_catalog')
    form = BookForm()
    context = {
        'form': form,
        'book_category_id': book_category_id
    }
    return render(request, 'library/add_book.html', context)


@permission_required(['library.change_book', 'library.delete_book'],
                     login_url='/library/all_books')
def change_book_info(request, book_id):
    """
    Изменение информации о имеющейся книги или удаление ее
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

    if request.method == 'POST' and 'change' in request.POST:
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book_name = form.cleaned_data.get('book_name')
            book_author = form.cleaned_data.get('book_author')
            year_publish = form.cleaned_data.get('year_publish')
            book_description = form.cleaned_data.get('book_description')
            num_copies = form.cleaned_data.get('num_copies')
            book_study_class = form.cleaned_data.get('book_study_class')
            if form.cleaned_data.get('book_image'):
                book_image = request.FILES['book_image']
                FileSystemStorage(
                    location=os.path.join(settings.MEDIA_ROOT, 'library')
                ).save(book_image.name, book_image)
                book_image = f'library/{book_image}'
            else:
                book_image = book.book_image

            Book.objects.filter(id=book_id).update(
                book_name=book_name,
                book_author=book_author,
                year_publish=year_publish,
                book_description=book_description,
                num_copies=num_copies,
                book_study_class=book_study_class,
                book_image=book_image
            )
            messages.success(
                request,
                f'Книга "{book_name}" успешно изменена!',
                extra_tags='alert alert-success alert-dismissible fade show'
            )
            return redirect('library:book_catalog')

    if request.method == 'POST' and 'delete' in request.POST:
        form = BookForm(request.POST)
        if form.is_valid():
            book_name = book.book_name
            Book.objects.filter(id=book_id).delete()
            messages.success(
                request,
                f'Книга "{book_name}" удалена!',
                extra_tags='alert alert-success alert-dismissible fade show'
            )
            return redirect('library:book_catalog')

    form = BookForm(initial={'book_category_id': book.book_category,
                             'book_name': book.book_name,
                             'book_author': book.book_author,
                             'year_publish': book.year_publish,
                             'book_description': book.book_description,
                             'num_copies': book.num_copies,
                             'book_study_class': book.book_study_class})
    book_image = book.book_image
    context = {
        'form': form,
        'book_image': book_image
    }
    return render(request, 'library/change_book.html', context)


@permission_required('library.add_store_fiction_book',
                     login_url='/library/all_books')
def give_book(request):
    """
    Выдать книгу
    """
    readers_group = Group.objects.get(name='Reader')
    users = User.objects.filter(groups=readers_group)
    return redirect('library:book_catalog')
