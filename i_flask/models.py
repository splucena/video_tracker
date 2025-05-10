from typing import Optional, Literal
from pydantic import BaseModel, field_validator
from datetime import datetime
import re


class Video(BaseModel):
    """Schema for a video object"""

    id: int
    name: str
    href: str
    post_date: str
    views_count: int

    @field_validator("post_date")
    @classmethod
    def validate_date_format(cls, v):
        """Ensure post_date is in YYYY-MM-DD format"""
        value_error = "post_date must be a valid date in YYYY-MM-DD format"
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError(value_error)

        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(value_error)

        return v


class Videos(BaseModel):
    """Schema for multiple videos response"""
    videos: list[Video]


class MessageResponse(BaseModel):
    """Response containing a simple message string"""
    message: str


class VideoWrapper(BaseModel):
    """Container for a single video object, used in requests and responses"""
    video: Video


class VideoIdParam(BaseModel):
    """Path parameter containing a video ID"""
    id: int


class VideosSortParams(BaseModel):
    """Query parameters for sorting videos"""

    sort_by: Optional[Literal["name", "post_date", "views_count"]]
    order: Optional[Literal["asc", "desc"]]
