"""Service for Gfycat GIFs."""
from typing import Any

import json
from urllib.parse import urlparse
import os
import requests

from requests import Response

from .service import Service
from ..models.media import Media
from ..models.content_type import ContentType
from ..exceptions import AuthenticationError


class Gfycat(Service):
    """
    Service for Gfycat GIFs.

    Notes
    -----
    This is an authenticated OAuth service.

    """

    is_authenticated: bool = True

    def __init__(self):
        Gfycat.authenticate()

    @classmethod
    def preprocess(cls, url: str, data: Any) -> str:
        """
        Override of `pyreddit.services.service.Service.preprocess` method.

        Extracts the gfycat Id from the url and constructs the provider url.
        """
        gfyid: str = urlparse(url).path.partition("-")[0]
        return f"https://api.gfycat.com/v1/gfycats/{gfyid}"

    @classmethod
    def get(cls, url: str) -> Response:
        """
        Override of `pyreddit.services.service.Service.get` method.

        Makes a call to the provider's API.
        """
        return requests.get(
            url, headers={"Authorization": f"Bearer {cls.access_token}"}
        )

    @classmethod
    def postprocess(cls, response) -> Media:
        """
        Override of `pyreddit.services.service.Service.postprocess` method.

        Returns the media url which respects the API file limits, if
        present.
        """
        gfy_item: Any = json.loads(response.content)["gfyItem"]
        media: Media = Media(
            gfy_item["webmUrl"].replace(".webm", ".mp4"),
            ContentType.VIDEO,
            gfy_item["webmSize"],
        )
        # See: https://shorturl.at/dnyBM
        if media.size and media.size > 20000000:
            media.url = gfy_item["max5mbGif"]
            media.type = ContentType.GIF
            media.size = 5000000
        return media

    @classmethod
    def authenticate(cls) -> None:
        """
        Override of `pyreddit.services.service.Service.authenticate` method.

        Authenticates the service through OAuth.
        """
        response: Response = requests.post(
            "https://api.gfycat.com/v1/oauth/token",
            data=json.dumps(
                {
                    "grant_type": "client_credentials",
                    "client_id": os.getenv("GFYCAT_CLIENT_ID"),  # type: ignore
                    "client_secret": os.getenv("GFYCAT_CLIENT_SECRET"),  # type: ignore
                }
            ),
        )
        if response.status_code >= 300:
            raise AuthenticationError({"response_text": response.text})

        cls.access_token = json.loads(response.content)["access_token"]
