"""Service for Gfycat GIFs."""
import json
import os
from typing import Any
from urllib.parse import urlparse
from .. import helpers

import requests
from requests import Response

from ..exceptions import AuthenticationError
from ..models.content_type import ContentType
from ..models.media import Media
from .service import Service


class RedditGallery(Service):
    """
    Service for Reddit-hosted galleries.

    """

    has_external_request: bool = False

    @classmethod
    def preprocess(cls, url: str, data: Any) -> str:
        """
        Override of `pyreddit.services.service.Service.preprocess` method.

        Extracts the images url from the gallery metadata object
        """
        gallery_ids = [
            item["media_id"]
            for item in helpers.chained_get(data, ["gallery_data", "items"])
        ]
        gallery_items = [
            helpers.chained_get(data, ["media_metadata", gallery_id])
            for gallery_id in gallery_ids
        ]
        gallery_info = []
        for item in gallery_items:
            content_type = ContentType.PHOTO
            get_array = ["s", "u"]
            if "mp4" in item["s"]:
                content_type = ContentType.VIDEO
                get_array = ["s", "mp4"]
            media_url = helpers.chained_get(item, get_array)
            gallery_info.append(
                {
                    "url": media_url.replace("&amp;", "&"),
                    "content_type": content_type,
                }
            )
        return gallery_info

    @classmethod
    def postprocess(cls, response) -> Media:
        """
        Override of `pyreddit.services.service.Service.postprocess` method.

        Returns the media url which respects the API file limits, if
        present.
        """
        medias = []
        for item in response:
            medias.append(Media(item["url"], item["content_type"]))
        return medias
