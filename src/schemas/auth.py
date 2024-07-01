from pydantic import BaseModel, EmailStr



class LoginInfo(BaseModel):

    email: EmailStr
    password: str


class AuthToken(BaseModel):

    token: str
