"""
Library's views for webapp project.
"""
import codecs
import csv
import os
from datetime import datetime, timedelta
from django.db.models import Count, F, Q, Subquery, OuterRef, Sum
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Book, Book_Category, School_Class
from .models import Store_Fiction_Book, Store_Study_Book
from .forms import BookForm, BookCategoryForm
from .forms import GiveFictionBookForm, GiveStudyBookForm


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


def generate_csv_report(request, class_id):
    """
    Формирует CSV-отчет по данным из таблицы Store_Study_Book для класса.
    """
    class_info = School_Class.objects.get(pk=class_id)
    csv_file_name = f'Список книг для {class_info.class_number} {class_info.class_letter} класса.csv'
    with codecs.open(csv_file_name, 'w', 'cp1251') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Название книги',
            'Автор',
            'Кол-во книг',
            'Дата выдачи',
            'Планируемая дата возврата',
        ])

        books = Store_Study_Book.objects.filter(
            school_class=class_id,
            return_day__isnull=True,
            status_store=True
        )
        for book in books:
            writer.writerow([
                book.book.book_name,
                book.book.book_author,
                book.num_books,
                book.issue_day,
                book.planned_return_day,
            ])

    return HttpResponse(open(csv_file_name, 'rb').read(), content_type='text/csv')


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

    paginator = Paginator(all_books, 4)
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


@login_required(login_url='/home')
def get_my_books(request):
    """
    Книги пользователя (мои книги)
    """
    current_user = request.user
    user_books = Store_Fiction_Book.objects.filter(
        reader_id=current_user.id,
        book_id=F('book__id')
    ).order_by('planned_return_day')

    search_term = ''
    if 'return_day_asc' in request.GET:
        user_books = user_books.order_by('planned_return_day')
    if 'return_day_desc' in request.GET:
        user_books = user_books.order_by('-planned_return_day')
    if 'search' in request.GET:
        search_term = request.GET['search']
        user_books = user_books.filter(
           book__book_name__icontains=search_term
        )

    context = {
        'user_books': user_books,
        'search_term': search_term,
        'today': timezone.now().date()
    }

    return render(request, 'library/my_books.html', context)


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
def select_reader_for_book_issuer(request):
    """
    Выбор читателя перед выдачью книги
    """
    readers_group = Group.objects.get(name='Reader')
    today = timezone.now().date()
    reader_list = User.objects.filter(groups=readers_group).annotate(
        num_active_books=Count('store_fiction_book', filter=Q(
            store_fiction_book__return_day__isnull=True
        )),
        num_overdue_books=Count('store_fiction_book', filter=Q(
            store_fiction_book__return_day__isnull=True,
            store_fiction_book__planned_return_day__lt=today
        ))
    ).order_by('last_name')
    search_term = ''
    if 'search' in request.GET:
        search_term = request.GET['search']
        reader_list = User.objects.filter(Q(groups=readers_group) &
                                    (Q(first_name__icontains=search_term) |
                                     Q(last_name__icontains=search_term) |
                                     Q(email__icontains=search_term) |
                                     Q(username__icontains=search_term)))

    context = {
        'reader_list': reader_list,
        'search_term': search_term,
    }
    return render(request, 'library/choose_reader.html', context)


@permission_required('library.add_store_fiction_book',
                     login_url='/library/all_books')
