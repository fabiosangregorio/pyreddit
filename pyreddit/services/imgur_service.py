"""Service for Imgur images and videos."""
import json
import os
import re
from typing import Any, List
from urllib.parse import urlparse

from .. import helpers
from ..models.content_type import ContentType
from ..models.media import Media
from .service import Service


class Imgur(Service):
    """Service for Imgur images and videos."""

    request_stream: bool = False

    @classmethod
    def get_request_headers(cls):
        return {"Authorization": f"Client-ID {os.getenv('IMGUR_CLIENT_ID')}"}

    @classmethod
    def preprocess(cls, url: str, data: Any) -> str:
        """
        Override of `pyreddit.services.service.Service.preprocess` method.

        Gets the media hash from the url and creates the accepted provider media
        url.
        """
        media_hash: str = urlparse(url).path.rpartition("/")[2]
        r = re.compile(r"image|gallery").search(url)
        api: str = r.group() if r else "image"
        if "." in media_hash:
            media_hash = media_hash.rpartition(".")[0]
        return f"https://api.imgur.com/3/{api}/{media_hash}"

    @classmethod
    def postprocess(cls, response) -> List[Media]:
        """
        Override of `pyreddit.services.service.Service.postprocess` method.

        Creates the right media object based on the size of provider's media.
        """
        data = json.loads(response.content)["data"]
        medias = []
        if "images" in data:
            data = data["images"]
        else:
            data = [data]
        for d in data:
            if helpers.any_str(["image/jpeg", "image/png"], d["type"]):
                medias.append(Media(d["link"], ContentType.PHOTO, d["size"]))
            elif helpers.any_str(["video", "image/gif"], d["type"]):
                medias.append(Media(d["mp4"], ContentType.VIDEO, d["mp4_size"]))

        return medias
