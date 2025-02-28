from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiosend import CryptoPay
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
    await callback.message.answer("Выберите товар:", reply_markup=catalog_keyboard(products))
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
        await callback.message.answer("Ваша корзина пуста.")
        return

    total = sum(item[2] * item[3] for item in cart_items)
    cart_text = "🛒 Ваша корзина:\n\n"
    cart_text += "\n".join(f"{item[1]} x{item[3]} = ${item[2] * item[3]:.2f}" for item in cart_items)
    cart_text += f"\n\n💵 Итого: ${total:.2f}"

    await callback.message.answer(cart_text, reply_markup=cart_keyboard())
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
        await callback.message.answer(
            f"Заказ создан на сумму ${total:.2f}\n\nДля оплаты нажмите кнопку ниже.",
            reply_markup=payment_keyboard(invoice.mini_app_invoice_url)
        )
        invoice.poll(message=callback.message)
    except Exception as e:
        await callback.message.answer(f"Ошибка при создании платежа: {str(e)}")

# Обработчик очистки корзины
async def clear_cart_handler(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    clear_cart(user_id)
    await callback.message.answer("Корзина очищена.")

# Обработчик успешной оплаты
@cp.invoice_polling()
async def handle_payment(invoice: Invoice, message: Message) -> None:
    if invoice.status == "paid":
        await message.answer(f"✅ Оплата получена: {invoice.amount} {invoice.asset}")
        # Очистка корзины после оплаты
        clear_cart(message.from_user.id)
    else:
        await message.answer("❌ Оплата не прошла. Попробуйте еще раз.")