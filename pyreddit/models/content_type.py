"""Module for ContentType class."""

from enum import Enum
from .. import helpers


class ContentType(Enum):
    """Enumerable to represent different `pyreddit.models.post.Post` types."""

    TEXT, PHOTO, VIDEO, GIF, YOUTUBE = range(5)

    @classmethod
    def from_str(cls, str_type, default=None):
        """Gets content type from its string representation"""
        content_type = default
        if helpers.any_str(["jpg", "png", "jpeg"], str_type):
            content_type = cls.PHOTO
        elif helpers.any_str(["gif"], str_type):
            content_type = cls.GIF
        elif helpers.any_str(["mp4"], str_type):
            content_type = cls.VIDEO

        return content_type
