from typing import Optional

from pydantic import BaseModel, field_validator



class Discussion(BaseModel):

    discussion_id: str
    user_id: str
    text: str
    hashtags: list[str]
    image_link: Optional[str] = None
    created_on: str
    


class DiscussionTextSearch(BaseModel):

    search_text: str


class DiscussionTagSearch(BaseModel):

    hashtags: list[str]

    @field_validator("hashtags")
    @classmethod
    def should_be_nonempty(cls, hashtags: list[str]) -> list[str]:
        if not hashtags:
            raise ValueError("'hashtags' must have at least one tag in it.")
        return hashtags
