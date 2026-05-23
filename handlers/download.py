import os
import httpx
from aiogram import Router, types, F
from services.pinterest import get_pinterest_media
from database.db import get_user_language
from utils.languages import TEXTS
from aiogram.types import FSInputFile

router = Router()

# 1. Хендлер дилхоҳ паёмеро, ки калимаҳои Pinterest дорад, дастгир мекунад
@router.message(F.text.contains("pinterest.com") | F.text.contains("pin.it"))
async def handle_pinterest_link(message: types.Message):
    url = message.text.strip()
    
    # 2. Гирифтани забони корбар
    user_lang = await get_user_language(message.from_user.id)
    lang_texts = TEXTS[user_lang]

    # 3. ТЕКШИРУВИ ТОЗАГИИ ЛИНК:
    # Агар дар дохили паём пробел (space) бошад, ин маънои онро дорад, ки
    # корбар ба ғайр аз линк боз калимаҳои дигар навиштааст.
    if " " in url:
        await message.reply(lang_texts["invalid_link"])
        return # Корро ҳамин ҷо қатъ мекунем!

    status_message = await message.answer(lang_texts["wait"])
    
    # 4. Фиристодани линки тоза ба парсер
    media = await get_pinterest_media(url)
    
    if not media:
        await status_message.edit_text(lang_texts["error_find"])
        return

    # Номи файлҳои вақтинчагӣ
    file_path = f"temp_{message.from_user.id}_{media['type']}"
    if media["type"] == "video":
        file_path += ".mp4"
    else:
        file_path += ".jpg"

    try:
        # 5. Боргирии файл ба сервер
        async with httpx.AsyncClient() as client:
            response = await client.get(media["url"], timeout=60.0)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
            else:
                raise Exception("Боргирии файл нобарор шуд")

        # 6. Сохтани объекти файл
        telegram_file = FSInputFile(file_path)

        # 7. Фиристодани файл
        if media["type"] == "video":
            await message.reply_video(video=telegram_file, caption=lang_texts["ready"])
        elif media["type"] == "image":
            await message.reply_photo(photo=telegram_file, caption=lang_texts["ready"])
        
        await status_message.delete()
        
    except Exception as e:
        await status_message.edit_text(lang_texts["error_send"])
        print(f"Хатогӣ: {e}")
        
    finally:
        # 8. Тоза кардани кэш
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🔥 Кэш тоза шуд: {file_path}")
            except Exception as e:
                print(f"Хатогии кэш: {e}")