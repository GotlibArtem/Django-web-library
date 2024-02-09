"""
Library's views for webapp project.
"""

from django.shortcuts import render


def book_catalog(request):
    """
    Каталог книг
    """
    return render(request, 'home.html')
