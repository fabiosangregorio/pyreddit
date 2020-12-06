"""Service for when a suitable specific service is not found."""
from typing import Optional, List

from ..models.content_type import ContentType
from ..models.media import Media
from .service import Service


class Generic(Service):
    """Service for when a suitable specific service is not found."""

    @classmethod
    def postprocess(cls, response) -> List[Media]:
        """Override of `pyreddit.services.service.Service.postprocess` method."""
        file_size: Optional[int] = None
        media_type: ContentType = ContentType.from_str(
            response.url, default=ContentType.PHOTO
        )

        if "Content-length" in response.headers:
            file_size = int(response.headers["Content-length"])

        return [Media(response.url, media_type, file_size)]
