import os
from http import HTTPStatus
from typing import List

import aiofiles
from fastapi import UploadFile
from loguru import logger

from main.config import ALLOWED_EXTENSIONS
from main.models.images import Image
from main.utils.exeptions import SpecialException


def allowed_image(image_name: str) -> None:
    """
    Проверка расширения изображения
    :param image_name: название изображения
    :return: None
    """
    logger.debug("Проверка формата изображения")

    # Проверяем, что расширение текущего файла есть в списке разрешенных
    # .rsplit('.', 1) - делит строку, начиная справа;
    # 1 - делит 1 раз (по умолчанию -1 - неограниченное кол-во раз)
    if "." in image_name and image_name.rsplit(".",
                                               1,
                                               )[1].lower() in ALLOWED_EXTENSIONS:
        logger.info("Формат изображения корректный")
    else:
        logger.error("Неразрешенный формат изображения")

        raise SpecialException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,  # 422
            detail=f"The image has an unresolved format. You can only download the following formats: "
            f"{', '.join(ALLOWED_EXTENSIONS)}",
        )


async def save_image_util(file: UploadFile) -> str:
    """
    Сохранение изображения
    :param file: файл - изображение
    :return: путь относительно static для сохранения в БД
    """
    # Проверка формата загружаемого файла
    allowed_image(image_name=file.filename)

    logger.debug("Сохранение изображения к твиту")
    # Сохраняем изображения в директорию по дате добавления твита
    contents = file.file.read()
    path = os.path.join("static", "images", f"{file.filename}")
    path_to_bd = os.path.join(f"{file.filename}")

    # Сохраняем изображение
    async with aiofiles.open(path, mode="wb") as f:
        await f.write(contents)

    # Возвращаем очищенную строку для записи в БД
    return path_to_bd


async def delete_images(images: List[Image]) -> None:
    """
    Удаление из файловой системы изображений
    :param images: объекты изображений из БД
    :return: None
    """
    logger.debug("Удаление изображений из файловой системы")

    for img in images:
        try:
            # Удаляем каждое изображение из файловой системы
            os.remove(os.path.join("static", "images", img.path_media))
            logger.debug(f"Изображение №{img.id} - {img.path_media} удалено")

        except FileNotFoundError:
            logger.error(f"Директория: {img.path_media} не найдена")

    logger.info("Все изображения удалены")
