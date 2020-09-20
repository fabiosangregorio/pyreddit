"""Entrypoint of the whole services pattern."""

import logging
from urllib.parse import urlparse
from typing import Any

from .gfycat_service import Gfycat
from .vreddit_service import Vreddit
from .imgur_service import Imgur
from .youtube_service import Youtube
from .generic_service import Generic
from ..models.media import Media


class ServicesWrapper:
    """
    Entrypoint of the whole services pattern.

    It represents a Facade which hides the complexity of the media retrieval
    across various services and providers.

    An instance for each service class is set at class initialization.
    """

    gfycat: Gfycat
    vreddit: Vreddit
    imgur: Imgur
    youtube: Youtube
    generic: Generic

    @classmethod
    def init_services(cls):
        """
        Construct services objects and initialize authentication.

        .. note::
            This needs to be called after having loaded the secret in the
            configuration.
        """
        cls.gfycat = Gfycat()
        cls.vreddit = Vreddit()
        cls.imgur = Imgur()
        cls.youtube = Youtube()
        cls.generic = Generic()

    @classmethod
    def get_media(cls, url: str, data: Any = None) -> Media:
        """
        Given the url from the Reddit json, return the corresponding media obj.

        Main function with the responsibility to choose the right service.

        Parameters
        ----------
        url : str
            Url from Reddit API json.
        data : json
            (Default value = {})

            Reddit data json containing media fallback urls.

        Returns
        -------
        `pyreddit.models.media.Media`
            The media object corresponding to the media post url.

        """
        base_url: str = urlparse(url).netloc
        media: Media

        if "gfycat.com" in base_url:
            media = cls.gfycat.get_media(url, data)
        elif "v.redd.it" in base_url:
            media = cls.vreddit.get_media(url, data)
        elif "imgur.com" in base_url:
            media = cls.imgur.get_media(url, data)
        elif "youtube.com" in base_url or "youtu.be" in base_url:
            media = cls.youtube.get_media(url, data)
        else:
            logging.info(
                "services_wrapper: no suitable service found. base_url: %s",
                base_url,
            )
            media = cls.generic.get_media(url, data)

        return media
