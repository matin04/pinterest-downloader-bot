import os
import httpx
from aiogram import Router, types, F
from services.pinterest import get_pinterest_media
from database.db import get_user_language
from utils.languages import TEXTS
from aiogram.types import FSInputFile  # Барои фиристодани файлҳо аз сервер

router = Router()

@router.message(F.text.contains("pinterest.com") | F.text.contains("pin.it"))
async def handle_pinterest_link(message: types.Message):
    url = message.text.strip()
    
    # 1. Гирифтани забони корбар
    user_lang = await get_user_language(message.from_user.id)
    lang_texts = TEXTS[user_lang]
    
    status_message = await message.answer(lang_texts["wait"])
    
    # 2. Гирифтани линки мустақим аз Pinterest
    media = await get_pinterest_media(url)
    
    if not media:
        await status_message.edit_text(lang_texts["error_find"])
        return

    # Номи файлҳои вақтинчагӣ дар сервер
    file_path = f"temp_{message.from_user.id}_{media['type']}"
    if media["type"] == "video":
        file_path += ".mp4"
    else:
        file_path += ".jpg"

    try:
        # 3. Боргирии файл аз интернет ба сервери мо (Вақтинча)
        async with httpx.AsyncClient() as client:
            response = await client.get(media["url"], timeout=60.0)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
            else:
                raise Exception("Боргирии файл аз Pinterest нобарор шуд")

        # 4. Сохтани объекти файл барои Телеграм
        telegram_file = FSInputFile(file_path)

        # 5. Фиристодани файл ба корбар
        if media["type"] == "video":
            await message.reply_video(video=telegram_file, caption=lang_texts["ready"])
        elif media["type"] == "image":
            await message.reply_photo(photo=telegram_file, caption=lang_texts["ready"])
        
        await status_message.delete()
        
    except Exception as e:
        await status_message.edit_text(lang_texts["error_send"])
        print(f"Хатогӣ ҳангоми кор бо файл: {e}")
        
    finally:
        # 6. АВТОМАТСОЗИИ ТОЗАКУНИИ КЭШ (МАҲЗ ҲАМИН ҶО!) ✅
        # Блоки finally 100% иҷро мешавад, ҳатто агар хатогӣ шуда бошад ҳам!
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🔥 Кэш тоза шуд: Файли вақтинчагии {file_path} аз сервер нест карда шуд!")
            except Exception as e:
                print(f"Хатогӣ ҳангоми тоза кардани кэш: {e}")