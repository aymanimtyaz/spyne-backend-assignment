from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.auth import auth_router
from src.api.user import user_router
from src.api.discussion import discussion_router
from src.api.following import following_router
from src.api.comment import comment_router
from src.api.like import like_router
from src.config import LOCAL_STORAGE_STATIC_FILES_PATH, LOCAL_STORAGE_BASE_URL



app: FastAPI = FastAPI()

app.mount(LOCAL_STORAGE_BASE_URL, StaticFiles(directory=LOCAL_STORAGE_STATIC_FILES_PATH), name="static")

app.include_router(router=auth_router)
app.include_router(router=user_router)
app.include_router(router=discussion_router)
app.include_router(router=following_router)
app.include_router(router=comment_router)
app.include_router(router=like_router)
