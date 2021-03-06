"""Module for ContentType class."""

from enum import Enum


class ContentType(Enum):
    """Enumerable to represent different `pyreddit.models.post.Post` types."""

    TEXT, PHOTO, VIDEO, GIF, YOUTUBE = range(5)
