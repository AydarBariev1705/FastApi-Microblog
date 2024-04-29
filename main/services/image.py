from itertools import chain
from typing import List

from fastapi import UploadFile
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from main.models.images import Image
from main.utils.image import delete_images, save_image_util


class ImageService:
    """
    Класс для обработки изображений при добавлении твита
    """

    @classmethod
    async def save_image(cls, image: UploadFile, session: AsyncSession) -> int:
        """
        Сохранение изображения (без привязки к твиту)
        :param image: файл
        :param session: асинхронная сессия
        :return: id изображения
        """
        logger.debug("Сохранение изображения")

        path = await save_image_util(
            file=image
        )  # Сохранение изображения в файловой системе
        image_obj = Image(path_media=path)  # Создание экземпляра изображения
        session.add(image_obj)  # Добавление изображения в БД
        await session.commit()  # Сохранение в БД

        return image_obj.id

    @classmethod
    async def update_images(
        cls, tweet_media_ids: List[int], tweet_id: int, session: AsyncSession
    ) -> None:
        """
        Обновление изображений (привязка к твиту)
        :param tweet_media_ids: список с id изображений
        :param tweet_id: id твита для привязки изображений
        :param session: асинхронная сессия
        :return: None
        """
        logger.debug(
            f"Обновление изображения: {tweet_media_ids}, tweet_id: {tweet_id}"
        )

        query = (
            update(Image).where(Image.id.in_(tweet_media_ids)).values(tweet_id=tweet_id)
        )
        await session.execute(query)

    @classmethod
    async def get_images(cls,
                         tweet_id: int,
                         session: AsyncSession,
                         ) -> List[Image]:
        """
        Функция для получения изображений.
        :param tweet_id: id твита
        :param session: асинхронная сессия
        :return: None
        """
        logger.debug("Поиск изображений твита")

        query = select(Image).filter(Image.tweet_id == tweet_id)
        images = await session.execute(query)

        # Очищаем результат от вложенных кортежей
        return list(chain(*images.all()))

    @classmethod
    async def delete_images(cls, tweet_id: int, session: AsyncSession) -> None:
        """
        Удаление изображений твита
        :param tweet_id: id твита
        :param session: асинхронная сессия
        :return: None
        """
        logger.debug("Удаление изображений твита")

        images = await cls.get_images(tweet_id=tweet_id, session=session)

        if images:
            # Удаляем изображения из файловой системы
            await delete_images(images=images)
        else:
            logger.warning("Изображения не найдены")