def get_reader_books(request, reader_id):
    """
    Книги читателя
    """
    reader = User.objects.get(id=reader_id)
    reader_books = Store_Fiction_Book.objects.filter(
        reader_id=reader_id,
        book_id=F('book__id')
    ).order_by('-return_day')
    search_term = ''
    if 'search' in request.GET:
        search_term = request.GET['search']
        reader_books = Store_Fiction_Book.objects.filter(
            reader_id=reader_id,
            book__book_name__icontains=search_term
        )

    paginator = Paginator(reader_books, 3)
    page = request.GET.get('page')
    list_fiction_books = paginator.get_page(page)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()

    if request.method == 'POST' and 'change-store' in request.POST:
        store_book_id = request.POST.get('store-book-id')
        planned_return_day = request.POST.get('planned-return-day')
        Store_Fiction_Book.objects.filter(pk=store_book_id) \
            .update(planned_return_day=planned_return_day)
        messages.success(
            request,
            'Период возврата книги успешно изменен!',
            extra_tags='alert alert-warning alert-dismissible fade show'
        )
        return redirect('library:reader_books', reader_id)

    if request.method == 'POST' and 'return-store' in request.POST:
        store_book_id = request.POST.get('store-book-id')
        Store_Fiction_Book.objects.filter(pk=store_book_id) \
            .update(return_day=datetime.now() + timedelta(hours=3))
        # Изменения остатка экземпляров книг
        reader_book = Store_Fiction_Book.objects.select_related('book').get(pk=store_book_id)
        book = reader_book.book
        book.num_copies += 1
        book.save()
        messages.success(
            request,
            'Книга возвращена!',
            extra_tags='alert alert-success alert-dismissible fade show'
        )
        return redirect('library:reader_books', reader_id)

    if request.method == 'POST' and 'give_book' in request.POST:
        return redirect('library:give_fiction_book', reader_id)

    context = {
        'reader': reader,
        'list_fiction_books': list_fiction_books,
        'params': params,
        'search_term': search_term,
        'today': timezone.now().date()
    }

    return render(request, 'library/reader_books.html', context)


@permission_required('library.add_store_fiction_book',
                     login_url='/library/all_books')
@csrf_exempt
def give_fiction_book(request, reader_id):
    """
    Выдача книги читателю
    """
    reader = User.objects.get(id=reader_id)
    all_books = Book.objects.filter(book_category_id=1).order_by('book_name')

    search_term = ''
    if 'search' in request.GET:
        search_term = request.GET['search']
        all_books = (all_books.filter(Q(book_name__icontains=search_term) |
                                      Q(book_author__icontains=search_term) |
                                      Q(year_publish__icontains=search_term)))

    paginator = Paginator(all_books, 3)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()

    issued_books = Store_Fiction_Book.objects \
        .filter(Q(reader=reader_id) & Q(status_store=False)) \
        .select_related('book')

    # Добавление записи о выдаваемых книгах
    if request.method == 'POST' and 'add-issued-book' in request.POST:
        book_id = request.POST.get('fiction-book-id')
        book = Book.objects.get(pk=book_id)
        # Изменения остатка экземпляров книг
        new_num_copies = book.num_copies - 1
        if new_num_copies < 0:
            messages.warning(
                request,
                'Кол-во выдаваемых книг превышает остаток экземпляров книг!',
                extra_tags='alert alert-danger alert-dismissible fade show'
            )
            return redirect('library:give_fiction_book', reader_id)

        Store_Fiction_Book.objects.create(
            reader=User.objects.get(pk=reader_id),
            book=book,
            num_books=1,
            issue_day=timezone.now(),
            planned_return_day=timezone.now(),
            status_store=False
        )
        Book.objects.filter(pk=book.id).update(
            num_copies=new_num_copies
        )
        return redirect('library:give_fiction_book', reader_id)

    # Удаление записи о выдаваемых книгах
    if request.method == 'POST' and 'delete-issued-book' in request.POST:
        issue_book_id = request.POST.get('issued-book-id')
        issue_book = Store_Fiction_Book.objects.get(pk=issue_book_id)
        book = Book.objects.get(pk=issue_book.book.id)
        # Изменения остатка экземпляров книг
        new_num_copies = book.num_copies + 1

        Store_Fiction_Book.objects.filter(pk=issue_book_id).delete()
        Book.objects.filter(pk=book.id).update(
            num_copies=new_num_copies
        )
        return redirect('library:give_fiction_book', reader_id)

    if request.method == 'POST' and 'give_books' in request.POST:
        form = GiveFictionBookForm(request.POST)
        if form.is_valid():
            issue_day = form.cleaned_data.get('issue_day')
            planned_return_day = form.cleaned_data.get('planned_return_day')
            issued_books = Store_Fiction_Book.objects \
                .filter(Q(reader=reader_id) & Q(status_store=False))
            for issued_book in issued_books:
                Store_Fiction_Book.objects.filter(pk=issued_book.id).update(
                    issue_day=issue_day,
                    planned_return_day=planned_return_day,
                    status_store=True
                )
            messages.success(
                request,
                'Художественная литература успешно выдана!',
                extra_tags='alert alert-success alert-dismissible fade show'
            )
            return redirect('library:reader_books', reader_id)

    form = GiveFictionBookForm(
        initial={'issue_day': timezone.now(),
                 'planned_return_day': timezone.now() + timedelta(days=30)}
    )
    context = {
        'form': form,
        'reader': reader,
        'books': books,
        'params': params,
        'search_term': search_term,
        'issued_books': issued_books
    }
    return render(request, 'library/give_fiction_book.html', context)


