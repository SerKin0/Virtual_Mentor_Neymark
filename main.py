from aiogram.utils import executor
from aiogram import types

from creat_bot import dp
from handlers.add_function import addEvent
from handlers.creat_buttons import creatButtonMenu
from database.all_database import sqliteStart, messageLanguage

from menu import main_menu, menu, other_menu, meme_menu
from database import edit_user_data
from handlers import question_answers


# Функция запускающаяся при включении бота
def onStartUp():
    # Подключение базы данных
    sqliteStart()
    # Высылаем сообщение в консоль и в базу данных о запуске бота
    addEvent("The bot is turned on!", color_consol="red")


# Ответ на команду /start
@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer_chat_action(types.ChatActions.TYPING)
    await message.bot.send_message(message.from_user.id, messageLanguage("start_message", message),
                                   reply_markup=creatButtonMenu(message, "buttons_start_menu_private"))
    addEvent("Команда /start", message=message)  # Высылаем сообщение об ответе на команду /start


# Ответ на команду /help
@dp.message_handler(commands="help")
async def help(message: types.Message):
    await message.answer_chat_action(types.ChatActions.TYPING)
    await message.bot.send_message(message.from_user.id, messageLanguage("help_message", message))
    addEvent("Команда /help", message=message)


menu.register_handlers_other(dp)
main_menu.register_handlers_other(dp)
edit_user_data.register_handlers_other(dp)
question_answers.register_handlers_question_and_answer(dp)
other_menu.register_handlers_other(dp)
meme_menu.register_handlers_other(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=onStartUp())
