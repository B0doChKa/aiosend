import asyncio
from dataclasses import dataclass
from typing import Dict, List

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from aiosend import CryptoPay
from aiosend.types import Invoice

BOT_TOKEN = "YOUR_BOT_TOKEN"
CRYPTO_PAY_TOKEN = "YOUR_CRYPTO_PAY_TOKEN"

bot = Bot(BOT_TOKEN)
cp = CryptoPay(CRYPTO_PAY_TOKEN)
router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    image_url: str

products: List[Product] = [
    Product(1, "Футболка", "Стильная футболка с логотипом", 10.99, "https://example.com/tshirt.jpg"),
    Product(2, "Кепка", "Спортивная кепка", 7.99, "https://example.com/cap.jpg"),
]

user_carts: Dict[int, Dict[int, int]] = {}

class OrderStates(StatesGroup):
    choosing_products = State()
    checkout = State()
    waiting_payment = State()
    order_complete = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Каталог товаров", callback_data="catalog")],
        [InlineKeyboardButton(text="🛒 Моя корзина", callback_data="cart")],
    ])
    await message.answer("👋 Добро пожаловать в наш магазин!", reply_markup=keyboard)

@router.callback_query(F.data == "catalog")
async def show_catalog(callback: CallbackQuery):
    keyboard = [[InlineKeyboardButton(text=f"{p.name} - ${p.price}", callback_data=f"product_{p.id}")] for p in products]
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    await callback.message.answer("Выберите товар из каталога:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()

@router.callback_query(F.data.startswith("product_"))
async def show_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = next((p for p in products if p.id == product_id), None)
    if not product:
        await callback.answer("Товар не найден")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить в корзину", callback_data=f"add_to_cart_{product.id}")],
        [InlineKeyboardButton(text="🔙 Назад к каталогу", callback_data="catalog")]
    ])
    await callback.message.answer(f"<b>{product.name}</b>\n\n{product.description}\n\n💵 Цена: ${product.price}", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    product_id = int(callback.data.split("_")[3])
    if user_id not in user_carts:
        user_carts[user_id] = {}
    if product_id in user_carts[user_id]:
        user_carts[user_id][product_id] += 1
    else:
        user_carts[user_id][product_id] = 1
    await callback.answer("Товар добавлен в корзину!")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Перейти в корзину", callback_data="cart")],
        [InlineKeyboardButton(text="🔙 Продолжить покупки", callback_data="catalog")]
    ])
    await callback.message.answer("Товар добавлен в корзину!", reply_markup=keyboard)

@router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_carts or not user_carts[user_id]:
        await callback.message.answer("Ваша корзина пуста.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍 Перейти в каталог", callback_data="catalog")]
        ]))
        await callback.answer()
        return
    total = 0
    cart_text = "🛒 <b>Ваша корзина:</b>\n\n"
    for product_id, quantity in user_carts[user_id].items():
        product = next((p for p in products if p.id == product_id), None)
        if product:
            item_total = product.price * quantity
            total += item_total
            cart_text += f"{product.name} x{quantity} = ${item_total:.2f}\n"
    cart_text += f"\n💵 <b>Итого: ${total:.2f}</b>"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", callback_data="checkout")],
        [InlineKeyboardButton(text="🗑 Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton(text="🔙 Продолжить покупки", callback_data="catalog")]
    ])
    await callback.message.answer(cart_text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in user_carts:
        user_carts[user_id] = {}
    await callback.message.answer("Корзина очищена.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Перейти в каталог", callback_data="catalog")]
    ]))
    await callback.answer()

@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id not in user_carts or not user_carts[user_id]:
        await callback.answer("Ваша корзина пуста")
        return
    await state.set_state(OrderStates.waiting_payment)
    total = 0
    for product_id, quantity in user_carts[user_id].items():
        product = next((p for p in products if p.id == product_id), None)
        if product:
            total += product.price * quantity
    try:
        invoice = await cp.create_invoice(total, "USDT")
        await state.update_data(invoice_id=invoice.invoice_id, total=total)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", url=invoice.mini_app_invoice_url)],
            [InlineKeyboardButton(text="🔙 Отменить", callback_data="cancel_payment")]
        ])
        await callback.message.answer(f"Заказ создан на сумму ${total:.2f}\n\nДля оплаты нажмите кнопку ниже.", reply_markup=keyboard)
        invoice.poll(message=callback.message)
    except Exception as e:
        await callback.message.answer(f"Ошибка при создании платежа: {str(e)}")
        await state.set_state(OrderStates.choosing_products)
    await callback.answer()

@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.choosing_products)
    await callback.message.answer("Платеж отменен.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Каталог товаров", callback_data="catalog")],
        [InlineKeyboardButton(text="🛒 Моя корзина", callback_data="cart")]
    ]))
    await callback.answer()

@cp.invoice_polling()
async def handle_payment(invoice: Invoice, message: Message):
    user_id = message.chat.id
    if user_id in user_carts:
        user_carts[user_id] = {}
    await message.answer("✅ <b>Оплата получена!</b>\n\nСпасибо за покупку!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Вернуться в магазин", callback_data="catalog")]
    ]))

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(
        dp.start_polling(bot),
        cp.start_polling(),
    )

if __name__ == "__main__":
    asyncio.run(main())
