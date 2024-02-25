"""
Library's forms for webapp project.
"""

from django.forms import Form, ModelChoiceField, CharField, IntegerField
from django.forms import Select, TextInput, ImageField, Textarea, FileInput
from .models import Book, Book_Category


class BookCategoryForm(Form):
    """
    Форма выбора категории литературы
    """
    book_category = ModelChoiceField(
        queryset=Book_Category.objects.all(),
        to_field_name="name_category",
        widget=Select(
            attrs={'class': 'form-select form-select-lg text-center'}
        )
    )

class BookForm(Form):
    """
    Форма добавления художественной книги
    """
    book_name = CharField(
        label='Наименование',
        min_length=2,
        widget=TextInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Наименование книги'
            }
        )
    )
    book_author = CharField(
        label='Автор',
        widget=TextInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Автор'
            }
        )
    )
    year_publish = IntegerField(
        label='Год издания',
        widget=TextInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Год издания'
            }
        )
    )
    book_description = CharField(
        label='Краткое описание',
        widget=Textarea(
            attrs={
                'class': 'form-control border border-primary',
                'rows': '4',
                'placeholder': 'Краткое описание'
            }
        )
    )
    num_copies = IntegerField(
        label='Кол-во экземпляров',
        widget=TextInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Кол-во экземпляров'
            }
        )
    )
    book_study_class = IntegerField(
        label='Класс изучения',
        required=False,
        widget=TextInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Класс изучения'
            }
        )
    )
    book_image = ImageField(
        label='Изображение',
        required=False,
        widget=FileInput(
            attrs={
                'class': 'form-control',
                'type': 'file',
                'name': 'book_image'
            }
        )
    )
