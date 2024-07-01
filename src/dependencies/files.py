from src.utils.file_storage import AbstractFileStorage, _file_storage



async def get_file_storage() -> AbstractFileStorage:
    return _file_storage
