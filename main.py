import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from config import BOT_TOKEN
from handlers import cmd_start, show_catalog, add_to_cart_handler, show_cart, checkout, clear_cart_handler
from database import init_db, add_products

# Инициализация бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Регистрация хендлеров
dp.message.register(cmd_start, Command("start"))
dp.callback_query.register(show_catalog, F.data == "catalog")
dp.callback_query.register(add_to_cart_handler, F.data.startswith("product_"))
dp.callback_query.register(show_cart, F.data == "cart")
dp.callback_query.register(checkout, F.data == "checkout")
dp.callback_query.register(clear_cart_handler, F.data == "clear_cart")

# Инициализация базы данных
init_db()
add_products()

# Запуск бота
async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())