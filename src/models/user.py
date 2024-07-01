import dataclasses

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCommandCursor
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from typing_extensions import Self

from src.schemas.user import NewUser
from src.models.common import NoChangeInResource, ResourceNotFound



@dataclasses.dataclass
class DBUser:

    _id: ObjectId
    full_name: str
    phone_number: str
    email: str
    pw_hash: str

    @classmethod
    async def create_new_user(
        cls,
        new_user: NewUser,
        hashed_password: str,
        db: AsyncIOMotorDatabase
    ) -> Self:
        try:
            inserted_user = await db["users"].insert_one(
                document={
                    "full_name": new_user.full_name,
                    "phone_number": new_user.phone_number.format()[4:].replace("-", ""),
                    "email": new_user.email,
                    "pw_hash": hashed_password
                }
            )
        except DuplicateKeyError as e:
            raise DuplicateEmailOrPhone(str(e))
        else:
            return cls(
                _id=inserted_user.inserted_id,
                full_name=new_user.full_name,
                phone_number=new_user.phone_number,
                email=new_user.email,
                pw_hash=hashed_password
            )

    @classmethod
    async def get_user_by_email(
        cls,
        email: str,
        db: AsyncIOMotorDatabase
    ) -> Self|None:
        user: dict|None = await db["users"].find_one(
            filter={
                "email": email
            }
        )
        if user is not None:
            return cls(
                _id=user["_id"],
                full_name=user["full_name"],
                phone_number=user["phone_number"],
                email=user["email"],
                pw_hash=user["pw_hash"]
            )
        return None

    @classmethod
    async def get_user_by_id(
        cls,
        _id: str,
        db: AsyncIOMotorDatabase
    ) -> Self|None:
        user: dict|None = await db["users"].find_one(
            filter={
                "_id": ObjectId(_id)
            }
        )
        if user is not None:
            return cls(
                _id=user["_id"],
                full_name=user["full_name"],
                phone_number=user["phone_number"],
                email=user["email"],
                pw_hash=user["pw_hash"]
            )
        return None

    async def update_user(
        self,
        db: AsyncIOMotorDatabase,
        new_full_name: str|None = None,
        new_phone_number: str|None = None,
        new_email: str|None = None,
        new_pw_hash: str|None = None
    ) -> None:
        update_dict: dict[str, str] = dict()
        if new_full_name is not None:
            update_dict["full_name"] = new_full_name
        if new_phone_number is not None:
            update_dict["phone_number"] = new_phone_number
        if new_email is not None:
            update_dict["email"] = new_email
        if new_pw_hash is not None:
            update_dict["pw_hash"] = new_pw_hash
        if not update_dict:
            raise NoChangeInResource()
        updated_user: dict|None = await db["users"].find_one_and_update(
            filter={
                "_id": self._id
            },
            update={
                "$set": update_dict
            },
            return_document=ReturnDocument.AFTER
        )
        if updated_user is not None:
            self.full_name = updated_user["full_name"]
            self.phone_number = updated_user["phone_number"]
            self.email = updated_user["email"]
            self.pw_hash = updated_user["pw_hash"]
        else:
            raise ResourceNotFound()

    @classmethod
    async def search_users_by_full_name(
        cls,
        search_term: str,
        skip: int,
        limit: int,
        db: AsyncIOMotorDatabase
    ) -> list[Self]:
        search_results: AsyncIOMotorCommandCursor = db["users"].aggregate(
            pipeline=[
                {
                    "$search": {
                        "index": "name_search",
                        "text": {
                            "path": "full_name",
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
        users: list[Self] = list()
        for doc in await search_results.to_list(length=None):
            users.append(
                cls(
                    _id=doc["_id"],
                    full_name=doc["full_name"],
                    phone_number=doc["phone_number"],
                    email=doc["email"],
                    pw_hash=doc["pw_hash"]
                )
            )
        return users

    async def delete_user(
        self,
        db: AsyncIOMotorDatabase
    ) -> None:
        await db["users"].delete_one(
            filter={
                "_id": self._id
            }
        )
        return None

class DuplicateEmailOrPhone(Exception):

    def __init__(self, message: str):
        super().__init__(message)
