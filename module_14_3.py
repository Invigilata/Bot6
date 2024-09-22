import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from crud_functions import initiate_db, get_all_products, add_product  # Импортируем функции из crud_functions.py

API_TOKEN = '7705325791:AAFMeqv8DKM1R7dLR0rabsGAFLlOHwO41uM'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Определение группы состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Обычная клавиатура
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(
    KeyboardButton('Рассчитать'),
    KeyboardButton('Информация'),
    KeyboardButton('Купить')  # Добавлена кнопка "Купить"
)

# Инлайн клавиатура для основного меню
inline_keyboard = InlineKeyboardMarkup(row_width=2)
inline_keyboard.add(
    InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
    InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
)

# Инлайн клавиатура с продуктами будет динамически создаваться из базы данных

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=keyboard)

@dp.message_handler(Text(equals='Рассчитать', ignore_case=True), state='*')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=inline_keyboard)

@dp.message_handler(Text(equals='Информация', ignore_case=True), state='*')
async def get_information(message: types.Message):
    await message.answer('Я бот для расчёта калорий по формуле Миффлина - Сан Жеора')

@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_text = "Формула Миффлина - Сан Жеора:\n10 х вес (кг) + 6,25 х рост (см) - 5 х возраст (г) - 161"
    await call.message.answer(formula_text)
    await call.answer()

@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await UserState.age.set()
    await call.message.answer('Введите свой возраст:')
    await call.answer()

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await UserState.growth.set()
        await message.answer('Введите свой рост (см):')
    except ValueError:
        await message.answer('Пожалуйста, введите корректный возраст.')

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    try:
        growth = int(message.text)
        await state.update_data(growth=growth)
        await UserState.weight.set()
        await message.answer('Введите свой вес (кг):')
    except ValueError:
        await message.answer('Пожалуйста, введите корректный рост.')

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        await state.update_data(weight=weight)
        data = await state.get_data()

        age = data['age']
        growth = data['growth']
        weight = data['weight']

        # Формула Миффлина - Сан Жеора:
        calories = 10 * weight + 6.25 * growth - 5 * age + 5

        await message.answer(f'Ваша норма калорий: {calories:.2f} ккал')
        await state.finish()
    except ValueError:
        await message.answer('Пожалуйста, введите корректный вес.')

# --- Новая функциональность "Купить" ---

@dp.message_handler(Text(equals='Купить', ignore_case=True), state='*')
async def get_buying_list(message: types.Message):
    products = get_all_products()
    if not products:
        await message.answer("В данный момент нет доступных продуктов для покупки.")
        return

    for product in products:
        product_id, title, description, price = product
        product_info = f"Название: {title} | Описание: {description} | Цена: {price}₽"
        await message.answer(product_info)
        await bot.send_photo(chat_id=message.chat.id, photo="https://novosibirsk.xbook.ru/upload/resize_cache/iblock/73b/1200_1200_140cd750bba9870f18aada2478b24840a/GeLq8gFs4vf1d.jpg", caption=title)

    # Создаем Inline клавиатуру динамически на основе продуктов
    products_inline_keyboard = InlineKeyboardMarkup(row_width=2)
    for product in products:
        product_id, title, _, _ = product
        products_inline_keyboard.add(
            InlineKeyboardButton(text=title, callback_data=f'product_buying_{product_id}')
        )

    await message.answer("Выберите продукт для покупки:", reply_markup=products_inline_keyboard)


@dp.callback_query_handler(lambda call: call.data and call.data.startswith('product_buying_'))
async def send_confirm_message(call: types.CallbackQuery):
    product_id = call.data.split('_')[-1]
    await call.message.answer(f"Вы успешно приобрели продукт с ID {product_id}!")
    await call.answer()


async def on_startup(dispatcher):
    # Инициализируем базу данных
    initiate_db()

    # Проверяем, есть ли уже продукты в базе
    products = get_all_products()
    if not products:
        # Если нет, добавляем 4 продукта
        add_product("Product1", "Описание 1", 100)
        add_product("Product2", "Описание 2", 200)
        add_product("Product3", "Описание 3", 300)
        add_product("Product4", "Описание 4", 400)
        print("Добавлены начальные продукты в базу данных.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)