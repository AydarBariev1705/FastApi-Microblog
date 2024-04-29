import json
from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.tweet
@pytest.mark.usefixtures("users", "tweets")
class TestTweets:

    @pytest.fixture(scope="class")
    async def new_tweet(self) -> Dict:
        """
        Данные для добавления нового твита
        """
        return {"tweet_data": "Тестовый твит", "tweet_media_ids": []}

    @pytest.fixture(scope="class")
    async def new_tweet_with_image(self, new_tweet: Dict) -> Dict:
        """
        Данные для добавления нового твита с изображениями
        """
        new_tweet["tweet_media_ids"] = [1, 2]
        return new_tweet

    async def test_create_tweet(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование добавления твита
        """
        resp = await client.post(
            "/api/tweets",
            data=json.dumps({"tweet_data": "Тестовый твит",
                             "tweet_media_ids": [],
                             }),
            headers={
                "api-key": "test-user1",
                "Content-Type": "application/json",
            },
        )
        assert resp
        assert resp.json() == {
            "result": True,
            "tweet_id": 4,
        }

    async def test_create_invalid_tweet(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование вывода сообщения об ошибке
         при публикации слишком длинного твита (> 280 символов)
        """

        long_tweet = (
            "Python — идеальный язык для новичка."
            "Код на Python легко писать и читать,"
            " язык стабильно занимает высокие места "
            "в рейтингах популярности,"
            " а «питонисты» востребованы"
            " почти во всех сферах IT — программировании,"
            " анализе данных, системном администрировании и тестировании. "
            "YouTube, Intel, Pixar, NASA, VK, Яндекс"
            " — вот лишь немногие из известных"
            " компаний,которые используют Python в своих продуктах."
        )
        resp = await client.post(
            "/api/tweets",
            data=json.dumps({"tweet_data": long_tweet, "tweet_media_ids": []}),
            headers={
                "api-key": "test-user1",
                "Content-Type": "application/json",
            },
        )
        er_msg = ("The length of the tweet should not exceed 280 characters."
                  " Current value: 394")
        assert resp
        assert resp.json() == {
            "error_message": er_msg,
            "error_type": "422",
            "result": False,
        }

    async def test_delete_tweet(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование удаление твита
        """
        resp = await client.delete(
            "/api/tweets/1",
            headers={
                "api-key": "test-user1",
                "Content-Type": "application/json",
            },
        )

        assert resp
        assert resp.json() == {"result": True}

    async def test_delete_tweet_not_found(
            self,
            client: AsyncClient,
            headers: Dict,
            response_tweet_not_found: Dict,
    ) -> None:
        """
        Тестирование вывода ошибки при попытке удалить несуществующий твит
        """
        resp = await client.delete(
            "/api/tweets/10000",
            headers={
                "api-key": "test-user1",
                "Content-Type": "application/json",
            },
        )

        assert resp
        assert resp.json() == {
            "result": False,
            "error_type": "404",
            "error_message": "Tweet not found",
        }

    async def test_delete_tweet_locked(
        self,
        client: AsyncClient,
    ) -> None:
        """
        Тестирование вывода ошибки при попытке удалить чужой твит
        """
        resp = await client.delete(
            "/api/tweets/2",
            headers={
                "api-key": "test-user1",
                "Content-Type": "application/json",
            },
        )

        assert resp
        assert resp.json() == {
            "result": False,
            "error_type": "423",
            "error_message": "The tweet that is being accessed is locked",
        }
