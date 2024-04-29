from http import HTTPStatus

from fastapi import Security
from loguru import logger

from main.database import async_session_maker
from main.models.users import User
from main.services.user import UserService
from main.utils.exeptions import SpecialException
from main.utils.token import TOKEN


async def get_current_user(token: str = Security(TOKEN)) -> User | None:
    """
    Поиск и возврат пользователя из базы данных по токену из header
    """

    if token is None:
        logger.error("Токен не найден в header")

        raise SpecialException(
            status_code=HTTPStatus.UNAUTHORIZED,  # 401
            detail="Valid api-token token is missing",
        )

    async with async_session_maker() as session:
        # Поиск пользователя
        current_user = await UserService.get_user_by_key(token=token,
                                                         session=session,
                                                         )

        if current_user is None:
            raise SpecialException(
                status_code=HTTPStatus.UNAUTHORIZED,  # 401
                detail="Sorry. Wrong api-key token. This user does not exist",
            )

        return current_user
