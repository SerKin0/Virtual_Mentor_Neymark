from aiogram import types, Dispatcher
from database.all_database import edit_user_data_in_database, messageLanguage


from handlers.creat_buttons import creatButtonMenu


async def commandsEditDataUser(message: types.Message):
    tmp = str(message.text).partition(" ")
    print(tmp)
    command, edited_text = tmp[0][1:], tmp[2]

    if (command == 'age') and (not edited_text.isdigit()) \
            or (command == 'language') and (not (edited_text[0:2] in ("ru", "en", "fr", "ar", "de"))):
        from handlers.add_function import addEvent
        addEvent(f"Пользователь не правильно вёл данные для исправления", message, color_consol="red")
        await message.answer(messageLanguage("error_data_entry", message),
                             reply_markup=creatButtonMenu(message, "buttons_start_menu_private"))
        return

    await edit_user_data_in_database(command, edited_text, message)


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(commandsEditDataUser,
                                commands=['first_name', 'second_name', 'age', 'description', 'language'])
