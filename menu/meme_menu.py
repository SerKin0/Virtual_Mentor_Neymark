from aiogram import types, Dispatcher
from handlers.add_function import addEvent
from handlers.creat_buttons import creatButtonMenu
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database.all_database import sqlAddCommand, sqlRead, messageLanguage, get_user_info_from_database


# -----------------------------------------Загрузка и выгрузка мемов---------------------------------------------------
class FSMMemes(StatesGroup):
    photo_or_video = State()
    text = State()
    name = ""


async def UploadMeme(message: types.Message):
    await FSMMemes.photo_or_video.set()
    addEvent("Пользователь загружает фото мема...", message=message, color_consol="yellow")
    await message.answer(messageLanguage("load_photo_or_video_meme", message),
                         reply_markup=creatButtonMenu(message, other_buttons=["Skip", "/Cancel"]))


async def loadPhotoOrVideoMeme(message: types.Message, state: FSMContext):
    if message.content_type == "photo":
        async with state.proxy() as data:
            data['photo_or_video'] = message.photo[0].file_id
    elif message.content_type == "video":
        async with state.proxy() as data:
            print(message)
            data['photo_or_video'] = message.video.thumb.file_id
    else:
        async with state.proxy() as data:
            data['photo_or_video'] = None
    await FSMMemes.next()
    await message.answer(messageLanguage("write_description_meme", message))
    addEvent("Пользователь загрузил фото, пишет описание...", message=message, color_consol="yellow")


async def loadDescriptionMeme(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["text"] = message.text if message.text != "Skip" else None
        info_user = get_user_info_from_database(message)
        if not info_user:
            data['name'] = f"t.me/{message.from_user.username} {message.from_user.full_name}"
        else:
            data['name'] = f"t.me/{info_user[2]} {info_user[0]} {info_user[1]}"
        flag = False if (data["text"] in (None, "")) and (data["photo_or_video"] in (None, "")) else True
    if not flag:
        await message.answer(messageLanguage("download_error", message),
                             reply_markup=creatButtonMenu(message, "buttons_meme_menu"))
        addEvent("Пользователь хотел загрузить мем, но оставил пустые поля", message=message, color_consol="red")
    else:
        addEvent("Пользователь загрузил мем!", message=message, color_consol="green")
        await message.answer(messageLanguage("finish_load_meme", message),
                             reply_markup=creatButtonMenu(message, "buttons_meme_menu"))
        await sqlAddCommand(state)
    await state.finish()
    print("finish")


async def randomMeme(message: types.Message):
    await message.answer_chat_action(types.ChatActions.TYPING)
    await sqlRead(message)
    addEvent("Пользователь загрузил Рандомный мем", message=message)


def register_handlers_other(dp: Dispatcher):
    # Загрузка новых мемов
    dp.register_message_handler(UploadMeme, lambda message: message.text == messageLanguage("buttons_meme_menu",
                                                                                            message)[0], state=None)
    # Загрузка новых мемов - Загрузка фото или видео
    dp.register_message_handler(loadPhotoOrVideoMeme, content_types=("photo", "video", "text"),
                                state=FSMMemes.photo_or_video)
    # Загрузка новых мемов - Загрузка описания мема
    dp.register_message_handler(loadDescriptionMeme, content_types="text", state=FSMMemes.text)
    # Рандомный мем
    dp.register_message_handler(randomMeme, lambda message: message.text == messageLanguage("buttons_meme_menu",
                                                                                            message)[1])
