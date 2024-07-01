from typing import Annotated
import datetime

from fastapi import (
    APIRouter, Depends, Response, Form, UploadFile,
    HTTPException, status
)
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.dependencies.auth import authenticate_user
from src.dependencies.database import get_db
from src.dependencies.files import AbstractFileStorage, get_file_storage
from src.models.user import DBUser
from src.models.discussion import DBDiscussion
from src.models.common import NoChangeInResource
from src.schemas.discussion import Discussion, DiscussionTextSearch, DiscussionTagSearch
from src.schemas.common import Message



discussion_router: APIRouter = APIRouter(prefix="/discussion")



@discussion_router.post("/")
async def create_discussion(
    user: Annotated[DBUser, Depends(authenticate_user)],
    text: Annotated[str, Form()],
    response: Response,
    file_storage: Annotated[AbstractFileStorage, Depends(get_file_storage)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    tags: str|None = Form(None),
    image: UploadFile|None = None
) -> Discussion:
    list_tags: list[str] = [
        tag.strip() for tag in tags.split(",")
    ] if tags is not None else list()
    if image is not None:
        if image.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="images must be of formats jpeg or png"
            )
        image_bytes: bytes = await image.read()
        image_link: str|None = await file_storage.create_file(
            content=image_bytes,
            file_type=image.content_type[6:]
        )
    else:
        image_link = None
    new_discussion: DBDiscussion = await DBDiscussion.create_discussion(
        user_id=user._id,
        text=text,
        tags=list_tags,
        created_on=datetime.datetime.now(tz=datetime.timezone.utc),
        image_link=image_link,
        db=db
    )
    response.status_code = status.HTTP_201_CREATED
    return Discussion(
        discussion_id=str(new_discussion._id),
        user_id=str(new_discussion.user_id),
        text=new_discussion.text,
        hashtags=new_discussion.tags,
        created_on=str(new_discussion.created_on),
        image_link=new_discussion.image_link
    )


@discussion_router.patch("/{discussion_id}")
async def update_discussion(
    discussion_id: str,
    user: Annotated[DBUser, Depends(authenticate_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    file_storage: Annotated[AbstractFileStorage, Depends(get_file_storage)],
    text: str|None = Form(None),
    tags: str|None = Form(None),
    image: UploadFile|None = None
) -> Discussion:
    discussion_to_update: DBDiscussion|None = await DBDiscussion.get_discussion_by_id(
        _id=discussion_id,
        db=db
    )
    if discussion_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="the specified discussion does not exist"
        )
    if discussion_to_update.user_id != user._id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you don't have permission to update this discussion"
        )
    list_tags: list[str]|None = [
        tag.strip() for tag in tags.split(",")
    ] if tags is not None else None
    if image is not None:
        if image.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="images must be of formats jpeg or png"
            )
        image_bytes: bytes = await image.read()
        image_link: str|None = await file_storage.create_file(
            content=image_bytes,
            file_type=image.content_type[6:]
        )
    else:
        image_link = None
    try:
        await discussion_to_update.update_discussion(
            db=db,
            text=text,
            tags=list_tags,
            image_link=image_link
        )
    except NoChangeInResource:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="at least one field must be updated"
        )
    return Discussion(
        discussion_id=str(discussion_to_update._id),
        user_id=str(discussion_to_update.user_id),
        text=discussion_to_update.text,
        hashtags=discussion_to_update.tags,
        created_on=str(discussion_to_update.created_on),
        image_link=discussion_to_update.image_link
    )


@discussion_router.delete("/{discussion_id}")
async def delete_discussion(
    discussion_id: str,
    user: Annotated[DBUser, Depends(authenticate_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> Message:
    discussion: DBDiscussion|None = await DBDiscussion.get_discussion_by_id(
        _id=discussion_id,
        db=db
    )
    if discussion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The discussion doesn't exist"
        )
    if discussion.user_id != user._id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have permission to delete this discussion"
        )
    await discussion.delete_discussion(
        db=db
    )
    # TODO: Handle orphaned resources such as likes and comments
    return Message(
        message="The discussion was successfully deleted"
    )


@discussion_router.post(path="/search/tags")
async def search_discussions_by_tags(
    search_tags: DiscussionTagSearch,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    skip: int = 0,
    limit: int = 10
) -> list[Discussion]:
    db_search_results: list[DBDiscussion] = await DBDiscussion.search_discussions_based_on_tags(
        search_tags=search_tags.hashtags,
        skip=skip,
        limit=limit,
        db=db
    )
    search_results: list[Discussion] = [
        Discussion(
            discussion_id=str(discussion._id),
            user_id=str(discussion.user_id),
            text=discussion.text,
            hashtags=discussion.tags,
            created_on=str(discussion.created_on),
            image_link=discussion.image_link
        ) for discussion in db_search_results
    ]
    return search_results


@discussion_router.post(path="/search")
async def search_discussions_by_content(
    search: DiscussionTextSearch,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    skip: int = 0,
    limit: int = 10
) -> list[Discussion]:
    db_search_results: list[DBDiscussion] = await DBDiscussion.search_discussions_based_on_text(
        search_term=search.search_text,
        skip=skip,
        limit=limit,
        db=db
    )
    search_results: list[Discussion] = [
        Discussion(
            discussion_id=str(discussion._id),
            user_id=str(discussion.user_id),
            text=discussion.text,
            hashtags=discussion.tags,
            created_on=str(discussion.created_on),
            image_link=discussion.image_link
        ) for discussion in db_search_results
    ]
    return search_results
