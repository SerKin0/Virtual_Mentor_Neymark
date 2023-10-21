from aiogram import types, Dispatcher
from handlers.add_function import addEvent
from database.all_database import messageLanguage


# Высылает информацию про разработчиков
async def informationAuthors(message: types.Message):
    await message.answer(messageLanguage("information_authors", message).format("https://t.me/BotsSerKin0"))
    addEvent("Пользователь запросил информацию про Разработчиков", message=message)


def register_handlers_other(dp: Dispatcher):
    # Информация про разработчиков
    dp.register_message_handler(informationAuthors,
                                lambda message: message.text == messageLanguage("buttons_other_menu", message)[1])
