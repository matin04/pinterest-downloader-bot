from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database.db import add_user, get_user_language, set_user_language
from utils.languages import TEXTS
from config import ADMIN_ID

router = Router()

def get_main_reply_keyboard(user_id: int):
    """Клавиатураи доимии поёни экран (барои админ 2 тугма, барои юзер 1 тугма)"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="🌐 Забон / Язык / Language")
    
    if user_id == ADMIN_ID:
        builder.button(text="🛠 Панели Админ")
        
    builder.adjust(1) 
    return builder.as_markup(resize_keyboard=True)

def get_lang_inline_keyboard():
    """Тугмаҳои inline барои интихоби забон"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🇹🇯 Тоҷикӣ", callback_data="set_lang_tg")
    builder.button(text="🇷🇺 Русский", callback_data="set_lang_ru")
    builder.button(text="🇬🇧 English", callback_data="set_lang_en")
    builder.adjust(1)
    return builder.as_markup()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )
    await message.answer(
        TEXTS["tg"]["choose_lang"], 
        reply_markup=get_lang_inline_keyboard()
    )

@router.message(F.text == "🌐 Забон / Язык / Language")
async def text_change_lang(message: types.Message):
    await message.answer(
        TEXTS["tg"]["choose_lang"], 
        reply_markup=get_lang_inline_keyboard()
    )

@router.callback_query(F.data.startswith("set_lang_"))
async def callback_set_language(callback: types.CallbackQuery):
    lang_code = callback.data.replace("set_lang_", "")
    await set_user_language(callback.from_user.id, lang_code)
    
    lang_texts = TEXTS[lang_code]
    user_name = callback.from_user.full_name
    
    builder = InlineKeyboardBuilder()
    builder.button(text=lang_texts["contact_btn"], url="https://t.me/beth_imeni")
    builder.adjust(1)
    
    await callback.answer(lang_texts["lang_changed"])
    
    await callback.message.answer(
        lang_texts["welcome"].format(name=user_name),
        reply_markup=get_main_reply_keyboard(callback.from_user.id)
    )
    await callback.message.delete()