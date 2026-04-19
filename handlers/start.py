from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from data.dbservice import get_settings
from keyboards.inline_kb import get_start_keyboard
from states.state_group import OrderForm

start_router = Router()


@start_router.message(CommandStart())
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


@start_router.callback_query(F.data == "prices")
async def process_prices(callback: CallbackQuery):
    await callback.answer()
    document_id = await get_settings("price_list_pdf_id")
    if document_id:
        await callback.message.answer_document(document=document_id, caption="Наш прайс-лист:")
    else:
        await callback.message.answer("Наш прайс-лист находится в разработке.")


@start_router.callback_query(F.data == "contacts")
async def process_contacts(callback: CallbackQuery):
    await callback.answer()
    contacts = await get_settings("contacts")
    if contacts:
        await callback.message.answer(contacts)
    else:
        await callback.message.answer("Меню контактов находится в стадии разработки.")


@start_router.callback_query(F.data == "faq")
async def process_faq(callback: CallbackQuery):
    await callback.answer()
    faq = await get_settings("faq")
    if faq:
        await callback.message.answer(text=faq)
    else:
        await callback.message.answer("FAQ находится в стадии разработки\n")


@start_router.callback_query(F.data == "order")
async def start_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Отлично! Как вас зовут?")
    await state.set_state(OrderForm.name)