@permission_required('library.add_store_study_book',
                     login_url='/library/all_books')
def select_class_for_book_issuer(request):
    """
    Выбор класса перед выдачью книги
    """
    class_list = School_Class.objects.all().order_by('id')

    search_term = ''
    if 'search' in request.GET:
        search_term = request.GET['search']
        class_list = School_Class.objects.filter((
            Q(class_number__icontains=search_term) |
            Q(class_letter__icontains=search_term)
        ))

    context = {
        'class_list': class_list,
        'search_term': search_term,
    }
    return render(request, 'library/choose_class.html', context)


@permission_required('library.add_store_study_book',
                     login_url='/library/all_books')
def get_class_books(request, class_id):
    """
    Книги, выданные классу

    :param class_id: id класса
    """
    school_class = School_Class.objects.get(id=class_id)
    class_books = Store_Study_Book.objects.filter(
        school_class=class_id
    ).order_by('-return_day') & Store_Study_Book.objects.filter(
        Q(book_id=F('book__id'))
    )

    # Поиск по параметрам книги
    search_term = ''
    if 'search' in request.GET:
        search_term = request.GET['search']
        class_books = Store_Study_Book.objects.filter(
            Q(school_class=class_id) &
            Q(book__book_name__icontains=search_term)
        )

    # Пагинация
    paginator = Paginator(class_books, 7)
    page = request.GET.get('page')
    list_study_books = paginator.get_page(page)
    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()

    # Изменение данных по выданным книгам
    if request.method == 'POST' and 'change-store' in request.POST:
        study_book_id = request.POST.get('study-book-id')
        num_books = request.POST.get('num-books')
        planned_return_day = request.POST.get('planned-return-day')
        Store_Study_Book.objects.filter(pk=study_book_id) \
            .update(planned_return_day=planned_return_day)
        messages.success(
            request,
            'Период возврата книги успешно изменен!',
            extra_tags='alert alert-warning alert-dismissible fade show'
        )
        return redirect('library:class_books', class_id)

    if request.method == 'POST' and 'return-store' in request.POST:
        study_book_id = request.POST.get('study-book-id')
        num_books = int(request.POST.get('num-books'))
        planned_return_day = request.POST.get('planned-return-day')
        class_book = Store_Study_Book.objects.select_related('book').get(pk=study_book_id)
        if class_book.num_books < num_books:
            messages.warning(
                request,
                'Кол-во книг возврата превышает число книг, взятых классом!',
                extra_tags='alert alert-danger alert-dismissible fade show'
            )
            return redirect('library:class_books', class_id)
        if class_book.num_books > num_books:
            Store_Study_Book.objects.create(
                school_class=School_Class.objects.get(pk=class_id),
                book=class_book.book,
                num_books=num_books,
                issue_day=class_book.issue_day,
                planned_return_day=request.POST.get('planned-return-day'),
                return_day=datetime.now() + timedelta(hours=3),
                status_store=True
            )
            class_book.num_books = class_book.num_books - num_books
            class_book.save()
        else:
            Store_Study_Book.objects.filter(pk=study_book_id) \
                .update(return_day=datetime.now() + timedelta(hours=3))
        # Изменения остатка экземпляров книг
        book = class_book.book
        book.num_copies += int(num_books)
        book.save()
        messages.success(
            request,
            'Книга возвращена!',
            extra_tags='alert alert-success alert-dismissible fade show'
        )
        return redirect('library:class_books', class_id)

    if request.method == 'POST' and 'give_book' in request.POST:
        return redirect('library:give_study_book', class_id)

    context = {
        'school_class': school_class,
        'list_study_books': list_study_books,
        'params': params,
        'search_term': search_term,
        'today': timezone.now().date()
    }

    return render(request, 'library/class_books.html', context)


