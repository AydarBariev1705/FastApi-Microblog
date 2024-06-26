from http import HTTPStatus

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from main.models.likes import Like
from main.models.tweets import Tweet
from main.models.users import User
from main.schemas import TweetSchema
from main.services.image import ImageService
from main.utils.exeptions import SpecialException


class TweetsService:
    """
    Класс для добавления, удаления и вывода твитов
    """

    @classmethod
    async def get_tweets(cls, user: User, session: AsyncSession):
        """
        Вывод последних твитов подписанных пользователей
        :param user: текущий пользователь
        :param session: асинхронная сессия
        :return: список твитов
        """
        logger.debug("Вывод твитов")
        query = (
            select(Tweet)
            .filter(Tweet.user_id.in_(user.id for user in user.following))
            .options(
                joinedload(Tweet.user),
                joinedload(Tweet.likes).subqueryload(Like.user),
                joinedload(Tweet.images),
            )
            .order_by(Tweet.likes_count.asc())
        )

        result = await session.execute(query)
        tweets = result.unique().scalars().all()

        return tweets

    @classmethod
    async def get_tweet(cls,
                        tweet_id: int,
                        session: AsyncSession,
                        ) -> Tweet | None:
        """
        Возврат твита по id
        :param tweet_id: id твита для поиска
        :param session: асинхронная сессия
        :return: твит
        """
        logger.debug(f"Поиск твита по id: {tweet_id}")

        query = select(Tweet).where(Tweet.id == tweet_id)
        tweet = await session.execute(query)

        return tweet.scalar_one_or_none()

    @classmethod
    async def create_tweet(
        cls, tweet: TweetSchema, current_user: User, session: AsyncSession
    ) -> Tweet:
        """
        Создание нового твита
        :param tweet: данные для нового твита
        :param current_user: текущий пользователь
        :param session: асинхронная сессия
        :return: новый твит
        """
        logger.debug("Добавление нового твита")

        new_tweet = Tweet(tweet_data=tweet.tweet_data, user_id=current_user.id)

        session.add(new_tweet)
        await session.flush()

        # Если есть изображение, то сохраняем его
        tweet_media_ids = tweet.tweet_media_ids

        if tweet_media_ids and tweet_media_ids != []:
            # Привязываем изображения к твиту
            await ImageService.update_images(
                tweet_media_ids=tweet_media_ids,
                tweet_id=new_tweet.id,
                session=session,
            )

        # Коммитим изменения в БД
        await session.commit()

        return new_tweet

    @classmethod
    async def delete_tweet(
        cls, user: User, tweet_id: int, session: AsyncSession
    ) -> None:
        """
        Удаление твита
        :param user: текущий пользователь
        :param tweet_id: id твита
        :param session: асинхронная сессия
        :return: None
        """
        logger.debug("Удаление твита")

        # Поиск твита по id
        tweet = await cls.get_tweet(tweet_id=tweet_id, session=session)

        if not tweet:
            logger.error("Твит не найден")

            raise SpecialException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Tweet not found",  # 404
            )

        else:
            if tweet.user_id != user.id:
                logger.error("Запрос на удаление чужого твита")

                raise SpecialException(
                    status_code=HTTPStatus.LOCKED,  # 423
                    detail="The tweet that is being accessed is locked",
                )

            else:
                # Удаляем изображения твита из файловой системы
                await ImageService.delete_images(tweet_id=tweet.id,
                                                 session=session,
                                                 )

                # Удаляем твит
                await session.delete(tweet)
                await session.commit()
