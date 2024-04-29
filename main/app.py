from fastapi import Depends, FastAPI
from starlette.staticfiles import StaticFiles

from main.routes.image import image_router
from main.routes.tweet import tweet_router
from main.routes.user import user_router
from main.utils.exeptions import SpecialException, custom_special_exception
from main.utils.user import get_current_user

app = FastAPI(title="Microblog",
              debug=True,
              dependencies=[Depends(get_current_user)],)

# Статик
# app.mount("/static",
#           StaticFiles(directory="/static"),
#           name="static",
#           )
# Регистрация пользовательского исключения
app.add_exception_handler(SpecialException, custom_special_exception)

# Включение URL адресов
app.include_router(user_router)
app.include_router(image_router)
app.include_router(tweet_router)
