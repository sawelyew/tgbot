from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import os
from states.state_group import OrderForm

order_router = Router()
CHAT_ID = os.getenv('CHAT_ID')


@order_router.message(OrderForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Что нужно сделать?")
    await state.set_state(OrderForm.task)


@order_router.message(OrderForm.task)
async def process_task(message: Message, state: FSMContext):
    await state.update_data(task=message.text)
    await message.answer("Оставьте контакт (телефон или email)")
    await state.set_state(OrderForm.contact)


@order_router.message(OrderForm.contact)
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
    await message.bot.send_message(chat_id=CHAT_ID, text=text)
    await state.clear()
