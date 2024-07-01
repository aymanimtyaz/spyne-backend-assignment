from abc import ABC, abstractmethod
from uuid import uuid4

import aiofiles

from src.config import LOCAL_STORAGE_STATIC_FILES_PATH, LOCAL_STORAGE_BASE_URL



class AbstractFileStorage(ABC):

    @abstractmethod
    async def create_file(self, content: bytes, file_type: str, file_name: str|None = None, file_path: str|None = None) -> str:
        """Write a new file to storage and return it's URL."""
        pass

class LocalFileStorage(AbstractFileStorage):

    def __init__(self, root: str, base_url: str):
        self.__root: str = root
        self.__base_url: str = base_url

    async def create_file(self, content: bytes, file_type: str, file_name: str|None = None, file_path: str|None = None) -> str:
        file_name = str(uuid4()) if file_name is None else file_name
        relative_path: str = f"/{file_path}" if file_path else "" + f"/{file_name}.{file_type.lstrip('.')}"
        full_path: str = self.__root + relative_path
        async with aiofiles.open(
            file=full_path,
            mode="wb"
        ) as handle:
            await handle.write(content)
        return f"{self.__base_url}{relative_path}"

_file_storage: AbstractFileStorage = LocalFileStorage(
    root=LOCAL_STORAGE_STATIC_FILES_PATH,
    base_url=LOCAL_STORAGE_BASE_URL
)
