import sqlite3 as sq
import json

# -------------------------------------------Создание Базы Данных------------------------------------------#
import handlers.creat_buttons


def sqliteStart():
    global base, cur

    base = sq.connect('database/database.db')  # Подключаем файл с базой данных
    cur = base.cursor()

    # Таблица с историей действий
    base.execute('CREATE TABLE IF NOT EXISTS history(type_chat TEXT, time TEXT, id_user INTEGER, first_name TEXT, '
                 'last_name TEXT, username TEXT, start_string TEXT, end_string TEXT, text_event TEXT)')
    # Таблица с данными пользователей
    base.execute('CREATE TABLE IF NOT EXISTS profile(first_name TEXT, second_name TEXT, username TEXT, age INTEGER, '
                 'id_telegram INTEGER PRIMARY KEY, description TEXT, level INTEGER, language TEXT)')
    # Таблица с вопросами пользователей
    base.execute('CREATE TABLE IF NOT EXISTS question(id_question INTEGER PRIMARY KEY, id_telegram INTEGER, '
                 'username TEXT, question TEXT)')
    # Таблица с мемами
    base.execute('CREATE TABLE IF NOT EXISTS meme(id INTEGER PRIMARY KEY AUTOINCREMENT,img TEXT, text TEXT, name TEXT)')

    # Обновление Базы Данных
    base.commit()


# -------------------------------------Регистрация Действий Пользователей----------------------#
def add_new_event_to_database(type_chat, text_event, time, id_user, first_name, last_name, username, start_string,
                              end_string):
    # Запись в БД с историей действий нового события
    cur.execute('INSERT INTO history VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                tuple((type_chat, time, id_user, first_name, last_name, username, start_string, end_string,
                       text_event)))
    # Сохранение нового события
    base.commit()


# -------------------------------------Работа С Профилями Пользователей------------------------#
# Создание новой строки с данными пользователя
async def add_user_to_database(state):
    async with state.proxy() as data:
        # Запись в БД с профилями пользователей новый аккаунт
        cur.execute('INSERT INTO profile VALUES (?, ?, ?, ?, ?, ?, ?, ?)', tuple(data.values()))
        # Сохранение нового профиля
        base.commit()


# Высылает данные профиля пользователя, если их нет, то выводит None
async def get_user_data_from_database(message=None, id_user=None):
    user_info = get_user_info_from_database(message, id_user)
    # Если данные о пользователе есть, то...
    if user_info:
        # Получаем из .json файла текст сообщения, в которое будет вставляться такие данные как:
        # [0] - Имя, [1] - Фамилия, [3] - Возраст, [5] - Описание пользователя, [6] - Статус/Уровень пользователя,
        # [7] - Язык пользователя
        string = str(messageLanguage("profile_data", message)) \
            .format(user_info[0], user_info[1], user_info[3], user_info[5],
                    messageLanguage("levels_users", message)[user_info[6]], user_info[7])

        # Если не был введен ID пользователя, то получаем через message
        id_user = id_user if id_user else message.from_user.id

        # Высылаем сообщение с Данными Пользователя, только в Личные Сообщения
        await message.bot.send_message(id_user, string)
        # Высылаем сообщение с инструкцией для изменения данных пользователей в Личные Сообщения
        await message.bot.send_message(id_user, messageLanguage("edit_profile", message))
    # Иначе, возвращаем None
    else:
        return None


# Возвращает массив информации о запрошенном пользователе
def get_user_info_from_database(message=None, id_user=None):
    # Если не был введен ID пользователя, то получаем через message
    id_user = message.from_user.id if not id_user else id_user

    # Получаем данные о пользователе по его id в телеграм и записываем в user_info
    user_info = cur.execute(f"SELECT * FROM profile WHERE id_telegram = {id_user}").fetchall()

    # Если есть данные о пользователе, то возвращаем массив, иначе ничего (None)
    return user_info[0] if user_info else None


