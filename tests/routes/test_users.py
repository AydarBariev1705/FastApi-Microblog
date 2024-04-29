import pytest
from httpx import AsyncClient


@pytest.mark.user
@pytest.mark.usefixtures("users")
class TestUsers:
    async def test_user_me_data(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование ендпоинта по выводу данных о текущем пользователе
        """
        resp = await client.get(
            "/api/users/me",
            headers={
                "api-key": "test-user3",
                "Content-Type": "application/json",
            },
        )

        assert resp
        assert resp.json() == {
            "result": True,
            "user": {
                "followers": [{"id": 4, "name": "test-user4"}],
                "following": [{"id": 1, "name": "test-user1"}],
                "id": 3,
                "name": "test-user3",
            },
        }

    async def test_user_data_by_id(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование ендпоинта
         по выводу данных о пользователе по переданному id
        """
        resp = await client.get(
            "/api/users/3",
            headers={
                "api-key": "test-user3",
                "Content-Type": "application/json",
            },
        )

        assert resp
        assert resp.json() == {
            "result": True,
            "user": {
                "followers": [{"id": 4, "name": "test-user4"}],
                "following": [{"id": 1, "name": "test-user1"}],
                "id": 3,
                "name": "test-user3",
            },
        }

    async def test_user_data_by_id_not_found(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование вывода ошибки
         при отсутствии пользователя по переданному id
        """
        resp = await client.get(
            "/api/users/1000",
            headers={
                "api-key": "test-user1",
                "Content-Type": "application/json",
            },
        )

        assert resp
        assert resp.json() == {
            "result": False,
            "error_type": "404",
            "error_message": "User not found",
        }
