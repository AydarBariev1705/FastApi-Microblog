from http import HTTPStatus

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from main.models.users import User
from main.services.user import UserService
from main.utils.exeptions import SpecialException


class FollowerService:
    """
    Класс для подписки и отписки между пользователями
    """

    @classmethod
    async def create_follower(
        cls, current_user: User, following_user_id: int, session: AsyncSession
    ) -> None:
        """
        Подписка на пользователя по id
        :param current_user: текущий пользователь
        :param following_user_id: id пользователя для подписки
        :param session: асинхронная сессия
        :return: None
        """
        logger.debug(
            f"Запрос подписки пользователя: {current_user.id} на id: {following_user_id}"
        )

        # Проверка, что текущий пользователь не подписывается сам на себя
        if await UserService.check_user_by_id(
            current_user_id=current_user.id, user_id=following_user_id
        ):
            logger.error("Попытка подписаться на самого себя")

            raise SpecialException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,  # 422
                detail="You can't subscribe to yourself",
            )

        # Поиск пользователя для подписки
        following_user = await UserService.get_user_by_id(
            user_id=following_user_id, session=session
        )

        if not following_user:
            logger.error(f"Пользователь с id: {following_user_id} не найден")

            raise SpecialException(
                status_code=HTTPStatus.NOT_FOUND,  # 404
                detail="The subscription user was not found",
            )

        if await cls.check_follower(
            current_user=current_user, following_user_id=following_user.id
        ):
            logger.warning("Подписка уже оформлена")

            raise SpecialException(
                status_code=HTTPStatus.LOCKED,  # 423
                detail="The user is already subscribed",
            )

        # Получаем текущего пользователя в текущей сессии
        # для записи нового подписчика
        current_user_db = await UserService.get_user_by_id(
            user_id=current_user.id, session=session
        )

        # Добавляем подписку текущему пользователю
        current_user_db.following.append(following_user)
        await session.commit()

        logger.info("Подписка оформлена")

    @classmethod
    async def check_follower(cls,
                             current_user: User,
                             following_user_id: int,
                             ) -> bool:
        """
        Проверка наличия подписки
        :param current_user: Текущий пользователь
        :param following_user_id: id пользователя для подписки
        :return: True - если пользователь уже подписан | False - если нет
        """
        # Проверяем, что текущего пользователя нет в числе подписчиков пользователя,
        # на которого он хочет подписаться
        return following_user_id in [
            following.id for following in current_user.following
        ]

    @classmethod
    async def delete_follower(
        cls, current_user: User, followed_user_id: int, session: AsyncSession
    ) -> None:
        """
        Отписка от пользователя
        :param current_user: текущий пользователь
        :param followed_user_id: id пользователя, от которого нужно отписаться
        :param session: асинхронная сессия
        :return: None
        """
        logger.debug(
            f"Пользователя с id: {current_user.id} пытается отписаться от id: {followed_user_id}"
        )

        # Проверка, что текущий пользователь не отписывается от самого себя
        if await UserService.check_user_by_id(
            current_user_id=current_user.id, user_id=followed_user_id
        ):
            logger.error("Попытка отписаться от самого себя")

            raise SpecialException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,  # 422
                detail="You can't unsubscribe from yourself",
            )

        # Поиск пользователя для отмены подписки
        followed_user = await UserService.get_user_by_id(
            user_id=followed_user_id, session=session
        )

        if not followed_user:
            logger.error(f"Не найден пользователь с id: {followed_user}")

            raise SpecialException(
                status_code=HTTPStatus.NOT_FOUND,  # 404
                detail="The user to cancel the subscription was not found",
            )

        if not await cls.check_follower(
            current_user=current_user, following_user_id=followed_user.id
        ):
            logger.warning("Подписка не обнаружена")

            raise SpecialException(
                status_code=HTTPStatus.LOCKED,  # 423
                detail="The user is not among the subscribers",
            )

        # Получаем текущего пользователя в текущей сессии для удаления подписки
        current_user_db = await UserService.get_user_by_id(
            user_id=current_user.id, session=session
        )

        # Отписка от пользователя
        current_user_db.following.remove(followed_user)
        await session.commit()

        logger.info("Пользователь успешно отписался")
