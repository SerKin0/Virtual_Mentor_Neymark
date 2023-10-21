from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from handlers.add_function import addEvent, comparisonText
from handlers.creat_buttons import creatButtonMenu
from database.all_database import messageLanguage, get_user_info_from_database, get_user_data_from_database, add_user_to_database, sqlAllQuestion


# --------------------------------------Поиск вопросов-------------------------------------------------------------#
class FSMquestion(StatesGroup):
    question = State()


async def searchQuestion(message: types.Message):
    await FSMquestion.question.set()
    await message.answer(messageLanguage("write_question", message),
                         reply_markup=creatButtonMenu(message, other_buttons=["/Cancel"], row_width=3))
    addEvent("Пользователь вводит вопрос для поиска...", message=message)


async def writeVariantQuestion(message: types.Message, state: FSMContext):
    await message.answer_chat_action(types.ChatActions.TYPING)
    tmp = sqlAllQuestion("question, username")
    questions = [i[0] for i in tmp]
    questions = comparisonText(message.text, questions)
    if not tmp:
        await message.answer(messageLanguage("empty_question", message),
                             reply_markup=creatButtonMenu(message, "buttons_start_menu_private"))
        addEvent(f"Пользователь не нашел вопроса: '{message.text}'", message=message)
    else:
        usernames = [i[1] for i in tmp]
        for i in zip(questions, usernames):
            await message.answer(f"<code>{i[0]}</code>\n\n@ t.me/{i[1]}", disable_web_page_preview=True)
        await message.answer(messageLanguage("if_not_found_need_question", message),
                             reply_markup=creatButtonMenu(message, "buttons_start_menu_private"))
    await state.finish()


# --------------------------------------Регистрация и получения данных пользователя--------------------------------#
# Данные для регистрации пользователя
class FSMProfile(StatesGroup):
    first_name = State()
    second_name = State()
    username = ""
    age = State()
    id_telegram = 0
    description = State()
    level = 0
    language = State()


# Выводит данные пользователя из БД, если их нет, то начинает регистрацию
async def profile(message: types.Message):
    if get_user_info_from_database(message):
        await get_user_data_from_database(message)
        addEvent("Пользователь запросил данные по профилю", message=message)
    else:
        await FSMProfile.first_name.set()

        tmp = messageLanguage("start_registration", message)
        for i in tmp[:-1]:
            await message.answer(i)
        await message.answer(tmp[-1], reply_markup=creatButtonMenu(message, other_buttons=["/Cancel"], row_width=3))
        addEvent("Пользователь начал регистрацию...", message=message, color_consol="yellow")


# Получает имя пользователя для регистрации
async def downloudFirstName(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["first_name"] = message.text
    await FSMProfile.next()
    await message.bot.send_message(message.from_user.id, messageLanguage("write_second_name", message))
    addEvent("Пользователь ввёл своё имя", message=message, color_consol="yellow")


# Получает фамилию пользователя для регистрации
async def downloudSecondName(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["second_name"] = message.text
        data["username"] = message.chat.username
    await FSMProfile.next()
    await message.answer(messageLanguage("write_age", message))
    addEvent("Пользователь ввёл свою фамилию", message=message, color_consol="yellow")


# Получает возраст пользователя для регистрации
async def downloudAge(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["age"] = int(message.text)
        data["id_telegram"] = message.chat.id
    await FSMProfile.next()
    for tmp in messageLanguage("write_description", message):
        await message.bot.send_message(message.from_user.id, tmp)
    addEvent("Пользователь ввёл свой возраст", message=message, color_consol="yellow")


# Получает описание пользователя для регистрации
async def downloudDescription(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text
        data["level"] = 0
    await FSMProfile.next()
    await message.answer(messageLanguage("select_language", message),
                         reply_markup=creatButtonMenu(message, row_width=3,
                                                      other_buttons=("ru🇷🇺", "en🇺🇸", "fr🇫🇷", "hy🇦🇲", "de🇩🇪",
                                                                     "/Cancel")))
    addEvent("Пользователь ввёл своё описание", message=message, color_consol="yellow")


# Получает язык на котором бот будет работать
async def downloudLanguage(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["language"] = message.text[0:2]
        await message.answer(messageLanguage("finish_registration", message),
                             reply_markup=creatButtonMenu(message, "buttons_start_menu_private",
                                                          language=message.text[0:2]))

    addEvent("Пользователь создал новый аккаунт!!", message=message, color_consol="green")
    await add_user_to_database(state)
    await state.finish()


# Отменяет какие-либо регистрации и загрузки
async def close(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    addEvent("Пользователь отменил загрузку мема", message=message, color_consol="yellow")
    await message.answer("Ну окей", reply_markup=creatButtonMenu(message, "buttons_start_menu_private"))
    await state.finish()


async def linkGroup(message: types.Message):
    if get_user_info_from_database(message):
        await message.answer(messageLanguage("link_group", message))
        addEvent("Запрос ссылок", message=message)
    else:
        await message.answer(messageLanguage("error_not_login", message))
        addEvent("Запрос ссылок отменен", message=message)


# ---------------------------------------


def register_handlers_other(dp: Dispatcher):
    # Отмена регистраций и загрузок
    dp.register_message_handler(close, commands="Cancel", state='*')

    dp.register_message_handler(searchQuestion, lambda message: message.text == messageLanguage(
        "buttons_start_menu_private", message)[0])

    dp.register_message_handler(writeVariantQuestion, content_types="text", state=FSMquestion.question)

    # Информация пользователя/Начало регистрации
    dp.register_message_handler(profile, lambda message: message.text == messageLanguage(
        "buttons_start_menu_private", message)[1])
    # Регистрация - Имя
    dp.register_message_handler(downloudFirstName, content_types="text", state=FSMProfile.first_name)
    # Регистрация - Фамилия
    dp.register_message_handler(downloudSecondName, content_types="text", state=FSMProfile.second_name)
    # Регистрация - Возраст
    dp.register_message_handler(downloudAge, lambda message: message.text.isdigit(), state=FSMProfile.age)
    # Регистрация - Описание
    dp.register_message_handler(downloudDescription, content_types="text", state=FSMProfile.description)
    # Регистрация - Язык
    dp.register_message_handler(downloudLanguage,
                                lambda message: message.text in ("ru🇷🇺", "en🇺🇸", "fr🇫🇷", "hy🇦🇲", "de🇩🇪"),
                                state=FSMProfile.language)

    dp.register_message_handler(linkGroup, lambda message: message.text == messageLanguage(
        "buttons_start_menu_private", message)[2])
