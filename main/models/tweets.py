import datetime
from typing import List

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from main.database import Base
from main.models.images import Image
from main.models.likes import Like


class Tweet(Base):
    """
    Модель твитов
    """

    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True,
                                    index=True,
                                    )
    tweet_data: Mapped[str] = mapped_column(String(280))
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow, nullable=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    images: Mapped[List["Image"]] = relationship(
        backref="tweet", cascade="all, delete-orphan"
    )
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[List["Like"]] = relationship(
        backref="tweet", cascade="all, delete-orphan"
    )

    # Отключаем проверку строк, тем самым убирая уведомление,
    # возникающее при удалении несуществующей строки
    __mapper_args__ = {"confirm_deleted_rows": False}
