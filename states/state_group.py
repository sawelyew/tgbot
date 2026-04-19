from aiogram.fsm.state import StatesGroup, State


class OrderForm(StatesGroup):
    name = State()
    task = State()
    contact = State()


class WelcomeTextForm(StatesGroup):
    text = State()
    photo = State()
    price_list = State()
