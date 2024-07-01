from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.schemas.user import NewUser
from src.schemas.auth import LoginInfo, AuthToken
from src.dependencies.database import get_db
from src.dependencies.auth import (
    AbstractPasswordHash, AbstractTokenGenerator, get_password_hasher, get_token_generator
)
from src.models.user import DBUser, DuplicateEmailOrPhone



auth_router: APIRouter = APIRouter(prefix="/auth")



@auth_router.post("/signup")
async def signup(
    new_user: NewUser,
    response: Response,
    password_hasher: Annotated[AbstractPasswordHash, Depends(get_password_hasher)],
    token_generator: Annotated[AbstractTokenGenerator, Depends(get_token_generator)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> AuthToken:
    try:
        new_db_user: DBUser = await DBUser.create_new_user(
            new_user=new_user,
            hashed_password=await password_hasher.hash(password=new_user.password),
            db=db
        )
    except DuplicateEmailOrPhone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The email and/or phone number provided is already in use"
        )
    response.status_code = status.HTTP_201_CREATED
    return AuthToken(
        token=await token_generator.create_token(
            payload={
                "user_id": str(new_db_user._id)
            }
        )
    )
    

@auth_router.post("/login")
async def login(
    login_info: LoginInfo,
    password_hasher: Annotated[AbstractPasswordHash, Depends(get_password_hasher)],
    token_generator: Annotated[AbstractTokenGenerator, Depends(get_token_generator)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> AuthToken:
    user: DBUser|None = await DBUser.get_user_by_email(
        email=login_info.email,
        db=db
    )
    if user is not None and await password_hasher.verify(
        password=login_info.password,
        hash=user.pw_hash
    ) is True:
        return AuthToken(
            token=await token_generator.create_token(
                payload={
                    "user_id": str(user._id)
                }
            )
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect email or password"
        )
