from typing import List
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


class VideoWrapper(BaseModel):
    """Container for a single video object, used in requests and responses"""

    video: Video


class Videos(BaseModel):
    """Schema for multiple videos response"""

    videos: List[Video]


class MessageResponse(BaseModel):
    """Response containing a simple message string"""

    message: str
