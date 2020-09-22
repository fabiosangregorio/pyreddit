"""Service for when a suitable specific service is not found."""
from typing import Optional

from ..models.content_type import ContentType
from ..models.media import Media
from .service import Service


class Generic(Service):
    """Service for when a suitable specific service is not found."""

    @classmethod
    def postprocess(cls, response) -> Media:
        """Override of `pyreddit.services.service.Service.postprocess` method."""
        file_size: Optional[int] = None
        media_type: ContentType = ContentType.PHOTO

        if ".gif" in response.url:
            media_type = ContentType.GIF
        elif ".mp4" in response.url:
            media_type = ContentType.VIDEO

        if "Content-length" in response.headers:
            file_size = int(response.headers["Content-length"])

        return Media(response.url, media_type, file_size)
