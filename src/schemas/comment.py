from pydantic import BaseModel



class Comment(BaseModel):

    comment_id: str
    discussion_id: str
    user_id: str
    text: str
    parent_comment_id: str|None = None


class NewComment(BaseModel):

    discussion_id: str
    text: str
    parent_comment_id: str|None = None


class CommentUpdate(BaseModel):

    text: str
