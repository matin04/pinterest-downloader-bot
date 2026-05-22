import asyncio
from aiogram import Router, types, Bot, F
from aiogram.filters import Command, or_f 
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_ID
from database.db import get_users_count, get_all_users, async_session
from database.models import User
from sqlalchemy import select

router = Router()

class AdminStates(StatesGroup):
    waiting_for_broadcast_text = State()
    waiting_for_user_id = State()
    waiting_for_single_text = State()

def get_admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Статистика", callback_data="admin_stats")
    builder.button(text="👥 Рӯйхати юзерҳо", callback_data="admin_users_list")
    builder.button(text="📢 Рассылка ба ҳама", callback_data="admin_broadcast")
    builder.button(text="👤 Паём ба як нафар", callback_data="admin_send_single")
    builder.button(text="⬅️ Ба ақиб (Баромадан)", callback_data="admin_exit")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Бекор кардан", callback_data="admin_back")
    return builder.as_markup()

@router.message(or_f(Command("admin"), F.text == "🛠 Панели Админ"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("🛠 **Панели Админ кушода шуд:**\n\nЛутфан функсияро интихоб кунед:", reply_markup=get_admin_keyboard())

# Қисмҳои дигари файл бе зор монда шаванд (онҳо дурустанд)...
@router.callback_query(F.data == "admin_back")
async def callback_back(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await callback.message.edit_text("🛠 **Панели Админ:**\n\nАмал бекор шуд. Функсияро интихоб кунед:", reply_markup=get_admin_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_exit")
async def callback_exit(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("👋 Шумо аз Панели Admin баромадед. Тугмаҳои асосӣ дар поёни экран дастрасанд.")
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def callback_stats(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    count = await get_users_count()
    await callback.message.edit_text(f"📊 **Статистикаи Бот:**\n\n👥 Шумораи умумии корбарон: **{count}**", reply_markup=get_admin_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_users_list")
async def callback_users_list(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
    text = "👥 **Рӯйхати корбарони бот:**\n\n"
    for idx, user in enumerate(users, 1):
        username = f"@{user.username}" if user.username else "Юзернейм надорад"
        text += f"{idx}. {user.full_name} ({username}) | ID: `{user.telegram_id}`\n"
    if len(text) > 4000:
        text = text[:3900] + "\n...ва ғайра"
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
async def callback_broadcast(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text("📝 **Матни паёмро нависед:**\n\nПаёми худро ба ин ҷо равон кунед:", reply_markup=get_cancel_keyboard())
    await state.set_state(AdminStates.waiting_for_broadcast_text)
    await callback.answer()

@router.message(AdminStates.waiting_for_broadcast_text)
async def process_broadcast(message: types.Message, state: FSMContext, bot: Bot):
    text_to_send = message.text
    await state.clear()
    users = await get_all_users()
    status_msg = await message.answer(f"Фиристодани паём ба {len(users)} корбар оғоз шуд... 🚀")
    success, failed = 0, 0
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=text_to_send)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
    await status_msg.answer(f"📢 **Рассылка ба охир расид:**\n\n✅ Муваффақ: {success}\n❌ Нобарор: {failed}", reply_markup=get_admin_keyboard())

@router.callback_query(F.data == "admin_send_single")
async def callback_single(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text("👤 **ID-и Телеграми он шахсро равон кунед:**", reply_markup=get_cancel_keyboard())
    await state.set_state(AdminStates.waiting_for_user_id)
    await callback.answer()

@router.message(AdminStates.waiting_for_user_id)
async def process_single_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Лутфан танҳо ID-и рақамиро биристед!", reply_markup=get_cancel_keyboard())
        return
    await state.update_data(target_user_id=int(message.text))
    await message.answer("📝 Акнун матни паёмро барои ин корбар нависед:", reply_markup=get_cancel_keyboard())
    await state.set_state(AdminStates.waiting_for_single_text)

@router.message(AdminStates.waiting_for_single_text)
async def process_single_text(message: types.Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    target_id = user_data.get("target_user_id")
    text_to_send = message.text
    await state.clear()
    try:
        await bot.send_message(chat_id=target_id, text=text_to_send)
        await message.answer("✅ Паём бо муваффақият ба он корбар фиристода шуд!", reply_markup=get_admin_keyboard())
    except Exception as e:
        await message.answer(f"❌ Хатогӣ ҳангоми фиристодан: {e}", reply_markup=get_admin_keyboard())