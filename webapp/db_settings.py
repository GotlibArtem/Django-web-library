import psycopg2
from psycopg2 import Error
from webapp.settings import DB_NAME, DB_USER, DB_PASSWORD


def main() -> None:
    """
    Основная функция
    """
    try:
        # Подключение к БД
        connection = psycopg2.connect(dbname=DB_NAME,
                                      user=DB_USER,
                                      password=DB_PASSWORD)
        print('Подключение к БД PostgreSQL прошло успешно!')
        cursor = connection.cursor()
        # Добавление групп для пользователей
        query_1 = """INSERT INTO auth_group (name)
                     VALUES ('читатель'), ('библиотекарь')"""
        cursor.execute(query_1)
        # Добавление разрешений для групп
        query_2 = """INSERT INTO auth_group_permissions (group_id, permission_id)
                     VALUES (1, 28), (1, 32), (1, 40),
                     (2, 14), (2, 16), (2, 25), (2, 26), (2, 27), (2,28), (2, 29),
                     (2, 30), (2, 40), (2, 41), (2, 42), (2, 43), 
                    """
    except (Exception, Error) as error:
        print("Ошибка при работе с БД PostgreSQL:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с БД PostgreSQL завершено!")


if __name__ == "__main__":
    main()
