from http import HTTPStatus

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from main.models.likes import Like
from main.services.tweet import TweetsService
from main.utils.exeptions import SpecialException


class LikeService:
    """
    Класс для проставления и удаления лайков
    """

    @classmethod
    async def like(cls,
                   tweet_id: int,
                   user_id: int,
                   session: AsyncSession,
                   ) -> None:
        """
        Лайк твита
        :param tweet_id: id твита для лайка
        :param user_id: id пользователя
        :param session: объект асинхронной сессии
        :return: None
        """
        logger.debug(f"Лайк твита №{tweet_id}")

        # Поиск твита по id
        tweet = await TweetsService.get_tweet(tweet_id=tweet_id,
                                              session=session,
                                              )

        if not tweet:
            logger.error("Твит не найден")

            raise SpecialException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Tweet not found",  # 404
            )

        if await cls.check_like_tweet(
            tweet_id=tweet_id, user_id=user_id, session=session
        ):
            logger.warning("Пользователь уже ставил лайк твиту")

            raise SpecialException(
                status_code=HTTPStatus.LOCKED,  # 423
                detail="The user has already liked this tweet",
            )
        tweet.likes_count += 1

        like_record = Like(user_id=user_id, tweets_id=tweet.id)

        session.add(like_record)
        await session.commit()

    @classmethod
    async def check_like_tweet(
        cls, tweet_id: int, user_id: int, session: AsyncSession
    ) -> Like | None:
        """
        Проверка ставил ли пользователь уже лайк
        :param tweet_id: id твита
        :param user_id: id пользователя
        :param session: асинхронная сессия
        """
        logger.debug("Поиск записи о лайке")

        query = select(Like).where(Like.user_id == user_id,
                                   Like.tweets_id == tweet_id,
                                   )
        like = await session.execute(query)

        return like.scalar_one_or_none()

    @classmethod
    async def dislike(cls,
                      tweet_id: int,
                      user_id: int,
                      session: AsyncSession,
                      ) -> None:
        """
        Удаление лайка
        :param tweet_id: id твита
        :param user_id: id пользователя
        :param session: асинхронная сессия
        :return: None
        """
        logger.debug(f"Убран лайк с твита №{tweet_id}")

        # Поиск твита по id
        tweet = await TweetsService.get_tweet(tweet_id=tweet_id,
                                              session=session,
                                              )

        if not tweet:
            logger.error("Твит не найден")

            raise SpecialException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Tweet not found",  # 404
            )

        # Ищем запись о лайке
        like_record = await cls.check_like_tweet(
            tweet_id=tweet_id, user_id=user_id, session=session
        )

        if like_record is None:
            logger.warning("Запись о лайке не найдена")

            raise SpecialException(
                status_code=HTTPStatus.LOCKED,  # 423
                detail="The user has not yet liked this tweet",
            )
        tweet.likes_count -= 1
        if tweet.likes_count < 0:
            tweet.likes_count = 0
        await session.delete(like_record)

        await session.commit()
