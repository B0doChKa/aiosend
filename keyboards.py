from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Клавиатура для главного меню
def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")],
    ])

# Клавиатура для каталога
def catalog_keyboard(products: list) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=f"{p[1]} - ${p[2]}", callback_data=f"product_{p[0]}")] for p in products]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для корзины
def cart_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", callback_data="checkout")],
        [InlineKeyboardButton(text="🗑 Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")],
    ])

# Клавиатура для оплаты
def payment_keyboard(invoice_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", url=invoice_url)],
        [InlineKeyboardButton(text="🔙 Отменить", callback_data="cancel_payment")],
    ])