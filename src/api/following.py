from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from src.dependencies.database import get_db
from src.dependencies.auth import authenticate_user
from src.schemas.following import FollowRequest, Following
from src.schemas.common import Message
from src.models.user import DBUser
from src.models.following import DBFollowing, FollowingAlreadyExists



following_router: APIRouter = APIRouter(prefix="/following")



@following_router.post("/")
async def follow(
    follow_request: FollowRequest,
    response: Response,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    user: Annotated[DBUser, Depends(authenticate_user)],
) -> Following:
    followee: DBUser|None = await DBUser.get_user_by_id(
        _id=follow_request.followee_id,
        db=db
    )
    if followee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="the followee doesn't exist"
        )
    if user._id == followee._id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="you cant follow yourself"
        )
    try:
        new_following: DBFollowing = await DBFollowing.create_following(
            db=db,
            followee_id=followee._id,
            follower_id=user._id
        )
    except FollowingAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="this following already exists"
        )
    response.status_code = status.HTTP_201_CREATED
    return Following(
        following_id=str(new_following._id)
    )



@following_router.delete("/{following_id}")
async def unfollow(
    following_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    user: Annotated[DBUser, Depends(authenticate_user)],
) -> Message:
    following_to_delete: DBFollowing|None = await DBFollowing.get_following_by_id(
        following_id=ObjectId(following_id),
        db=db
    )
    if following_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="the following doesn't exist"
        )
    if following_to_delete.follower_id != user._id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have permission to delete this following"
        )
    await following_to_delete.delete_following(
        db=db
    )
    return Message(
        message="The following was deleted successfully"
    )
