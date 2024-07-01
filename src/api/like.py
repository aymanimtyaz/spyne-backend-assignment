from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from src.schemas.like import NewLike, Like
from src.schemas.common import Message
from src.dependencies.auth import authenticate_user
from src.dependencies.database import get_db
from src.models.user import DBUser
from src.models.comment import DBComment
from src.models.discussion import DBDiscussion
from src.models.like import DBLike, LikeAlreadyExists



like_router: APIRouter = APIRouter(prefix="/like")



@like_router.post("/")
async def like(
    like: NewLike,
    response: Response,
    user: Annotated[DBUser, Depends(authenticate_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> Like:
    if like.like_context == "COMMENT":
        comment: DBComment|None = await DBComment.get_comment_by_id(
            comment_id=ObjectId(like.context_id),
            db=db
        )
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The comment doesn't exist"
            )
    elif like.like_context == "DISCUSSION":
        discussion: DBDiscussion|None = await DBDiscussion.get_discussion_by_id(
            _id=like.context_id,
            db=db
        )
        if discussion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The discussion doesn't exist"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'like_context' should only be one of COMMENT or DISCUSSION"
        )
    response.status_code = status.HTTP_201_CREATED
    try:
        new_like: DBLike = await DBLike.add_like(
            db=db,
            context=like.like_context,
            context_id=ObjectId(like.context_id),
            user_id=user._id
        )
    except LikeAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="this like already exists"
        )
    return Like(
        like_id=str(new_like._id),
        like_context=new_like.context,
        context_id=str(new_like.context_id),
        user_id=str(new_like.user_id)
    )
    


@like_router.delete("/{like_id}")
async def unlike(
    like_id: str,
    user: Annotated[DBUser, Depends(authenticate_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> Message:
    like: DBLike|None = await DBLike.get_like(
        _id=ObjectId(like_id),
        db=db
    )
    if like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="that like does not exist"
        )
    if like.user_id != user._id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you don't have permission to delete this like"
        )
    await like.delete_like(
        db=db
    )
    return Message(
        message="like deleted successfully"
    )
