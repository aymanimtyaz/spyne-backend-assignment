import dataclasses

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from typing_extensions import Self



@dataclasses.dataclass
class DBFollowing:

    _id: ObjectId
    follower_id: ObjectId
    followee_id: ObjectId

    @classmethod
    async def get_following_by_id(
        cls,
        following_id: ObjectId,
        db: AsyncIOMotorDatabase
    ) -> Self|None:
        following: dict|None = await db["followings"].find_one(
            filter={
                "_id": following_id
            }
        )
        if following is not None:
            return cls(
                _id=following["_id"],
                follower_id=following["follower_id"],
                followee_id=following["followee_id"]
            )
        return None

    @classmethod
    async def create_following(
        cls,
        db: AsyncIOMotorDatabase,
        follower_id: ObjectId,
        followee_id: ObjectId
    ) -> Self:
        try:
            new_following = await db["followings"].insert_one(
                document={
                    "followee_id": followee_id,
                    "follower_id": follower_id
                }
            )
        except DuplicateKeyError:
            raise FollowingAlreadyExists()
        else:
            return cls(
                _id=new_following.inserted_id,
                followee_id=followee_id,
                follower_id=follower_id
            )

    async def delete_following(
        self,
        db: AsyncIOMotorDatabase
    ) -> None:
        await db["followings"].delete_one(
            filter={
                "_id": self._id
            }
        )
        return None

class FollowingAlreadyExists(Exception):
    pass
