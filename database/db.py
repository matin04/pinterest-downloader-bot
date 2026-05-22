from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, func
from database.models import Base, User

DATABASE_URL = "sqlite+aiosqlite:///bot_database.db"
engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    """Сохтани таблитсаҳо агар мавҷуд набошанд"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def add_user(telegram_id: int, username: str | None, full_name: str):
    """Илова кардани корбари нав ба база, агар аллакай мавҷуд набошад"""
    async with async_session() as session:
        async with session.begin():
            
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()
            
            if not user:
                new_user = User(
                    telegram_id=telegram_id,
                    username=username,
                    full_name=full_name,
                    language="tg"
                )
                session.add(new_user)
                await session.commit()

async def get_users_count() -> int:
    """Гирифтани шумораи умумии корбарон барои статистика"""
    async with async_session() as session:
        result = await session.execute(select(func.count(User.telegram_id)))
        return result.scalar() or 0

async def get_all_users():
    """Гирифтани рӯйхати ҳамаи корбарон барои рассылка"""
    async with async_session() as session:
        result = await session.execute(select(User.telegram_id))
        return result.scalars().all()

async def get_user_language(telegram_id: int) -> str:
    """Гирифтани забони корбар"""
    async with async_session() as session:
        result = await session.execute(select(User.language).where(User.telegram_id == telegram_id))
        lang = result.scalar_one_or_none()
        return lang or "tg"

async def set_user_language(telegram_id: int, lang: str):
    """Иваз кардани забони корбар"""
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()
            if user:
                user.language = lang
                await session.commit()