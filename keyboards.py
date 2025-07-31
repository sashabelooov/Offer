from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import json



with open("data.json", "r", encoding="utf-8") as file:
    translations = json.load(file)

def get_text(lang, category, key):
    return translations.get(lang, {}).get(category, {}).get(key, f"[{key}]")

def start_key():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=f"🇺🇸 eng"), KeyboardButton(text=f"🇺🇿 uz"),KeyboardButton(text=f"🇷🇺 ru"))
    keyboard.adjust(3)
    return keyboard.as_markup(resize_keyboard=True)


def ask_phone(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'contact'),request_contact=True))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)



def conf(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'confirm')), KeyboardButton(text=get_text(lang, 'buttons', 'rejected')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)


def back(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
                 KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)