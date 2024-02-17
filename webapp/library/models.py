"""
Library's models for webapp project.
"""

from django.contrib.auth.models import User
from django.db import models


class Book_Category(models.Model):
    """
    Таблица категорий книг
    """
    name_category = models.CharField(
        max_length=64, verbose_name='Имя категории', db_comment='Имя категории'
    )

    def __str__(self) -> str:
        return f'{self.name_category}'

    class Meta:
        """
        Переопределение отображаемых имен в админке
        """
        verbose_name = 'категорию книг'
        verbose_name_plural = 'Категории книг'


class Book(models.Model):
    """
    Таблица книг (каталог)
    """
    book_category = models.ForeignKey(
        Book_Category, on_delete=models.DO_NOTHING,
        verbose_name='Категория', db_comment='id категории'
    )
    book_name = models.CharField(
        max_length=256, null=False,
        verbose_name='Наименование', db_comment='Наименование'
    )
    book_author = models.CharField(
        max_length=128, verbose_name='Автор', db_comment='Автор'
    )
    year_publish = models.IntegerField(
        verbose_name='Год издания', db_comment='Год издания'
    )
    book_description = models.CharField(
        max_length=2048,
        verbose_name='Краткое описание', db_comment='Краткое описание'
    )
    num_copies = models.IntegerField(
        default=0, null=False,
        verbose_name='Кол-во экземпляров', db_comment='Кол-во экземпляров'
    )
    book_study_class = models.IntegerField(
        null=True, blank=True,
        verbose_name='Класс изучения', db_comment='Класс изучения'
    )
    book_image = models.ImageField(
        upload_to='library/',
        verbose_name='Изображение', db_comment='Путь к изображению'
    )

    def __str__(self) -> str:
        return f'Книга: {self.book_name}'

    class Meta:
        """
        Переопределение отображаемых имен в админке
        """
        verbose_name = 'книгу'
        verbose_name_plural = 'Каталог книг'


class School_Class(models.Model):
    """
    Таблица школьных классов
    """
    class_number = models.IntegerField(
        null=False, verbose_name='Номер класса', db_comment='Номер класса'
    )
    class_letter = models.CharField(
        max_length=1, null=False,
        verbose_name='Буква класса', db_comment='Буква класса'
    )

    def __str__(self) -> str:
        return f'Класс {self.class_number} {self.class_letter}'

    class Meta:
        """
        Переопределение отображаемых имен в админке
        """
        verbose_name = 'класс'
        verbose_name_plural = 'Классы'


class Store_Fiction_Book(models.Model):
    """
    Таблица выдачи художественной литературы
    """
    reader = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Читатель', db_comment='id читателя'
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE,
        verbose_name='Книга', db_comment='id книги'
    )
    num_books = models.IntegerField(
        default=1, null=False,
        verbose_name='Количество', db_comment='Количество'
    )
    issue_day = models.DateField(
        auto_now_add=True, verbose_name='День выдачи', db_comment='День выдачи'
    )
    period = models.IntegerField(
        default=30, null=False,
        verbose_name='Период возврата', db_comment='Период возврата'
    )
    return_day = models.DateField(  
        verbose_name='День возврата', db_comment='День возврата'
    )

    class Meta:
        """
        Переопределение отображаемых имен в админке
        """
        verbose_name = 'выданную художественную литературу'
        verbose_name_plural = 'Учет художественной литературы'


class History_Fiction_Book(models.Model):
    """
    Таблица библиотекарей, выдававших художественную литературу
    """
    librarian = models.ForeignKey(
        User, on_delete=models.CASCADE, db_comment='id библиотекаря'
    )
    store_fiction_book = models.ForeignKey(
        Store_Fiction_Book, on_delete=models.CASCADE,
        db_comment='id выданной художественной книги'
    )


class Store_Study_Book(models.Model):
    """
    Таблица выдачи учебной литературы
    """
    school_clase = models.ForeignKey(
        School_Class, on_delete=models.CASCADE,
        verbose_name='Школьный класс', db_comment='id класса'
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE,
        verbose_name='Книга', db_comment='id книги'
    )
    num_books = models.IntegerField(
        null=False, verbose_name='Количество', db_comment='Количество'
    )
    issue_day = models.DateField(
        auto_now_add=True, verbose_name='День выдачи', db_comment='День выдачи'
    )
    period = models.IntegerField(
        default=273, null=False,
        verbose_name='Период возврата', db_comment='Период возврата'
    )
    return_day = models.DateField(
        verbose_name='День возврата', db_comment='День возврата'
    )

    class Meta:
        """
        Переопределение отображаемых имен в админке
        """
        verbose_name = 'выданную учебную литературу'
        verbose_name_plural = 'Учет учебной литературы'


class History_Study_Book(models.Model):
    """
    Таблица библиотекарей, выдававших учебную литературу
    """
    librarian = models.ForeignKey(
        User, on_delete=models.CASCADE, db_comment='id библиотекаря'
    )
    store_study_book = models.ForeignKey(
        Store_Study_Book, on_delete=models.CASCADE,
        db_comment='id выданной учебной литературы'
    )
