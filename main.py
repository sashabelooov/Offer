import json
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from decouple import config
from datetime import datetime
from zoneinfo import ZoneInfo
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# local modules
from state import UserState
import keyboards as kb

TOKEN = config('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

with open("data.json", "r", encoding="utf-8") as file:
    translations = json.load(file)


def get_text(lang, category, key):
    return translations.get(lang, {}).get(category, {}).get(key, f"[{key}]")


@router.message(F.text.startswith("/start"))
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await bot.send_message(
        chat_id=user_id,
        text=translations['start'],
        reply_markup=kb.start_key(),
        parse_mode='HTML'
    )
    await state.set_state(UserState.language)


@router.message(UserState.language)
async def ask_phone(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text in {"🇺🇸 eng": "🇺🇸 eng", "🇺🇿 uz": "🇺🇿 uz", "🇷🇺 ru": "🇷🇺 ru", }:
        await state.update_data(language=message.text)
        data = await state.get_data()
        lang = data['language']
        await bot.send_message(chat_id=user_id, text=get_text(lang, 'message_text', 'phone'),
                               reply_markup=kb.ask_phone(lang))
        await state.set_state(UserState.phone)


@router.message(UserState.phone)
async def check_phone(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data['language']
    if message.contact:
        await state.update_data(phone=message.contact.phone_number)
        await bot.send_message(chat_id=user_id, text=get_text(lang, 'message_text', 'name'),
                               reply_markup=ReplyKeyboardRemove())
        await state.set_state(UserState.fio)
    else:
        text = message.text
        if message.text.startswith("+998") and len(text) == 13 and text[1:].isdigit():
            await state.update_data(phone=message.text)
            await bot.send_message(chat_id=user_id, text=get_text(lang, 'message_text', 'name'),
                                   reply_markup=ReplyKeyboardRemove())
            await state.set_state(UserState.fio)
        else:
            await bot.send_message(chat_id=user_id, text=get_text(lang, 'message_text', 'error_phone'))


@router.message(UserState.fio)
async def fio_user(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data['language']
    ok = True
    for i in message.text:
        if not i.isalpha():
            await bot.send_message(chat_id=user_id, text=get_text(lang, 'message_text', 'error_name'))
            ok = False
            break
    if ok:
        await state.update_data(user_name=message.text)
        await bot.send_message(chat_id=user_id, text=get_text(lang, 'message_text', 'offer'),
                               reply_markup=ReplyKeyboardRemove())
        await state.set_state(UserState.issue)





@router.message(UserState.issue)
async def issue(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data['language']
    msg_text = (
        f"{get_text(lang, 'message_text', 'confirmed_userinfo')}\n"
        f"{get_text(lang, 'message_text', 'conf_phone')} {data['phone']}\n"
        f"{get_text(lang, 'message_text', 'conf_name')} {data['user_name']}\n"
        f"{get_text(lang, 'message_text', 'offer_conf')} {message.text}"
    )

    await state.update_data(offer=message.text)
    await message.answer(text=msg_text, reply_markup=kb.conf(lang))
    await state.set_state(UserState.conf)


@router.message(UserState.conf)
async def conf(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data['language']
    if message.text == get_text(lang, "buttons", "confirm"):

        phone = data["phone"]
        name = data["user_name"]
        user_problem = "—"
        taklif = data["offer"]



        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds_example.json", scope)
        client = gspread.authorize(creds)

        sheet = client.open("Volna_Shikoyatlar_Takliflar").sheet1
        hozir = datetime.now(ZoneInfo("Asia/Tashkent"))

        url = f"https://t.me/{phone}"
        sana = hozir.strftime("%Y-%m-%d")  # '2025-07-31' formatida
        vaqt = hozir.strftime("%H:%M:%S")  # '15:56:22' formatida

        row = [url, phone, name, user_problem, taklif, sana, vaqt]
        sheet.append_row(row)


        await message.answer(
            text=get_text(lang, "message_text", "issue_received"),
            reply_markup=ReplyKeyboardRemove()
        )
        await bot.send_message(
            chat_id=user_id,
            text=translations['start'],
            reply_markup=kb.start_key(),
            parse_mode='HTML'
        )
        await state.set_state(UserState.language)
    elif message.text == get_text(lang, "buttons", "rejected"):
        await bot.send_message(
            chat_id=user_id,
            text=translations['start'],
            reply_markup=kb.start_key(),
            parse_mode='HTML'
        )
        await state.set_state(UserState.language)
