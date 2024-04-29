from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from main.database import get_async_session
from main.models.tweets import Tweet
from main.models.users import User
from main.schemas import (
    BaseSchema,
    ErrorSchema,
    LockedSchema,
    TweetIdSchema,
    TweetListSchema,
    TweetSchema,
    UnauthorizedSchema,
    ValidationSchema,
)
from main.services.like import LikeService
from main.services.tweet import TweetsService
from main.utils.user import get_current_user

tweet_router = APIRouter(
    prefix="/api/tweets", tags=["tweets"]  # URL  # Объединяем URL в группу
)


@tweet_router.get(
    "",
    response_model=TweetListSchema,
    responses={401: {"model": UnauthorizedSchema}},
    status_code=200,
)
async def get_tweets(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session),
):
    """
    Вывод ленты твитов (выводятся твиты людей,
     на которых подписан пользователь)
    """
    tweets = await TweetsService.get_tweets(user=current_user, session=session)

    return {"tweets": tweets}


@tweet_router.post(
    "",
    response_model=TweetIdSchema,
    responses={
        401: {"model": UnauthorizedSchema},
        422: {"model": ValidationSchema},
    },
    status_code=201,
)
async def create_tweet(
    tweet_data: TweetSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session),
):
    """
    Добавление твита
    """
    tweet: Tweet = await TweetsService.create_tweet(
        tweet=tweet_data, current_user=current_user, session=session
    )

    return {"tweet_id": tweet.id}


@tweet_router.delete(
    "/{tweet_id}",
    response_model=BaseSchema,
    responses={
        401: {"model": UnauthorizedSchema},
        404: {"model": ErrorSchema},
        422: {"model": ValidationSchema},
        423: {"model": LockedSchema},
    },
    status_code=200,
)
async def delete_tweet(
    tweet_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаление твита
    """
    await TweetsService.delete_tweet(
        user=current_user, tweet_id=tweet_id, session=session
    )

    return {"result": True}


@tweet_router.post(
    "/{tweet_id}/likes",
    response_model=BaseSchema,
    responses={
        401: {"model": UnauthorizedSchema},
        404: {"model": ErrorSchema},
        422: {"model": ValidationSchema},
        423: {"model": LockedSchema},
    },
    status_code=201,
)
async def create_like(
    tweet_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session),
):
    """
    Лайк твита
    """
    await LikeService.like(tweet_id=tweet_id,
                           user_id=current_user.id,
                           session=session,
                           )

    return {"result": True}


@tweet_router.delete(
    "/{tweet_id}/likes",
    response_model=BaseSchema,
    responses={
        401: {"model": UnauthorizedSchema},
        404: {"model": ErrorSchema},
        422: {"model": ValidationSchema},
        423: {"model": LockedSchema},
    },
    status_code=200,
)
async def delete_like(
    tweet_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаление лайка
    """
    await LikeService.dislike(
        tweet_id=tweet_id, user_id=current_user.id, session=session
    )

    return {"result": True}
