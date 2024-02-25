"""
User's forms for webapp project.
"""

from django.forms import Form, CharField, EmailField
from django.forms import TextInput, EmailInput, PasswordInput


class UserRegistrationForm(Form):
    """
    Форма регистрации новых пользователей
    """
    first_name = CharField(
        label='Имя',
        min_length=3,
        widget=TextInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Имя'
            }
        )
    )
    last_name = CharField(
        label='Фамилия',
        min_length=3,
        widget=TextInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Фамилия'
            }
        )
    )
    username = CharField(
        label='Логин',
        min_length=5,
        widget=TextInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Логин'
            }
        )
    )
    email = EmailField(
        label='Электронная почта',
        min_length=5,
        widget=EmailInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Электронная почта'
            }
        )
    )
    password = CharField(
        label='Пароль',
        min_length=5,
        widget=PasswordInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Пароль'
            }
        )
    )
