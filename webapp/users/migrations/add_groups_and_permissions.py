from django.contrib.auth.models import Group, Permission
from django.db import migrations


def add_groups_and_permissions(apps, schema_editor):
    # Create a group of readers
    group_reader = Group.objects.create(name='Reader')

    # Assign a permission to the group 'Reader'
    codenames_reader = [
        'view_book_category',
        'view_book',
        'view_store_fiction_book'
    ]
    for codename in codenames_reader:
        permission = Permission.objects.get(codename=codename)
        group_reader.permissions.add(permission)

    # Save the group 'Reader'
    group_reader.save()

    # Create a group of librarians
    group_librarian = Group.objects.create(name='Librarian')

    # Assign a permission to the group 'Librarian'
    codenames_librarian = [
        'change_user', 'view_user', 'add_book_category', 'change_book_category',
        'delete_book_category', 'view_book_category', 'add_book', 'change_book',
        'delete_book', 'view_book', 'add_school_class', 'change_school_class',
        'delete_school_class', 'view_school_class', 'add_store_fiction_book',
        'change_store_fiction_book', 'delete_store_fiction_book',
        'view_store_fiction_book', 'add_store_study_book', 'change_store_study_book',
        'delete_store_study_book', 'view_store_study_book'
    ]
    for codename in codenames_librarian:
        permission = Permission.objects.get(codename=codename)
        group_librarian.permissions.add(permission)

    # Save the group 'Librarian'
    group_librarian.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunPython(add_groups_and_permissions),
    ]
