from abc import ABC, abstractmethod
from typing import Any
import datetime
import time

import argon2
import jwt

from src.config import JWT_SECRET, JWT_VALIDITY_DAYS



class AbstractPasswordHash(ABC):

    @abstractmethod
    async def hash(self, password: str) -> str:
        pass

    @abstractmethod
    async def verify(self, password: str, hash: str) -> bool:
        pass

class Argon2PasswordHash(AbstractPasswordHash):

    __password_hasher: argon2.PasswordHasher = argon2.PasswordHasher()

    async def hash(self, password: str) -> str:
        return self.__password_hasher.hash(password=password)

    async def verify(self, password: str, hash: str) -> bool:
        try:
            return self.__password_hasher.verify(
                hash=hash,
                password=password
            )
        except (
            argon2.exceptions.VerificationError,
            argon2.exceptions.VerifyMismatchError,
            argon2.exceptions.VerifyMismatchError
        ):
            return False

_password_hasher: AbstractPasswordHash = Argon2PasswordHash()



class AbstractTokenGenerator(ABC):

    @abstractmethod
    async def create_token(self, payload: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def decode_token(self, token: str) -> dict[str, Any]:
        pass

class HS256JWT(AbstractTokenGenerator):

    def __init__(self, secret: str, token_validity_days: int):
        self.__secret: str = secret
        self.__token_validity_days: int = token_validity_days

    async def create_token(self, payload: dict[str, Any]) -> str:
        time_now_utc_seconds: int = int(time.time())
        return jwt.encode(
            payload=payload,
            key=self.__secret,
            algorithm="HS256",
            headers={
                "exp": time_now_utc_seconds + int(self.__token_validity_days * 86400),
                "iat": time_now_utc_seconds
            }
        )

    async def decode_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                jwt=token,
                key=self.__secret,
                algorithms=["HS256"]
            )
        except jwt.PyJWTError as e:
            print(str(e))
            raise InvalidToken()

class InvalidToken(Exception):
    pass

_token_generator: AbstractTokenGenerator = HS256JWT(
    secret=JWT_SECRET,
    token_validity_days=JWT_VALIDITY_DAYS
)
