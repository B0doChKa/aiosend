import asyncio
from dataclasses import dataclass
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiosend import CryptoPay

BOT_TOKEN = "токен бота"
CRYPTO_PAY_TOKEN = "токен из @send"

bot = Bot(BOT_TOKEN)
cp = CryptoPay(CRYPTO_PAY_TOKEN)
router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dataclass
class Product:
    id: int
    name: str
    price: float

products = [Product(1, "Футболка", 10.99), Product(2, "Кепка", 7.99)]
user_carts = {}

class OrderStates(StatesGroup):
    choosing_products = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")]
    ])
    await message.answer("Добро пожаловать!", reply_markup=keyboard)

@router.callback_query(F.data == "catalog")
async def show_catalog(callback: CallbackQuery):
    keyboard = [[InlineKeyboardButton(text=f"{p.name} - ${p.price}", callback_data=f"product_{p.id}")] for p in products]
    await callback.message.answer("Каталог:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()

@router.callback_query(F.data.startswith("product_"))
async def show_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = next((p for p in products if p.id == product_id), None)
    if product:
        await callback.message.answer(f"{product.name} - ${product.price}")
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
