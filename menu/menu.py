from aiogram import types, Dispatcher
from handlers.add_function import addEvent
from handlers.creat_buttons import creatButtonMenu
from database.all_database import messageLanguage


async def otherMenu(message: types.Message):
    await message.answer(messageLanguage("open_other_menu", message),
                         reply_markup=creatButtonMenu(message, "buttons_other_menu"))
    addEvent("Открываю меню Прочее", message=message)


async def startMenu(message: types.Message):
    await message.answer(messageLanguage("open_start_menu", message),
                         reply_markup=creatButtonMenu(message, "buttons_start_menu_private"))
    addEvent("Открываю Стартовое меню", message=message)


async def memsMenu(message: types.Message):
    await message.answer(messageLanguage("open_memes_menu", message),
                         reply_markup=creatButtonMenu(message, "buttons_meme_menu"))
    addEvent(text_event="Открываю меню Мемов", message=message)


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(otherMenu, lambda message:
    message.text == messageLanguage("buttons_start_menu_private", message)[-1])
    dp.register_message_handler(startMenu, lambda message:
    message.text == messageLanguage("buttons_other_menu", message)[-1] or
    message.text == messageLanguage("buttons_meme_menu", message)[-1])
    dp.register_message_handler(memsMenu, lambda message:
    message.text == messageLanguage("buttons_other_menu", message)[0])
