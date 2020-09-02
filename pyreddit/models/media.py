"""Module for Media class."""

from typing import Optional
from .content_type import ContentType


class Media:
    """
    Represents a media content in the application.

    This can be any of `pyreddit.models.content_type.ContentType`: photo,
    video, gif, etc.

    Parameters
    ----------
    url : str
        URL of the media on the internet.

    media_type : `pyreddit.models.content_type.ContentType`
        Content type of the media. This is used in
        `pyreddit.linker.Linker` to determine what type of message to send
        to the chat.

    size : int
        Size (in bytes) of the media content. This can be none if it
        is unkwnown, but it is crucial because of file size
        limitations.

    """

    def __init__(
        self, url: str, media_type: ContentType, size: Optional[int] = None
    ):
        self.url = url
        self.type = media_type
        self.size = size
