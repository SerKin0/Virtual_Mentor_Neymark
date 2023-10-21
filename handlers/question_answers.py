from aiogram import types, Dispatcher
from dotenv import load_dotenv

from handlers.add_function import addEvent
from handlers.creat_buttons import creatButtonMenu

from database.all_database import get_user_info_from_database, messageLanguage
from database.all_database import sqlAddQuestion

import os


# Пишем что пользователь может ввести вопрос, при условии что он регистрировался
async def writeQuestion(message: types.Message):
    info = get_user_info_from_database(message)
    if not info:
        await message.answer(messageLanguage("error_not_login", message))
        addEvent("Пользователь пытался написать вопрос, но не был зарегистрирован", message=message, color_consol="red")
    else:
        tmp = message.text.replace("/question", "") if message.content_type not in ("photo", "video") else \
            message.caption.replace("/question", "")
        menu = "buttons_start_menu_private" if message.chat.type == "private" else None
        if tmp:
            await sqlAddQuestion(tmp, message)
            await message.reply(messageLanguage("finish_write_question", message),
                                reply_markup=creatButtonMenu(message, menu))
            load_dotenv(dotenv_path='.env')
            await message.forward(os.environ['ID_CHANEL'])
            addEvent(f"Пользователь задал вопрос: '{tmp}'", message=message, color_consol="green")
        else:
            await message.answer(messageLanguage("empty_question", message),
                                 reply_markup=creatButtonMenu(message, menu))
            addEvent("Пользователь ввел пустой вопрос", message=message)


def register_handlers_question_and_answer(dp: Dispatcher):
    dp.register_message_handler(writeQuestion, commands=["question"], commands_prefix="/!",
                                commands_ignore_caption=False, content_types=["photo", "text", "video"])
