import os
from http import HTTPStatus
from pathlib import Path

import pytest
from httpx import AsyncClient

# Корневая директория с тестами
_TEST_ROOT_DIR = Path(__file__).resolve().parents[1]


@pytest.mark.image
@pytest.mark.usefixtures("users")
class TestImages:
    async def test_load_incorrect_file(self, client: AsyncClient) -> None:
        """
        Тестирование вывода сообщения об ошибке
         при попытке загрузить файл неразрешенного формата
        """
        test_image_name = os.path.join(
            _TEST_ROOT_DIR, "files_for_tests", "test_bad_file.txt"
        )
        test_image = open(test_image_name, "rb")
        resp = await client.post(
            "/api/medias",
            files={"file": test_image},
            headers={"api-key": "test-user1"},
        )

        assert resp
        assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert resp.json()["error_type"] == "422"
        assert resp.json()["result"] is False
