import sqlite3
from sqlite3 import Error

DATABASE = 'products.db'

def initiate_db():
    """
    Создаёт таблицу Products, если она ещё не существует.
    """
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL
            )
        ''')
        conn.commit()
        print("Таблица Products успешно создана или уже существует.")
    except Error as e:
        print(f"Ошибка при создании таблицы: {e}")
    finally:
        if conn:
            conn.close()

def get_all_products():
    """
    Возвращает все записи из таблицы Products.
    """
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Products')
        products = cursor.fetchall()
        return products
    except Error as e:
        print(f"Ошибка при получении продуктов: {e}")
        return []
    finally:
        if conn:
            conn.close()

def add_product(title, description, price):
    """
    Добавляет новый продукт в таблицу Products.
    """
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Products (title, description, price)
            VALUES (?, ?, ?)
        ''', (title, description, price))
        conn.commit()
        print(f"Продукт '{title}' успешно добавлен.")
    except Error as e:
        print(f"Ошибка при добавлении продукта: {e}")
    finally:
        if conn:
            conn.close()
