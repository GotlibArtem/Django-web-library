"""
User's views for webapp project.
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import UserRegistrationForm, UserProfileForm, MyPasswordChangeForm


def login_user(request):
    """
    Аутентификация пользователя
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.user_cache)
            return redirect('home')

        messages.error(request,
                       'Имя пользователя или пароль неверные!',
                       extra_tags='''alert alert-warning '''
                                  '''alert-dismissible fade show''')

    return render(request, 'users/login.html')


@login_required
def logout_user(request):
    """
    Выход из аккаунта пользователем
    """
    logout(request)

    return redirect('home')


def create_user(request):
    """
    Регистрация нового пользователя
    """
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                messages.error(request,
                               '''Пользователь с таким именем '''
                               '''уже зарегистрирован!''',
                               extra_tags='''alert alert-warning '''
                                          '''alert-dismissible fade show''')
                return redirect('users:create_user')

            if User.objects.filter(email=email).exists():
                messages.error(request,
                               '''Пользователь с такой электронной почтой '''
                               '''уже зарегистрирован!''',
                               extra_tags='''alert alert-warning '''
                                          '''alert-dismissible fade show''')
                return redirect('users:create_user')

            User.objects.create_user(first_name=first_name,
                                     last_name=last_name,
                                     username=username,
                                     email=email,
                                     password=password,)

            user = User.objects.get(username=username)
            group = Group.objects.get(name='Reader')
            user.groups.add(group)

            messages.success(request,
                             'Подзравляем, вы зарегистрированы!',
                             extra_tags='''alert alert-success '''
                                        '''alert-dismissible fade show''')
            return redirect('users:login_user')

    form = UserRegistrationForm()

    return render(request, 'users/register.html', {"form": form})


@login_required
def profile_view(request):
    """
    Профиль пользователя
    """
    user = request.user

    if request.method == 'POST' and 'change_password' in request.POST:
        password_form = MyPasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request,
                'Пароль успешно изменен!',
                extra_tags='''alert alert-success '''
                           '''alert-dismissible fade show'''
            )
            return redirect('users:profile')

    if request.method == 'POST' and 'change_name' in request.POST:
        name_form = UserProfileForm(data=request.POST)
        if name_form.is_valid():
            user.first_name = name_form.cleaned_data.get('first_name')
            user.last_name = name_form.cleaned_data.get('last_name')
            user.save()
            messages.success(
                request,
                'Имя и/или фамилия пользователя успешно изменены!',
                extra_tags='''alert alert-success '''
                           '''alert-dismissible fade show'''
            )
            return redirect('users:profile')

    password_form = MyPasswordChangeForm(user)
    name_form = UserProfileForm(initial={
        'first_name': user.first_name,
        'last_name': user.last_name
    })

    context = {
        'user': user,
        'password_form': password_form,
        'name_form': name_form
    }
    return render(request, 'users/profile.html', context)
