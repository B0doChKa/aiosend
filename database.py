import sqlite3
from config import DATABASE_NAME

# Инициализация базы данных
def init_db() -> None:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carts (
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                PRIMARY KEY (user_id, product_id)
            )
        """)
        conn.commit()

# Добавление товаров в базу данных
def add_products() -> None:
    products = [
        (1, "Футболка", 0.01),
        (2, "Кепка", 0.01),
    ]
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.executemany("INSERT OR IGNORE INTO products (id, name, price) VALUES (?, ?, ?)", products)
        conn.commit()

# Получение всех товаров
def get_products() -> list:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM products")
        return cursor.fetchall()

# Добавление товара в корзину
def add_to_cart(user_id: int, product_id: int) -> None:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO carts (user_id, product_id, quantity)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + 1
        """, (user_id, product_id))
        conn.commit()

# Получение корзины пользователя
def get_cart(user_id: int) -> list:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.price, c.quantity
            FROM carts c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
        """, (user_id,))
        return cursor.fetchall()

# Очистка корзины пользователя
def clear_cart(user_id: int) -> None:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM carts WHERE user_id = ?", (user_id,))
        conn.commit()
