import tkinter as tk
from tkinter import filedialog, StringVar, Entry
import pandas as pd
import psycopg2


# Функция для загрузки файла
def load_file(dbname, username, password):
    # Подключение к базе данных
    conn = psycopg2.connect(dbname=dbname, user=username, password=password)

    # Создание курсора
    cursor = conn.cursor()

    # Загрузка данных из Excel файла
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
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
    # Создание окна tkinter
    root = tk.Tk()

    # Создание полей для ввода данных подключения к базе данных
    dbname_var = StringVar()
    dbname_label = tk.Label(root, text="Имя БД:")
    dbname_label.pack()
    dbname_entry = Entry(root, textvariable=dbname_var)
    dbname_entry.pack()

    username_var = StringVar()
    username_label = tk.Label(root, text="Имя пользователя:")
    username_label.pack()
    username_entry = Entry(root, textvariable=username_var)
    username_entry.pack()

    password_var = StringVar()
    password_label = tk.Label(root, text="Пароль:")
    password_label.pack()
    password_entry = Entry(root, textvariable=password_var, show='*')
    password_entry.pack()

    # Создание кнопки для загрузки файла
    load_file_button = tk.Button(root,
                                text="Выберите excel файл с книгами",
                                command=lambda: load_file(
                                    dbname_var.get(),
                                    username_var.get(),
                                    password_var.get()
                                ))
    load_file_button.pack()

    root.mainloop()


if __name__ == '__main__':
    main()
