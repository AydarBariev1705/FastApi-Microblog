from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from collections.abc import Sequence

from main.database import async_session_maker
from main.models.users import User


class UserService:
    """
    Класс для получения данных о пользователе
    """

    @classmethod
    async def get_user_by_key(cls,
                              token: str,
                              session: AsyncSession,
                              ) -> User | None:
        """
        Получение пользователя по api-ключу
        :param token: api-ключ пользователя
        :param session: асинхронная сессия
        :return: Пользователь / False если пользователь не найден
        """
        logger.debug(f"Поиск пользователя по api-key: {token}")

        query = (
            select(User)
            .where(User.api_key == token)
            .options(selectinload(User.following),
                     selectinload(User.followers),
                     )
        )

        result = await session.execute(query)

        return result.scalar_one_or_none()

    @classmethod
    async def get_user_by_id(cls, user_id: int,
                             session: AsyncSession,
                             ) -> User | None:
        """
        Возврат объекта пользователя по id
        :param user_id: id пользователя
        :param session: асинхронная сессия
        :return: Пользователь / False если пользователь не найден
        """
        logger.debug(f"Поиск пользователя по id: {user_id}")

        query = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.following),
                     selectinload(User.followers),)
        )

        result = await session.execute(query)

        return result.scalar_one_or_none()

    @classmethod
    async def check_user_by_id(cls, current_user_id: int,
                               user_id: int,
                               ) -> bool:
        """
        Проверка, чтобы пользователь не подписался сам на себя.
        :param current_user_id: текущий пользователь
        :param user_id: id пользователя для проверки
        :return: True - user_id == current_user.id | False - id не совпадают
        """
        return current_user_id == user_id

    @classmethod
    async def check_users(cls) -> Sequence[User] | None:
        """
        Проверка наличия записей о пользователях в БД.
        :param session: асинхронная сессия
        :return: Пользователи
        """
        async with async_session_maker() as session:
            logger.debug("Проверка данных о пользователях в БД")

            query = select(User)
            result = await session.execute(query)

            return result.scalars().all()
