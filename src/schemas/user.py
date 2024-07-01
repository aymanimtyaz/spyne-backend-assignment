from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber



class NewUser(BaseModel):

    full_name: str
    phone_number: PhoneNumber
    email: EmailStr
    password: str


class UserSelf(BaseModel):

    user_id: str
    full_name: str
    phone_number: PhoneNumber
    email: EmailStr


class UserPublic(BaseModel):

    user_id: str
    full_name: str


class UserUpdate(BaseModel):

    full_name: str|None = None
    phone_number: PhoneNumber|None = None
    email: EmailStr|None = None
