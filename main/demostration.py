import asyncio

from loguru import logger

from main.database import Base, async_session_maker, engine
from main.models.images import Image
from main.models.likes import Like
from main.models.tweets import Tweet
from main.models.users import User

users = [
    {
        "username": "Test_user",
        "api_key": "test",
    },
    {
        "username": "Test_user2",
        "api_key": "test2",
    },
    {
        "username": "Test_user3",
        "api_key": "test3",
    },
]

images2 = [
    {
        "tweet_id": 1,
        "path_media": "images/tweets/img/1.jpg",
    },
    {
        "tweet_id": 4,
        "path_media": "images/tweets/img/3.jpg",
    },
    {
        "tweet_id": 6,
        "path_media": "images/tweets/img/5.jpg",
    },
    {
        "tweet_id": 6,
        "path_media": "images/tweets/img/7.jpg",
    },
    {
        "tweet_id": 6,
        "path_media": "images/tweets/img/2.jpg",
    },
    {
        "tweet_id": 8,
        "path_media": "images/tweets/img/4.jpg",
    },
    {
        "tweet_id": 11,
        "path_media": "images/tweets/img/6.jpg",
    },
    {
        "tweet_id": 10,
        "path_media": "images/tweets/img/8.jpg",
    },
]
images = [
    {
        "tweet_id": 1,
        "path_media": "1.jpg",
    },
    {
        "tweet_id": 4,
        "path_media": "3.jpg",
    },
    {
        "tweet_id": 6,
        "path_media": "5.jpg",
    },
    {
        "tweet_id": 6,
        "path_media": "7.jpg",
    },
    {
        "tweet_id": 6,
        "path_media": "2.jpg",
    },
    {
        "tweet_id": 8,
        "path_media": "4.jpg",
    },
    {
        "tweet_id": 11,
        "path_media": "6.jpg",
    },
    {
        "tweet_id": 10,
        "path_media": "8.jpg",
    },
]

tweets = [
    {
        "tweet_data": "Test_tweet 1",
        "user_id": 1,
        "likes_count": 3,
    },
    {
        "tweet_data": "Test_tweet 2",
        "user_id": 2,
        "likes_count": 2,
    },
    {
        "tweet_data": "Test_tweet 3",
        "user_id": 3,
        "likes_count": 2,
    },
    {
        "tweet_data": "Test_tweet 4",
        "user_id": 2,
        "likes_count": 1,
    },
    {
        "tweet_data": "Test_tweet 5",
        "user_id": 1,
    },
    {
        "tweet_data": "Test_tweet 6",
        "user_id": 1,
        "likes_count": 2,
    },
    {
        "tweet_data": "Test_tweet 7",
        "user_id": 3,
        "likes_count": 1,
    },
    {
        "tweet_data": "Test_tweet 8",
        "user_id": 3,
    },
    {
        "tweet_data": "Test_tweet 9",
        "user_id": 2,
        "likes_count": 2,
    },
    {
        "tweet_data": "Test_tweet 10",
        "user_id": 2,
    },
    {
        "tweet_data": "Test_tweet 11",
        "user_id": 2,
        "likes_count": 2,
    },
    {
        "tweet_data": "Test_tweet 12",
        "user_id": 1,
    },
]

likes = [
    {
        "user_id": 1,
        "tweets_id": 1,
    },
    {
        "user_id": 3,
        "tweets_id": 1,
    },
    {
        "user_id": 2,
        "tweets_id": 1,
    },
    {
        "user_id": 2,
        "tweets_id": 2,
    },
    {
        "user_id": 3,
        "tweets_id": 2,
    },
    {
        "user_id": 1,
        "tweets_id": 3,
    },
    {
        "user_id": 2,
        "tweets_id": 3,
    },
    {
        "user_id": 1,
        "tweets_id": 4,
    },
    {
        "user_id": 1,
        "tweets_id": 6,
    },
    {
        "user_id": 3,
        "tweets_id": 6,
    },
    {
        "user_id": 2,
        "tweets_id": 7,
    },
    {
        "user_id": 1,
        "tweets_id": 9,
    },
    {
        "user_id": 2,
        "tweets_id": 9,
    },
    {
        "user_id": 2,
        "tweets_id": 11,
    },
    {
        "user_id": 3,
        "tweets_id": 11,
    },
]


async def re_creation_db():
    """
    Удаление и создание БД
    """
    logger.debug("Создание демонстрационной Базы")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаление всех таблиц
        await conn.run_sync(Base.metadata.create_all)  # Создание всех таблиц


async def demo():
    """
    Функция для наполнения БД демонстрационными данными
    """
    logger.debug("Загрузка демонстрационных данных")

    await re_creation_db()

    async with async_session_maker() as session:
        # Инициализируем и добавляем пользователей
        initial_users = [User(**user) for user in users]
        session.add_all(initial_users)

        # Подписки пользователей
        initial_users[0].following.extend([initial_users[1], initial_users[2]])
        initial_users[1].following.append(initial_users[0])
        initial_users[2].following.extend([initial_users[1], initial_users[0]])

        # Твиты
        initial_tweets = [Tweet(**tweet) for tweet in tweets]
        session.add_all(initial_tweets)

        # Изображения к твитам
        initial_images = [Image(**image) for image in images]
        session.add_all(initial_images)

        # Лайки
        initial_likes = [Like(**like) for like in likes]
        session.add_all(initial_likes)

        await session.commit()

        logger.debug("Демонстрационная база создана")


if __name__ == "__main__":
    asyncio.run(demo())