@permission_required('library.add_store_study_book',
                     login_url='/library/all_books')
@csrf_exempt
def give_study_book(request, class_id):
    """
    Выдача учебников для класса

    :param class_id: id класса
    """
    school_class = School_Class.objects.get(id=class_id)
    all_books = Book.objects.filter(book_category_id=2) \
        .order_by('book_study_class')
    issued_books = Store_Study_Book.objects \
        .filter(Q(school_class=class_id) & Q(status_store=False)) \
        .select_related('book')

    # Поиск по параметрам книги
    search_term = ''
    if 'search' in request.GET:
        search_term = request.GET['search']
        all_books = (all_books.filter(
            Q(book_name__icontains=search_term) |
            Q(book_author__icontains=search_term) |
            Q(year_publish__icontains=search_term) |
            Q(book_study_class__icontains=search_term)
        ))

    # Пагинация
    paginator = Paginator(all_books, 3)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()

    # Добавление записи о выдаваемых книгах
    if request.method == 'POST' and 'add-issued-book' in request.POST:
        book_id = request.POST.get('study-book-id')
        num_books = request.POST.get('num-books')
        book = Book.objects.get(pk=book_id)
        # Изменения остатка экземпляров книг
        new_num_copies = book.num_copies - int(num_books)
        if new_num_copies < 0:
            messages.warning(
                request,
                'Кол-во выдаваемых книг превышает остаток экземпляров книг!',
                extra_tags='alert alert-danger alert-dismissible fade show'
            )
            return redirect('library:give_study_book', class_id)

        Store_Study_Book.objects.create(
            school_class=School_Class.objects.get(pk=class_id),
            book=book,
            num_books=num_books,
            issue_day=timezone.now(),
            planned_return_day=timezone.now(),
            status_store=False
        )
        Book.objects.filter(pk=book.id).update(
            num_copies=new_num_copies
        )
        return redirect('library:give_study_book', class_id)

    # Удаление записи о выдаваемых книгах
    if request.method == 'POST' and 'delete-issued-book' in request.POST:
        issue_book_id = request.POST.get('issued-book-id')
        issue_book = Store_Study_Book.objects.get(pk=issue_book_id)
        book = Book.objects.get(pk=issue_book.book.id)
        # Изменения остатка экземпляров книг
        new_num_copies = book.num_copies + issue_book.num_books
        Store_Study_Book.objects.filter(pk=issue_book_id).delete()
        Book.objects.filter(pk=book.id).update(
            num_copies=new_num_copies
        )
        return redirect('library:give_study_book', class_id)

    # Выдача книг
    if request.method == 'POST' and 'give_books' in request.POST:
        form = GiveStudyBookForm(request.POST)
        if form.is_valid():
            issue_day = form.cleaned_data.get('issue_day')
            planned_return_day = form.cleaned_data.get('planned_return_day')
            num_books = request.POST.get('num-books')
            issued_books = Store_Study_Book.objects \
                .filter(Q(school_class=class_id) & Q(status_store=False))
            for issued_book in issued_books:
                Store_Study_Book.objects.filter(pk=issued_book.id).update(
                    issue_day=issue_day,
                    planned_return_day=planned_return_day,
                    status_store=True
                )
            messages.success(
                request,
                'Учебная литература успешно выдана!',
                extra_tags='alert alert-success alert-dismissible fade show'
            )
            return redirect('library:class_books', class_id)

    form = GiveStudyBookForm(
        initial={'issue_day': timezone.now(),
                 'planned_return_day': timezone.now() + timedelta(days=273)}
    )
    context = {
        'form': form,
        'school_class': school_class,
        'books': books,
        'params': params,
        'search_term': search_term,
        'issued_books': issued_books
    }
    return render(request, 'library/give_study_book.html', context)
