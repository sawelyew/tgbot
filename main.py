import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from database import init_database, update_settings, get_settings, get_buttons
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]

dp = Dispatcher()
class OrderForm(StatesGroup):
    name = State()
    task = State()
    contact = State()

class WelcomeTextForm(StatesGroup):
    text = State()
    photo = State()
    price_list = State()

def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Узнать цены", callback_data="prices")],
            [InlineKeyboardButton(text="Заказать", callback_data="order")],
            [InlineKeyboardButton(text="Контакты", callback_data="contacts")],
            [InlineKeyboardButton(text="FAQ", callback_data="faq")]
        ]
    )
    return keyboard


@dp.message(CommandStart())
async def start(message: Message):
    keyboard = get_start_keyboard()
    welcome_text = await get_settings("welcome_text")
    if welcome_text is None:
        welcome_text = "Добро пожаловать, выберите интересующее вас: "
    photo_id = await get_settings("welcome_photo_id")
    if photo_id:
        await message.answer_photo(caption=welcome_text, reply_markup=keyboard, photo=photo_id)
    else:
        await message.answer(text=welcome_text, reply_markup=keyboard)


@dp.callback_query(F.data == "prices")
async def process_prices(callback: CallbackQuery):
    await callback.answer()
    document_id = await get_settings("price_list_pdf_id")
    if document_id:
        await callback.message.answer_document(document=document_id, caption="Наш прайс-лист:")
    else:
        await callback.message.answer("Наш прайс-лист находится в разработке.")


@dp.callback_query(F.data == "contacts")
async def process_contacts(callback: CallbackQuery):
    await callback.answer()
    contacts = await get_settings("contacts")
    if contacts:
        await callback.message.answer(contacts)
    else:
        await callback.message.answer("Меню контактов находится в стадии разработки.")


@dp.callback_query(F.data == "faq")
async def process_faq(callback: CallbackQuery):
    await callback.answer()
    faq = await get_settings("faq")
    if faq:
        await callback.message.answer(text=faq)
    else:
        await callback.message.answer("FAQ находится в стадии разработки\n")


@dp.callback_query(F.data == "order")
async def start_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Отлично! Как вас зовут?")
    await state.set_state(OrderForm.name)

@dp.message(OrderForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Что нужно сделать?")
    await state.set_state(OrderForm.task)

@dp.message(OrderForm.task)
async def process_task(message: Message, state: FSMContext):
    await state.update_data(task=message.text)
    await message.answer("Оставьте контакт (телефон или email)")
    await state.set_state(OrderForm.contact)

@dp.message(OrderForm.contact)
async def process_contact(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get("name")
    task = user_data.get("task")
    contact = message.text
    await message.answer("✅ Спасибо! Заявка передана, свяжемся в течение 2 часов.")
    text = (f"📋 НОВАЯ ЗАЯВКА\n"
                  f"Имя: {name}\n"
                  f"Задача: {task}\n"
                  f"Контакт: {contact}\n"
                  f"Время (UTC+0): {message.date.time()}")
    await message.bot.send_message(chat_id=CHAT_ID,text=text)
    await state.clear()


# Admin Panel
@dp.message(Command("panel"), F.from_user.id.in_(ADMIN_IDS))
async def admin_panel(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Приветствие', callback_data='admin_panel_welcome_text')],
            [InlineKeyboardButton(text='Текущие кнопки', callback_data='admin_panel_buttons_menu')],
        ]
    )
    await message.answer(text="Вы вошли в админ-панель. Выберите что вас интересует: ", reply_markup=keyboard)


@dp.callback_query(F.data=='admin_panel_welcome_text', F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_welcoming_text(callback: CallbackQuery):
    await callback.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить текст', callback_data='admin_panel_change_welcome_text')],
        [InlineKeyboardButton(text='Добавить картинку', callback_data='admin_panel_add_picture_to_welcome_text')],
        [InlineKeyboardButton(text='Изменить прайс-лист', callback_data='admin_panel_change_price_list')],
        [InlineKeyboardButton(text='Предпросмотр', callback_data='admin_panel_welcome_text_preview')],
    ])
    welcome_text = await get_settings("welcome_text")
    if welcome_text is None:
        welcome_text = "Отсутствует"
    await callback.message.answer(text=f"Текущий текст: '{welcome_text}'", reply_markup=keyboard)

@dp.callback_query(F.data == 'admin_panel_change_welcome_text', F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_change_welcome_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Напишите текст, который хотите использовать как приветствие.")
    await state.set_state(WelcomeTextForm.text)

@dp.message(WelcomeTextForm.text, F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_process_welcome_text(message: Message, state: FSMContext):
    welcome_text = message.text
    await update_settings("welcome_text", welcome_text)
    await message.answer(f"Приветствие было успешно заменено на: '{welcome_text}' ✅")
    await state.clear()

@dp.callback_query(F.data == 'admin_panel_add_picture_to_welcome_text', F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_add_picture_to_welcome_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Отправьте картинку")
    await state.set_state(WelcomeTextForm.photo)

@dp.message(WelcomeTextForm.photo, F.from_user.id.in_(ADMIN_IDS), F.photo)
async def admin_panel_process_picture(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await update_settings("welcome_photo_id", photo_id)
    await message.answer("Картинка успешно обновлена ✅")
    await state.clear()

@dp.callback_query(F.data == 'admin_panel_change_price_list', F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_change_price_list(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Отправьте PDF документ с прайс-листом.")
    await state.set_state(WelcomeTextForm.price_list)

@dp.message(F.document, WelcomeTextForm.price_list, F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_process_price_list(message: Message, state: FSMContext):
    price_list = message.document.file_id
    await update_settings("price_list_pdf_id", price_list)
    await message.answer("Прайс-лист был успешно обновлен ✅")
    await state.clear()

@dp.callback_query(F.data == 'admin_panel_welcome_text_preview', F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_welcome_text_preview(callback: CallbackQuery):
    await callback.answer()
    welcome_text = await get_settings("welcome_text")
    photo_id = await get_settings("welcome_photo_id")
    if photo_id:
        await callback.message.answer_photo(photo=photo_id, caption=welcome_text)
    else:
        if welcome_text is None:
            welcome_text = "Добро пожаловать, выберите интересующее вас: "
        await callback.message.answer(text=welcome_text)

@dp.callback_query(F.data == 'admin_panel_buttons_menu', F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_buttons_menu(callback:CallbackQuery):
    await callback.answer()
    message_text = "Текущие кнопки: \n"
    buttons = await get_buttons()
    for btn in buttons:
        message_text += f"{btn.button_order}. {btn.button_text}\n"
    await callback.message.answer(text=message_text)


@dp.message(Command("test"), F.from_user.id.in_(ADMIN_IDS))
async def test_command(message: Message):
    photo_id = await get_settings("welcome_photo_id")
    welcome_text = await get_settings("welcome_text")
    if welcome_text is None:
        welcome_text = "Добро пожаловать, выберите интересующее вас: "
    if photo_id:
        await message.answer_photo(photo=photo_id, caption=welcome_text, reply_markup=get_start_keyboard())
    else:
        await message.answer(text=welcome_text, reply_markup=get_start_keyboard())


async def main() -> None:
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await init_database()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())