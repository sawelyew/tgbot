from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy import select, update
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class BotSettings(Base):
    __tablename__ = "bot_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(unique=True)
    value: Mapped[str] = mapped_column()


class Buttons(Base):
    __tablename__ = "buttons"
    id: Mapped[int] = mapped_column(primary_key=True)
    button_text: Mapped[str] = mapped_column(nullable=False)
    callback_data: Mapped[str] = mapped_column(nullable=False)
    button_order: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self):
        return f"{self.button_order}. {self.button_text}"


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def update_settings(key, value):
    async with async_session() as session:
        await session.execute(
            update(BotSettings).where(BotSettings.key == key).values(value=value)
        )
        await session.commit()


async def get_settings(key):
    async with async_session() as session:
        result = await session.execute(
            select(BotSettings.value).where(BotSettings.key == key)
        )
        return result.scalar_one_or_none()


async def get_buttons():
    async with async_session() as session:
        result = await session.execute(
            select(Buttons).order_by(Buttons.button_order)
        )
        return result.scalars().all()