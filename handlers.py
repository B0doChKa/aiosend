from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiosend import CryptoPay
import asyncio
from aiosend.types import Invoice
from config import CRYPTO_PAY_TOKEN
from database import get_products, add_to_cart, get_cart, clear_cart
from keyboards import main_menu_keyboard, catalog_keyboard, cart_keyboard, payment_keyboard

cp = CryptoPay(CRYPTO_PAY_TOKEN)

# Обработчик команды /start
async def cmd_start(message: Message) -> None:
    await message.answer("👋 Добро пожаловать в магазин!", reply_markup=main_menu_keyboard())

# Обработчик каталога
async def show_catalog(callback: CallbackQuery) -> None:
    products = get_products()
    await callback.message.edit_text("Выберите товар:", reply_markup=catalog_keyboard(products))
    await callback.answer()

# Обработчик добавления товара в корзину
async def add_to_cart_handler(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    product_id = int(callback.data.split("_")[1])
    add_to_cart(user_id, product_id)
    await callback.answer("Товар добавлен в корзину!")

# Обработчик корзины
async def show_cart(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    cart_items = get_cart(user_id)
    if not cart_items:
        await callback.message.edit_text("Ваша корзина пуста.", reply_markup=main_menu_keyboard())
        return

    total = sum(item[2] * item[3] for item in cart_items)
    cart_text = "🛒 Ваша корзина:\n\n"
    cart_text += "\n".join(f"{item[1]} x{item[3]} = ${item[2] * item[3]:.2f}" for item in cart_items)
    cart_text += f"\n\n💵 Итого: ${total:.2f}"

    await callback.message.edit_text(cart_text, reply_markup=cart_keyboard())
    await callback.answer()

# Обработчик оплаты
async def checkout(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    cart_items = get_cart(user_id)
    if not cart_items:
        await callback.answer("Ваша корзина пуста")
        return

    total = sum(item[2] * item[3] for item in cart_items)
    try:
        invoice = await cp.create_invoice(total, "USDT")
        await callback.message.edit_text(
            f"Заказ создан на сумму ${total:.2f}\n\nДля оплаты нажмите кнопку ниже.",
            reply_markup=payment_keyboard(invoice.mini_app_invoice_url)
        )
        # Запуск проверки статуса оплаты
        await check_payment_status(invoice.invoice_id, callback.message)
    except Exception as e:
        await callback.message.edit_text(f"Ошибка при создании платежа: {str(e)}")

# Обработчик очистки корзины
async def clear_cart_handler(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    clear_cart(user_id)
    await callback.message.edit_text("Корзина очищена.", reply_markup=main_menu_keyboard())

# Обработчик кнопки "Назад"
async def back_to_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text("👋 Добро пожаловать в магазин!", reply_markup=main_menu_keyboard())
    await callback.answer()

# Обработчик кнопки "Отменить"
async def cancel_payment(callback: CallbackQuery) -> None:
    await callback.message.edit_text("❌ Оплата отменена.", reply_markup=main_menu_keyboard())
    await callback.answer()

# Функция для проверки статуса оплаты
async def check_payment_status(invoice_id: str, message: Message) -> None:
    while True:
        await asyncio.sleep(5)  # Проверяем статус каждые 5 секунд
        invoice = await cp.get_invoice(invoice_id)
        if invoice.status == "paid":
            await message.edit_text(f"✅ Оплата получена: {invoice.amount} {invoice.asset}")
            # Очистка корзины после оплаты
            clear_cart(message.from_user.id)
            break
        elif invoice.status in ["expired", "cancelled"]:
            await message.edit_text("❌ Оплата не прошла. Попробуйте еще раз.", reply_markup=main_menu_keyboard())
            break