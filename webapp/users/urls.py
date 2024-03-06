"""
URL configuration for users of webapp project.
"""

from django.urls import path
from . import views


app_name = "users"

urlpatterns = [
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('register/', views.create_user, name='create_user'),
    path('profile/', views.profile_view, name='profile'),
]