# Изменяет значения в БД пользователей и их профилей
async def edit_user_data_in_database(commands, edited_information, message, id_user=None):
    # Подключаем функцию для объявления события
    from handlers.add_function import addEvent

    # Если не был введен ID пользователя, то получаем через message
    id_user = message.from_user.id if not id_user else id_user

    # Если нет информации о пользователе, то...
    if not get_user_info_from_database(id_user=id_user):
        # Выводим сообщение, что пользователь не зарегистрирован в системе, поэтому не может изменить данные
        await message.answer(messageLanguage("error_edit_data_not_reg", message))

        addEvent(f"Пользователь решил изменить профиля, но он не зарегистрирован", message,
                 color_consol="red")
        return

    cur.execute(f'UPDATE profile SET "{commands}" = "{edited_information}" WHERE id_telegram = {id_user}')
    base.commit()
    await message.answer(messageLanguage("edited_data_user", message),
                         reply_markup=handlers.creat_buttons.creatButtonMenu(message, "buttons_start_menu_private"))
    addEvent(f"Пользователь изменил данные профиля: '{commands}' на '{edited_information}'", message=message,
             color_consol="yellow")


# -------------------------------------Функции Вопрос-Ответ------------------------------------#
# Сохраняет вопрос в таблицу
async def sqlAddQuestion(question, message=None, id_question=None, id_telegram=None, username=None):
    if message:
        id_question = message.message_id if not id_question else id_question
        id_telegram = message.from_user.id if not id_telegram else id_telegram
        username = message.from_user.username if not username else username
    array = (id_question, id_telegram, username, question)  # Добавляем во вводимые данные id пользователя и вопрос
    # Записываем в таблицу новый вопрос
    cur.execute('INSERT INTO question VALUES (?, ?, ?, ?)', array)
    # Сохраняем изменения
    base.commit()


def sqlAllQuestion(column="*"):
    return cur.execute(f"SELECT {column} FROM question").fetchall()


# ----------------------------------------------Мемы-------------------------------------------#
variants = []
counter = 0


async def sqlAddCommand(state):
    async with state.proxy() as data:
        print(type(data))
        cur.execute('INSERT INTO meme VALUES (?, ?, ?, ?)', tuple([None] + list(data.values())))
        base.commit()


async def sqlRead(message):
    try:
        global variants, counter
        # Запрашиваем количество мемов в Базе Данных
        count_string = cur.execute('SELECT COUNT(id) FROM meme').fetchall()[0][0]
        # Если мы прошлись по всем мемами (либо программа только запустилась), то...
        if counter % count_string == 0:
            # Подключаем функцию для перемешивания случайным образом
            from random import shuffle
            # Если массив пустой ИЛИ длина нынешнего массива вариантов не равна количеству мемов в БД, то...
            if not variants or len(variants) != count_string:
                # Записываем в БД массив с ID мемов
                variants = list(map(lambda x: x[0], cur.execute("SELECT id FROM meme").fetchall()))
            # Перемешиваем массив
            shuffle(variants)

        # Выгружаем из БД с мемами строку по ID
        meme = cur.execute(f'SELECT * FROM meme WHERE id = {variants[counter % len(variants)]}').fetchall()[0]

        # Переходим на следующий мем
        counter += 1

        # Если нет ссылки на изображения, то...
        if not meme[1]:
            # Выводим сообщение только с описанием и ссылкой на автора мема
            await message.answer(f"{meme[1]}\n\n<i>@ {meme[2]}</i>")
        # Иначе...
        else:
            # Записываем описание мема
            description = f"{meme[2]}\n\n" if meme[2] else ""
            # Высылаем фото мема, описание и автора
            await message.bot.send_photo(message.chat.id, meme[1], f"{description}<i>@ {meme[3]}</i>")
    except BaseException:
        # Подключаем функцию для объявления событий
        from handlers.add_function import addEvent
        await message.answer("Прости, мемов пока нет...")
        addEvent("НЕТ МЕМОВ!", start_string="SYSTEM EVENT: ", color_consol="yellow", message=message)


# -------------------------------------Дополнительные Функции----------------------------------#
# Функция возвращает язык пользователя, если он не зарег., то возвращается язык по стране номера телефона
def languageUser(message):
    tmp = cur.execute(f"SELECT language FROM profile WHERE id_telegram = {message.from_user.id}").fetchall()
    return message.from_user.language_code if not tmp else tmp[0][0]


# Функция возвращает текст сообщения на определенном языке
def messageLanguage(text_message, message=None, language=None):
    language = languageUser(message) if not language else language
    with open(f"languages/{language}.json", encoding='utf-8') as f:
        return json.load(f)[text_message]


# Запрашивает данные из любой базы данных
async def data_from_database(name_database, column='*', command=None):
    return cur.execute(f'SELECT {column} FROM {name_database} {command}').fetchall()[0]
