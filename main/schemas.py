from http import HTTPStatus
from typing import List, Optional

from pydantic import (BaseModel,
                      ConfigDict,
                      Field,
                      field_validator,
                      model_validator,)

from main.utils.exeptions import SpecialException


class BaseSchema(BaseModel):
    """
    Базовая схема для возврата успешного ответа
    """

    result: bool = True
    model_config = ConfigDict(from_attributes=True)


class ErrorSchema(BaseSchema):
    """
    Базовая схема для неуспешного ответа с типом и текстом ошибки.
    """

    result: bool = False
    error_type: HTTPStatus = HTTPStatus.NOT_FOUND  # 404
    error_message: str = "Not found"


class UnauthorizedSchema(ErrorSchema):
    """
    Схема для неуспешного ответа при ошибке авторизации.
    """

    error_type: HTTPStatus = HTTPStatus.UNAUTHORIZED  # 401
    error_message: str = "User authorization error"


class ValidationSchema(ErrorSchema):
    """
    Схема для неуспешного ответа при ошибке валидации входных данных.
    """

    error_type: HTTPStatus = HTTPStatus.UNPROCESSABLE_ENTITY  # 422
    error_message: str = "Invalid input data"


class LockedSchema(ErrorSchema):
    """
    Схема для неуспешного ответа при блокировке действия.
    """

    error_type: HTTPStatus = HTTPStatus.LOCKED  # 423
    error_message: str = "The action is blocked"


class ImageErrorSchema(ErrorSchema):
    """
    Схема для ответа при отправке запроса на добавление изображения,
     но не приложив его.
    """

    error_type: HTTPStatus = HTTPStatus.BAD_REQUEST  # 400
    error_message: str = "The image was not attached to the request"


class ImageSchema(BaseSchema):
    """
    Схема для вывода id изображения после публикации твита
    """

    id: int = Field(alias="media_id")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Использовать псевдоним вместо названия поля
    )


class ImagePathSchema(BaseModel):
    """
    Схема для вывода ссылки на изображения при отображении твитов
    """

    path_media: str

    model_config = ConfigDict(from_attributes=True)


class LikeSchema(BaseModel):
    """
    Схема для вывода лайков при выводе твитов
    """

    id: int = Field(alias="user_id")
    username: str = Field(alias="name")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Использовать псевдоним вместо названия поля
    )

    @model_validator(mode="before")
    def extract_user(cls, data):
        """
        Метод извлекает и возвращает данные о пользователе из объекта Like
        """
        user = data.user
        return user


class UserSchema(BaseModel):
    """
    Базовая схема для вывода основных данных о пользователе
    """

    id: int
    username: str = Field(alias="name")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class UserInfoSchema(UserSchema):
    """
    Схема для вывода детальной информации о пользователе
    """

    following: Optional[List["UserSchema"]] = []
    followers: Optional[List["UserSchema"]] = []

    # Преобразование данных ORM-модели в объект схемы для сериализации
    model_config = ConfigDict(from_attributes=True)


class UserOutSchema(BaseSchema):
    """
    Схема для вывода ответа с детальными данными о пользователе
    """

    user: UserInfoSchema


class TweetSchema(BaseModel):
    """
    Схема для входных данных при добавлении нового твита
    """

    tweet_data: str = Field()
    tweet_media_ids: Optional[list[int]]

    @field_validator("tweet_data", mode="before")
    @classmethod
    def check_len_tweet_data(cls, val: str) -> str | None:
        """
        Проверка длины твита
        с переопределением вывода ошибки в случае превышения
        """
        if len(val) > 280:
            raise SpecialException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,  # 422
                detail=f"The length of the tweet should not exceed 280 characters. "
                f"Current value: {len(val)}",
            )

        return val

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Использовать псевдоним вместо названия поля
    )


class TweetIdSchema(BaseSchema):
    """
    Схема для вывода id твита после публикации
    """

    id: int = Field(alias="tweet_id")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Использовать псевдоним вместо названия поля
    )


class TweetOutSchema(BaseModel):
    """
    Схема для вывода твита, автора, вложенных изображений и данных по лайкам
    """

    id: int
    tweet_data: str = Field(alias="content")
    user: UserSchema = Field(alias="author")
    likes: List[LikeSchema]
    images: List[str] = Field(alias="attachments")
    likes_count: int

    @field_validator("images", mode="before")
    def serialize_images(cls, val: List[ImagePathSchema]):
        """
        Возвращаем список строк с ссылками на изображение
        """
        if isinstance(val, list):
            return [v.path_media for v in val]

        return val

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Использовать псевдоним вместо названия поля
    )


class TweetListSchema(BaseSchema):
    """
    Схема для вывода списка твитов
    """

    tweets: List[TweetOutSchema]
