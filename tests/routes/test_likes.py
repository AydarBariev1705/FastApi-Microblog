from typing import Dict, Tuple

import pytest
from httpx import AsyncClient

from main.models.tweets import Like, Tweet
from main.models.users import User
from tests.database import async_session_maker


@pytest.mark.like
# Используем в тестах данные о пользователе и твитах
@pytest.mark.usefixtures("users", "tweets")
class TestLikes:
    @pytest.fixture(scope="class")
    async def likes(self, users: Tuple[User], tweets: Tuple[Tweet]) -> Like:
        """
        Добавляем записи о лайках
        """
        async with async_session_maker() as session:
            like_1 = Like(user_id=users[0].id, tweets_id=tweets[0].id)
            session.add(like_1)
            await session.commit()

            return like_1

    async def test_create_like(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование добавления лайка к твиту
        """
        resp = await client.post(
            "/api/tweets/2/likes", headers={"api-key": "test-user1"}
        )

        assert resp
        assert resp.json() == {"result": True}

    async def test_create_like_not_found(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование вывода ошибки
         при попытке поставить лайк несуществующему твиту
        """
        resp = await client.post(
            "/api/tweets/1000/likes",
            headers={"api-key": "test-user1"},
        )

        assert resp
        assert resp.json() == {
            "result": False,
            "error_type": "404",
            "error_message": "Tweet not found",
        }

    async def test_create_like_locked(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование вывода ошибки
         при добавлении лайка твиту, у которого уже есть лайк от пользователя
        """
        for _ in range(2):
            resp = await client.post(
                "/api/tweets/1/likes", headers={"api-key": "test-user1"}
            )

        assert resp
        assert resp.json() == {
            "result": False,
            "error_type": "423",
            "error_message": "The user has already liked this tweet",
        }

    async def test_delete_like(
        self, client: AsyncClient, headers: Dict, good_response: Dict
    ) -> None:
        """
        Тестирование удаления лайка
        """
        resp = await client.post(
            "/api/tweets/1/likes", headers={"api-key": "test-user1"}
        )
        resp = await client.delete(
            "/api/tweets/1/likes", headers={"api-key": "test-user1"}
        )

        assert resp
        assert resp.json() == {"result": True}

    async def test_delete_like_not_found(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование вывода ошибки при удалении лайка у несуществующей записи
        """
        resp = await client.delete(
            "/api/tweets/1000/likes", headers={"api-key": "test-user1"}
        )

        assert resp
        assert resp.json() == {
            "result": False,
            "error_type": "404",
            "error_message": "Tweet not found",
        }

    async def test_delete_like_locked(
        self, client: AsyncClient, headers: Dict, response_locked: Dict
    ) -> None:
        """
        Тестирование вывода ошибки при попытке удалить не существующий лайк
        """

        er_msg = "The user has not yet liked this tweet"
        resp = await client.delete(
            "/api/tweets/3/likes",
            headers={"api-key": "test-user1"},
        )
        response_locked["error_message"] = er_msg

        assert resp
        assert resp.json() == {
            "result": False,
            "error_type": "423",
            "error_message": "The user has not yet liked this tweet",
        }
