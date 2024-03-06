import os
import pandas as pd
import psycopg2
import tkinter as tk
from tkinter import filedialog, StringVar, Entry
from settings import DB_NAME, DB_USER, DB_PASSWORD


# Функция для загрузки файла
def load_file(dbname, user, password):
    # Подключение к базе данных
    conn = psycopg2.connect(dbname=dbname, user=user, password=password)

    # Создание курсора
    cursor = conn.cursor()

    # Загрузка данных из Excel файла
    parent_directory = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
    file_path = os.path.join(parent_directory, 'Таблица книг.xlsx')
    df = pd.read_excel(file_path)

    # Добавление данных в таблицу library_book_category
    cursor.execute("INSERT INTO library_book_category (name_category) VALUES ('Художественная')")
    cursor.execute("INSERT INTO library_book_category (name_category) VALUES ('Учебная')")
    conn.commit()

    # Загрузка данных из DataFrame в таблицу library_book
    for index, row in df.iterrows():
        book_name = row['book_name']
        book_author = row['book_author']
        year_publish = int(row['year_publish'])
        book_description = row['book_description']
        num_copies = int(row['num_copies'])
        if pd.isnull(row['book_study_class']):
            book_study_class = None
        else:
            book_study_class = int(row['book_study_class'])
        book_category_id = int(row['book_category_id'])

        cursor.execute("INSERT INTO library_book (book_name, book_author, year_publish, book_description, num_copies, book_study_class, book_category_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (book_name, book_author, year_publish, book_description, num_copies, book_study_class, book_category_id))
    conn.commit()
    # Закрытие соединения
    cursor.close()
    conn.close()


def main():
    load_file(DB_NAME, DB_USER, DB_PASSWORD)

if __name__ == '__main__':
    main()
