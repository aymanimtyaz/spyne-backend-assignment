from typing import Any, Annotated

from fastapi import Depends, Header, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.utils.auth import (
    AbstractPasswordHash, _password_hasher, AbstractTokenGenerator, InvalidToken,
    _token_generator
)
from src.models.user import DBUser
from src.dependencies.database import get_db



async def get_password_hasher() -> AbstractPasswordHash:
    return _password_hasher

async def get_token_generator() -> AbstractTokenGenerator:
    return _token_generator

async def authenticate_user(
    authorization: Annotated[str, Header()],
    token_generator: Annotated[AbstractTokenGenerator, Depends(get_token_generator)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> DBUser:
    try:
        auth_token: str = authorization.strip().split(" ")[1]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    try:
        token_payload: dict[str, Any] = await token_generator.decode_token(
            token=auth_token
        )
    except InvalidToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    if "user_id" not in token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    user_id: str = token_payload["user_id"]
    user: DBUser|None = await DBUser.get_user_by_id(
        _id=user_id,
        db=db
    )
    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
