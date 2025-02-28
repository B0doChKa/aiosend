import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiosend import CryptoPay
from config import BOT_TOKEN, CRYPTO_PAY_TOKEN
from keyboards import main_menu_keyboard, catalog_keyboard, cart_keyboard, payment_keyboard
from database import init_db, add_products, get_products, add_to_cart, get_cart, clear_cart

# Инициализация бота и CryptoPay
bot = Bot(BOT_TOKEN)
cp = CryptoPay(CRYPTO_PAY_TOKEN)
dp = Dispatcher()

# Инициализация базы данных
init_db()
add_products()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer("👋 Добро пожаловать в магазин!", reply_markup=main_menu_keyboard())

# Обработчик каталога
@dp.callback_query(lambda c: c.data == "catalog")
async def show_catalog(callback: types.CallbackQuery) -> None:
    products = get_products()
    await callback.message.answer("Выберите товар:", reply_markup=catalog_keyboard(products))
    await callback.answer()

# Обработчик добавления товара в корзину
@dp.callback_query(lambda c: c.data.startswith("product_"))
async def add_to_cart_handler(callback: types.CallbackQuery) -> None:
    user_id = callback.from_user.id
    product_id = int(callback.data.split("_")[1])
    add_to_cart(user_id, product_id)
    await callback.answer("Товар добавлен в корзину!")

# Обработчик корзины
@dp.callback_query(lambda c: c.data == "cart")
async def show_cart(callback: types.CallbackQuery) -> None:
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
@dp.callback_query(lambda c: c.data == "checkout")
async def checkout(callback: types.CallbackQuery) -> None:
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
@dp.callback_query(lambda c: c.data == "clear_cart")
async def clear_cart_handler(callback: types.CallbackQuery) -> None:
    user_id = callback.from_user.id
    clear_cart(user_id)
    await callback.message.answer("Корзина очищена.")

# Запуск бота
async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())