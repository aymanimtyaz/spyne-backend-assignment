from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from src.dependencies.database import get_db
from src.dependencies.auth import authenticate_user
from src.schemas.comment import NewComment, Comment, CommentUpdate
from src.schemas.common import Message
from src.models.user import DBUser
from src.models.comment import DBComment
from src.models.discussion import DBDiscussion



comment_router: APIRouter = APIRouter(prefix="/comment")



@comment_router.post("/")
async def add_comment(
    new_comment: NewComment,
    response: Response,
    user: Annotated[DBUser, Depends(authenticate_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> Comment:
    discussion: DBDiscussion|None = await DBDiscussion.get_discussion_by_id(
        _id=new_comment.discussion_id,
        db=db
    )
    if discussion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="the discussion for which this comment was being added doesn't exist"
        )
    if new_comment.parent_comment_id is not None:
        parent_comment: DBComment|None = await DBComment.get_comment_by_id(
            comment_id=ObjectId(new_comment.parent_comment_id),
            db=db
        )
        if parent_comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="the specified parent comment doesn't exist"
            )
    new_db_comment: DBComment = await DBComment.add_comment(
        db=db,
        discussion_id=discussion._id,
        user_id=user._id,
        text=new_comment.text,
        parent_comment_id=ObjectId(new_comment.parent_comment_id) if new_comment.parent_comment_id
                          is not None else None
    )
    response.status_code = status.HTTP_201_CREATED
    return Comment(
        comment_id=str(new_db_comment._id),
        discussion_id=str(new_db_comment.discussion_id),
        user_id=str(new_db_comment.user_id),
        text=new_db_comment.text,
        parent_comment_id=str(new_db_comment.parent_comment_id) if new_db_comment.parent_comment_id
                          is not None else None
    )


@comment_router.patch("/{comment_id}")
async def update_comment(
    comment_id: str,
    comment_update: CommentUpdate,
    user: Annotated[DBUser, Depends(authenticate_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> Comment:
    comment: DBComment|None = await DBComment.get_comment_by_id(
        comment_id=ObjectId(comment_id),
        db=db
    )
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="the comment you're trying to update doesn't exist"
        )
    if comment.user_id != user._id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have permission to update this comment"
        )
    await comment.update_comment(
        db=db,
        text=comment_update.text
    )
    return Comment(
        comment_id=str(comment._id),
        discussion_id=str(comment.discussion_id),
        user_id=str(comment.user_id),
        text=comment.text,
        parent_comment_id=str(comment.parent_comment_id) if comment.parent_comment_id is not None
                          else None
    )
    


@comment_router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    user: Annotated[DBUser, Depends(authenticate_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> Message:
    comment: DBComment|None = await DBComment.get_comment_by_id(
        comment_id=ObjectId(comment_id),
        db=db
    )
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="the comment you're trying to delete doesn't exist"
        )
    if comment.user_id != user._id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have permission to delete that comment"
        )
    await comment.delete_comment(db=db)
    # TODO: Handle orphaned resources (replies)
    return Message(
        message="The comment was deleted successfully"
    )
