import dataclasses
from typing import Any
import datetime

from bson import ObjectId
from motor.motor_asyncio import (
    AsyncIOMotorDatabase, AsyncIOMotorCommandCursor,
    AsyncIOMotorCursor
)
from pymongo import ReturnDocument
from typing_extensions import Self

from src.models.common import NoChangeInResource, ResourceNotFound



@dataclasses.dataclass
class DBDiscussion:

    _id: ObjectId
    user_id: ObjectId
    text: str
    tags: list[str]
    created_on: datetime.datetime
    image_link: str|None = None
    
    def __post_init__(self) -> None:
        if self.created_on.tzinfo != datetime.timezone.utc:
            raise ValueError("'creation_date_utc' must have UTC as its timezone")

    @classmethod
    async def get_discussion_by_id(
        cls,
        _id: str,
        db: AsyncIOMotorDatabase
    ) -> Self|None:
        discussion: dict|None = await db["discussions"].find_one(
            filter={
                "_id": ObjectId(_id)
            }
        )
        if discussion is not None:
            return cls(
                _id=discussion["_id"],
                user_id=discussion["user_id"],
                text=discussion["text"],
                tags=discussion["tags"],
                created_on=discussion["created_on"].astimezone(tz=datetime.timezone.utc),
                image_link=discussion["image_link"]
            )
        return None

    @classmethod
    async def create_discussion(
        cls,
        user_id: ObjectId,
        text: str,
        tags: list[str],
        created_on: datetime.datetime,
        db: AsyncIOMotorDatabase,
        image_link: str|None = None
    ) -> Self:
        inserted_discussion = await db["discussions"].insert_one(
            document={
                "user_id": user_id,
                "text": text,
                "tags": tags,
                "image_link": image_link,
                "created_on": created_on
            }
        )
        return cls(
            _id=inserted_discussion.inserted_id,
            user_id=user_id,
            text=text,
            tags=tags,
            created_on=created_on,
            image_link=image_link
        )

    @classmethod
    async def search_discussions_based_on_text(
        cls,
        search_term: str,
        skip: int,
        limit: int,
        db: AsyncIOMotorDatabase
    ) -> list[Self]:
        search_results: AsyncIOMotorCommandCursor = db["discussions"].aggregate(
            pipeline=[
                {
                    "$search":{
                        "index": "discussions_text",
                        "text": {
                            "path": "text",
                            "query": search_term
                        }
                    }
                },
                {
                    "$skip": skip
                },
                {
                    "$limit": limit
                }
            ]
        )
        discussions: list[Self] = list()
        for doc in await search_results.to_list(length=None):
            discussions.append(
                cls(
                    _id=doc["_id"],
                    user_id=doc["user_id"],
                    text=doc["text"],
                    tags=doc["tags"],
                    created_on=doc["created_on"].astimezone(tz=datetime.timezone.utc),
                    image_link=doc["image_link"]
                )
            )
        return discussions

    @classmethod
    async def search_discussions_based_on_tags(
        cls,
        search_tags: list[str],
        skip: int,
        limit: int,
        db: AsyncIOMotorDatabase
    ) -> list[Self]:
        search_results: AsyncIOMotorCursor = db["discussions"].find(
            filter={
                "tags": {
                    "$all": search_tags
                }
            }
        ).skip(skip=skip).limit(limit=limit)
        discussions: list[Self] = list()
        async for doc in search_results:
            discussions.append(
                cls(
                    _id=doc["_id"],
                    user_id=doc["user_id"],
                    text=doc["text"],
                    tags=doc["tags"],
                    created_on=doc["created_on"].astimezone(tz=datetime.timezone.utc),
                    image_link=doc["image_link"]
                )
            )
        return discussions

    async def update_discussion(
        self,
        db: AsyncIOMotorDatabase,
        text: str|None = None,
        tags: list[str]|None = None,
        image_link: str|None = None
    ) -> None:
        update_dict: dict[str, Any] = dict()
        if text is not None:
            update_dict["text"] = text
        if tags is not None:
            update_dict["tags"] = tags
        if image_link is not None:
            update_dict["image_link"] = image_link
        print(update_dict)
        if not update_dict:
            raise NoChangeInResource()
        updated_discussion: dict|None = await db["discussions"].find_one_and_update(
            filter={
                "_id": self._id
            },
            update={
                "$set": update_dict
            },
            return_document=ReturnDocument.AFTER
        )
        if updated_discussion is not None:
            self.text = updated_discussion["text"]
            self.tags = updated_discussion["tags"]
            self.image_link = updated_discussion["image_link"]
        else:
            ResourceNotFound()

    async def delete_discussion(
        self,
        db: AsyncIOMotorDatabase
    ) -> None:
        await db["discussions"].delete_one(
            filter={
                "_id": self._id
            }
        )
        return None
