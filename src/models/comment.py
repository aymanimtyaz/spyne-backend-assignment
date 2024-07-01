import dataclasses

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from typing_extensions import Self

from src.models.common import ResourceNotFound



@dataclasses.dataclass
class DBComment:

    _id: ObjectId
    discussion_id: ObjectId
    user_id: ObjectId
    text: str
    parent_comment_id: ObjectId|None = None

    @classmethod
    async def get_comment_by_id(
        cls,
        comment_id: ObjectId,
        db: AsyncIOMotorDatabase
    ) -> Self|None:
        comment: dict|None = await db["comments"].find_one(
            filter={
                "_id": comment_id
            }
        )
        if comment is not None:
            return cls(
                _id=comment["_id"],
                discussion_id=comment["discussion_id"],
                user_id=comment["user_id"],
                text=comment["text"],
                parent_comment_id=comment["parent_comment_id"]
            )
        return None

    @classmethod
    async def add_comment(
        cls,
        db: AsyncIOMotorDatabase,
        discussion_id: ObjectId,
        user_id: ObjectId,
        text: str,
        parent_comment_id: ObjectId|None = None
    ) -> Self:
        new_comment = await db["comments"].insert_one(
            document={
                "discussion_id": discussion_id,
                "user_id": user_id,
                "text": text,
                "parent_comment_id": parent_comment_id
            }
        )
        return cls(
            _id=new_comment.inserted_id,
            discussion_id=discussion_id,
            user_id=user_id,
            text=text,
            parent_comment_id=parent_comment_id
        )

    async def update_comment(
        self,
        db: AsyncIOMotorDatabase,
        text: str
    ) -> None:
        updated_comment: dict|None = await db["comments"].find_one_and_update(
            filter={
                "_id": self._id
            },
            update={
                "$set": {
                    "text": text
                }
            },
            return_document=ReturnDocument.AFTER
        )
        if updated_comment is None:
            raise ResourceNotFound()
        self.text = updated_comment["text"]
        return None

    async def delete_comment(
        self,
        db: AsyncIOMotorDatabase
    ) -> None:
        await db["comments"].delete_one(
            filter={
                "_id": self._id
            }
        )
        return None
