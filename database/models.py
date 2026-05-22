from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    full_name: Mapped[str] = mapped_column(String(128))
    language: Mapped[str] = mapped_column(String(2), default="tg")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)