from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.db.connection import PLAYERS_TABLE
from app.db.limits import PLAYER_APPEARANCE_MAX_LIMIT


class Base(DeclarativeBase):
    pass


class PlayerORM(Base):
    __tablename__ = PLAYERS_TABLE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    appearance: Mapped[str] = mapped_column(
        String(PLAYER_APPEARANCE_MAX_LIMIT), nullable=False
    )
    race: Mapped[str] = mapped_column(String(50), nullable=False)
    class_name: Mapped[str] = mapped_column(String(50), nullable=False)
    size: Mapped[str] = mapped_column(String(20), nullable=False)
    alignment: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    abilities: Mapped[dict] = mapped_column(JSON, nullable=False)
    skills: Mapped[dict] = mapped_column(JSON, nullable=False)
