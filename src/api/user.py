from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.schemas.user import UserSelf, UserUpdate, UserPublic
from src.schemas.common import Message
from src.dependencies.auth import authenticate_user
from src.dependencies.database import get_db
from src.models.user import DBUser
from src.models.common import ResourceNotFound



user_router: APIRouter = APIRouter(prefix="/user")



@user_router.patch(path="/")
async def update_user(
    user_update: UserUpdate,
    user: Annotated[DBUser, Depends(authenticate_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> UserSelf:
    try:
        await user.update_user(
            db=db,
            new_full_name=user_update.full_name,
            new_phone_number=user_update.phone_number,
            new_email=user_update.email
        )
    except ResourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="at least one field must be updated"
        )
    return UserSelf(
        user_id=str(user._id),
        full_name=user.full_name,
        phone_number=PhoneNumber(user.phone_number),
        email=user.email
    )


@user_router.delete(path="/")
async def delete_user(
    user: Annotated[DBUser, Depends(authenticate_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> Message:
    await user.delete_user(db=db)
    # TODO: Handle orphaned resources like discussions, likes
    # comments, followings, etc.
    return Message(
        message="The user was successfully deleted"
    )
    

@user_router.get(path="/search/{full_name}")
async def search_users_by_name(
    full_name: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    skip: int = 0,
    limit: int = 10
) -> list[UserPublic]:
    db_search_results: list[DBUser] = await DBUser.search_users_by_full_name(
        search_term=full_name,
        skip=skip,
        limit=limit,
        db=db
    )
    search_results: list[UserPublic] = [
        UserPublic(
            user_id=str(user._id),
            full_name=user.full_name
        ) for user in db_search_results
    ]
    return search_results
