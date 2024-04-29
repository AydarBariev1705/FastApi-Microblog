import pytest
from httpx import AsyncClient


@pytest.mark.follower
@pytest.mark.usefixtures("users")
class TestFollowers:
    async def test_create_follower(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование подписки на пользователя
        """
        resp = await client.post(
            "/api/users/4/follow", headers={"api-key": "test-user1"}
        )

        assert resp
        assert resp.json() == {"result": True}

    async def test_create_follower_not_found(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование вывода ошибки
         при попытке подписки на несуществующего пользователя
        """
        resp = await client.post(
            "/api/users/999/follow",
            headers={"api-key": "test-user1"},
        )

        assert resp
        assert resp.json() == {
            "result": False,
            "error_type": "404",
            "error_message": "The subscription user was not found",
        }

    async def test_create_follower_locked(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование вывода ошибки
         при попытке подписки на уже подписанного ранее пользователя
        """
        resp = await client.post(
            "/api/users/2/follow",
            headers={"api-key": "test-user1"},
        )

        assert resp
        assert resp.json() == {
            "error_message": "The user is already subscribed",
            "error_type": "423",
            "result": False,
        }

    async def test_delete_follower(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование удаления подписки пользователя
        """
        resp = await client.delete(
            "/api/users/2/follow", headers={"api-key": "test-user1"}
        )

        assert resp
        assert resp.json() == {"result": True}

    async def test_delete_follower_not_found(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование вывода ошибки
        при удалении подписки с несуществующего пользователя
        """
        resp = await client.delete(
            "/api/users/999/follow",
            headers={"api-key": "test-user1"},
        )
        er_msg = "The user to cancel the subscription was not found"

        assert resp
        assert resp.json() == {
            "result": False,
            "error_type": "404",
            "error_message": er_msg,
        }

    async def test_delete_follower_locked(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование вывода ошибки
         при удалении подписки от пользователя, на которого нет подписки
        """
        resp = await client.delete(
            "/api/users/5/follow",
            headers={"api-key": "test-user1"},
        )

        assert resp
        assert resp.json() == {
            "result": False,
            "error_type": "423",
            "error_message": "The user is not among the subscribers",
        }

    async def test_create_follower_to_yourself(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование подписки на пользователя
        """
        resp = await client.post(
            "/api/users/1/follow", headers={"api-key": "test-user1"}
        )

        assert resp
        assert resp.json() == {
            "result": False,
            "error_type": "422",
            "error_message": "You can't subscribe to yourself",
        }
