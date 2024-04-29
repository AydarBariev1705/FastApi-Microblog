from http import HTTPStatus
from typing import Optional

from fastapi.security import APIKeyHeader
from starlette.requests import Request

from main.utils.exeptions import SpecialException


class APITokenHeader(APIKeyHeader):
    """
    Проверка и извлечение токена из header
    """

    async def __call__(self, request: Request) -> Optional[str]:
        api_key = request.headers.get(self.model.name)

        if not api_key:
            if self.auto_error:
                # Кастомная ошибка для вывода сообщения в формате,
                # указанном в документации
                raise SpecialException(
                    status_code=HTTPStatus.UNAUTHORIZED,  # 401
                    detail="User authorization error",
                )
            else:
                return None

        return api_key


# Для авторизации в /docs (верхний правый угол на странице документации)
TOKEN = APITokenHeader(name="api-key")
