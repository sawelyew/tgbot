from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


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