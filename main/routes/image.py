from http import HTTPStatus

from fastapi import APIRouter, Depends, UploadFile
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from main.database import get_async_session
from main.schemas import (
    ImageErrorSchema,
    ImageSchema,
    UnauthorizedSchema,
    ValidationSchema,
)
from main.services.image import ImageService
from main.utils.exeptions import SpecialException

image_router = APIRouter(
    prefix="/api/medias", tags=["medias"]  # URL  # Объединяем URL в группу
)


@image_router.post(
    "",
    response_model=ImageSchema,
    responses={
        401: {"model": UnauthorizedSchema},
        400: {"model": ImageErrorSchema},
        422: {"model": ValidationSchema},
    },
    status_code=201,
)
async def add_image(
    file: UploadFile,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    Загрузка изображения к твиту
    """
    if not file:
        logger.error("Изображение не передано в запросе")

        raise SpecialException(
            status_code=HTTPStatus.BAD_REQUEST,  # 400
            detail="The image was not attached to the request",
        )
    logger.info(f"Изображение {file}")

    # Записываем изображение в файловой системе и создаем запись в БД
    image_id = await ImageService.save_image(image=file, session=session)

    return {"media_id": image_id}
