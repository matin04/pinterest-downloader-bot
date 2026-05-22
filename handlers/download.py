from aiogram import Router, types, F
from services.pinterest import get_pinterest_media
from database.db import get_user_language  
from utils.languages import TEXTS         
router = Router()

@router.message(F.text.contains("pinterest.com") | F.text.contains("pin.it"))
async def handle_pinterest_link(message: types.Message):
    url = message.text.strip()
    
    user_lang = await get_user_language(message.from_user.id)
    lang_texts = TEXTS[user_lang] 
    
    status_message = await message.answer(lang_texts["wait"])
    
    media = await get_pinterest_media(url)
    
    if not media:
        await status_message.edit_text(lang_texts["error_find"])
        return

    try:
        if media["type"] == "video":
            await message.reply_video(video=media["url"], caption=lang_texts["ready"])
        elif media["type"] == "image":
            await message.reply_photo(photo=media["url"], caption=lang_texts["ready"])
        
        await status_message.delete()
        
    except Exception as e:
        await status_message.edit_text(lang_texts["error_send"])
        print(f"Хатогии Телеграм: {e}")