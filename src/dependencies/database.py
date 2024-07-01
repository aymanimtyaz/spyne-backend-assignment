from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.config import MONGO_CONNECTION_STRING, MONGO_DATABASE_NAME



client: AsyncIOMotorClient = AsyncIOMotorClient(host=MONGO_CONNECTION_STRING)
db: AsyncIOMotorDatabase = AsyncIOMotorDatabase(client=client, name=MONGO_DATABASE_NAME)



def get_db() -> AsyncIOMotorDatabase:
    return db
