from pydantic import BaseModel



class NewLike(BaseModel):

    like_context: str
    context_id: str


class Like(BaseModel):

    like_id: str
    like_context: str
    context_id: str
    user_id: str
