from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse


class SpecialException(HTTPException):
    """
    Кастомная ошибка для быстрого вызова исключений
    """

    pass


async def custom_special_exception(request: Request, exc: HTTPException):
    """
    Кастомный обработчик ошибок для CustomApiException
    """

    return JSONResponse(
        {
            "result": False,
            "error_type": f"{exc.status_code}",
            "error_message": str(exc.detail),
        },
        status_code=exc.status_code,
    )
