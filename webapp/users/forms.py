"""
User's forms for webapp project.
"""

from django.contrib.auth.forms import PasswordChangeForm
from django.forms import Form, CharField, EmailField, HiddenInput
from django.forms import TextInput, EmailInput, PasswordInput, ValidationError


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


class UserProfileForm(Form):
    """
    Форма отображения данных профиля пользователя
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


class MyPasswordChangeForm(PasswordChangeForm):
    """
    Переопределение формы смены пароля
    """
    old_password = CharField(
        label="Старый пароль",
        widget=PasswordInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Старый пароль',
            }
        ),
        strip=False,
    )
    new_password1 = CharField(
        label="Новый пароль",
        widget=PasswordInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Новый пароль',
            }
        ),
        strip=False,
    )
    new_password2 = CharField(
        label="Подтверждение нового пароля",
        widget=PasswordInput(
            attrs={
                'class': 'form-control border border-primary',
                'placeholder': 'Подтверждение нового пароля',
            }
        ),
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Удаление валидаторов пароля
        self.fields['new_password1'].validators = []
        self.fields['new_password2'].validators = []

    def clean_new_password1(self):
        password1 = self.cleaned_data['new_password1']
        if len(password1) < 6:
            raise ValidationError("Пароль должен содержать не менее 6 символов.")
        return password1

    def clean_new_password2(self):
        password1 = self.cleaned_data['new_password1']
        password2 = self.cleaned_data['new_password2']
        if password1 != password2:
            raise ValidationError("Пароли не совпадают.")
        return password2
