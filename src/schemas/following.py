from pydantic import BaseModel



class Following(BaseModel):

    following_id: str


class FollowRequest(BaseModel):

    followee_id: str
