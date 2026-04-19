from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from .base import engine, async_session
from .models import BotSettings, Buttons, Base


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def update_settings(key, value):
    async with async_session() as session:
        stmt = insert(BotSettings).values(key=key, value=value)

        stmt = stmt.on_conflict_do_update(
            index_elements=['key'],
            set_=dict(value=value)
        )

        await session.execute(stmt)
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
