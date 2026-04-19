from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from data.dbservice import update_settings, get_settings, get_buttons
from keyboards.inline_kb import get_admin_panel_keyboard, get_admin_panel_welcome_text
import os
from states.state_group import WelcomeTextForm

admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
admin_router = Router()


@admin_router.message(Command("panel"), F.from_user.id.in_(ADMIN_IDS))
async def admin_panel(message: Message):
    keyboard = get_admin_panel_keyboard()
    await message.answer(text="Вы вошли в админ-панель. Выберите что вас интересует: ", reply_markup=keyboard)


@admin_router.callback_query(F.data == 'admin_panel_welcome_text', F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_welcoming_text(callback: CallbackQuery):
    await callback.answer()
    keyboard = get_admin_panel_welcome_text()
    welcome_text = await get_settings("welcome_text")
    if welcome_text is None:
        welcome_text = "Отсутствует"
    await callback.message.answer(text=f"Текущий текст: '{welcome_text}'", reply_markup=keyboard)


@admin_router.callback_query(F.data == 'admin_panel_change_welcome_text', F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_change_welcome_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Напишите текст, который хотите использовать как приветствие.")
    await state.set_state(WelcomeTextForm.text)


@admin_router.message(WelcomeTextForm.text, F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_process_welcome_text(message: Message, state: FSMContext):
    welcome_text = message.text
    await update_settings("welcome_text", welcome_text)
    await message.answer(f"Приветствие было успешно заменено на: '{welcome_text}' ✅")
    await state.clear()


@admin_router.callback_query(F.data == 'admin_panel_add_picture_to_welcome_text', F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_add_picture_to_welcome_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Отправьте картинку")
    await state.set_state(WelcomeTextForm.photo)


@admin_router.message(WelcomeTextForm.photo, F.from_user.id.in_(ADMIN_IDS), F.photo)
async def admin_panel_process_picture(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await update_settings("welcome_photo_id", photo_id)
    await message.answer("Картинка успешно обновлена ✅")
    await state.clear()


@admin_router.callback_query(F.data == 'admin_panel_change_price_list', F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_change_price_list(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Отправьте PDF документ с прайс-листом.")
    await state.set_state(WelcomeTextForm.price_list)


@admin_router.message(F.document, WelcomeTextForm.price_list, F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_process_price_list(message: Message, state: FSMContext):
    price_list = message.document.file_id
    await update_settings("price_list_pdf_id", price_list)
    await message.answer("Прайс-лист был успешно обновлен ✅")
    await state.clear()


@admin_router.callback_query(F.data == 'admin_panel_welcome_text_preview', F.from_user.id.in_(ADMIN_IDS))
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


@admin_router.callback_query(F.data == 'admin_panel_buttons_menu', F.from_user.id.in_(ADMIN_IDS))
async def admin_panel_buttons_menu(callback: CallbackQuery):
    await callback.answer()
    message_text = "Текущие кнопки: \n"
    buttons = await get_buttons()
    if buttons:
        for btn in buttons:
            message_text += f"{btn.button_order}. {btn.button_text}\n"
    else:
        buttons = ['Узнать цены', 'Заказать', 'Контакты', 'FAQ']
        for i in range(len(buttons)):
            message_text += f"{i+1}. {buttons[i]}\n"
    await callback.message.answer(text=message_text)
