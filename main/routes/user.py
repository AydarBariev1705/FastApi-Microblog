from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from main.database import get_async_session
from main.models.users import User
from main.schemas import (
    BaseSchema,
    ErrorSchema,
    LockedSchema,
    UnauthorizedSchema,
    UserOutSchema,
    ValidationSchema,
)
from main.services.follower import FollowerService
from main.services.user import UserService
from main.utils.exeptions import SpecialException
from main.utils.user import get_current_user

user_router = APIRouter(
    prefix="/api/users", tags=["users"]  # URL  # Объединяем URL в группу
)


@user_router.get(
    "/me",
    # Валидация выходных данных согласно схеме UserOutSchema
    response_model=UserOutSchema,
    # Примеры схем ответов для разных кодов ответов сервера
    responses={401: {"model": UnauthorizedSchema}},
    status_code=200,
)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Вывод данных о текущем пользователе: id, username, подписки, подписчики
    """
    return {"user": current_user}


@user_router.post(
    "/{user_id}/follow",
    response_model=BaseSchema,
    responses={
        401: {"model": UnauthorizedSchema},
        404: {"model": ErrorSchema},
        422: {"model": ValidationSchema},
        423: {"model": LockedSchema},
    },
    status_code=201,
)
async def create_follower(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session),
):
    """
    Подписка на пользователя
    """
    await FollowerService.create_follower(
        current_user=current_user, following_user_id=user_id, session=session
    )

    return {"result": True}


@user_router.delete(
    "/{user_id}/follow",
    response_model=BaseSchema,
    responses={
        401: {"model": UnauthorizedSchema},
        404: {"model": ErrorSchema},
        422: {"model": ValidationSchema},
        423: {"model": LockedSchema},
    },
    status_code=200,
)
async def delete_follower(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session),
):
    """
    Отписка от пользователя
    """
    await FollowerService.delete_follower(
        current_user=current_user, followed_user_id=user_id, session=session
    )

    return {"result": True}


@user_router.get(
    "/{user_id}",
    response_model=UserOutSchema,
    responses={
        401: {"model": UnauthorizedSchema},
        404: {"model": ErrorSchema},
        422: {"model": ValidationSchema},
        423: {"model": LockedSchema},
    },
    status_code=200,
)
async def get_user(user_id: int,
                   session: AsyncSession = Depends(get_async_session),
                   ):
    """
    Вывод данных о пользователе: id, username, подписки, подписчики
    """
    user = await UserService.get_user_by_id(user_id=user_id, session=session)

    if user is None:
        raise SpecialException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )

    return {"user": user}
