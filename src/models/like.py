import dataclasses

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from typing_extensions import Self

from src.models.common import ResourceNotFound



@dataclasses.dataclass
class DBLike:

    _id: ObjectId
    context: str
    context_id: ObjectId
    user_id: ObjectId

    @classmethod
    async def get_like(
        cls,
        _id:ObjectId,
        db: AsyncIOMotorDatabase
    ) -> Self|None:
        like: dict|None = await db["likes"].find_one(
            filter={
                "_id": _id
            }
        )
        if like is not None:
            return cls(
                _id=like["_id"],
                context=like["context"],
                context_id=like["context_id"],
                user_id=like["user_id"]
            )
        return None

    @classmethod
    async def add_like(
        cls,
        db: AsyncIOMotorDatabase,
        context: str,
        context_id: ObjectId,
        user_id: ObjectId
    ) -> Self:
        try:
            new_like = await db["likes"].insert_one(
                document={
                    "context": context,
                    "context_id": context_id,
                    "user_id": user_id
                }
            )
        except DuplicateKeyError:
            raise LikeAlreadyExists()
        return cls(
            _id=new_like.inserted_id,
            context=context,
            context_id=context_id,
            user_id=user_id
        )

    async def delete_like(
        self,
        db: AsyncIOMotorDatabase
    ) -> None:
        await db["likes"].delete_one(
            filter={
                "_id": self._id
            }
        )
        return None

class LikeAlreadyExists(Exception):
    pass
