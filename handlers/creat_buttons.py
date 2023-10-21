from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Кнопки "Стартового" меню
def creatButtonMenu(message, menu=None, row_width=2, other_buttons=None, language=None):
    if not menu and not other_buttons:
        return None
    else:

        buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
        from database.all_database import messageLanguage
        mass_buttons = messageLanguage(menu, message, language) if not other_buttons else other_buttons

        for i in mass_buttons[:-1]:
            buttons.insert(i)
        buttons.add(KeyboardButton(mass_buttons[-1]))
        return buttons
