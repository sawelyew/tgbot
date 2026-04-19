from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Узнать цены", callback_data="prices")],
        [InlineKeyboardButton(text="Заказать", callback_data="order")],
        [InlineKeyboardButton(text="Контакты", callback_data="contacts")],
        [InlineKeyboardButton(text="FAQ", callback_data="faq")]
    ]
    )
    return keyboard


def get_admin_panel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Приветствие', callback_data='admin_panel_welcome_text')],
            [InlineKeyboardButton(text='Текущие кнопки', callback_data='admin_panel_buttons_menu')],
        ])


def get_admin_panel_welcome_text():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить текст', callback_data='admin_panel_change_welcome_text')],
        [InlineKeyboardButton(text='Добавить картинку', callback_data='admin_panel_add_picture_to_welcome_text')],
        [InlineKeyboardButton(text='Изменить прайс-лист', callback_data='admin_panel_change_price_list')],
        [InlineKeyboardButton(text='Предпросмотр', callback_data='admin_panel_welcome_text_preview')],
    ])
