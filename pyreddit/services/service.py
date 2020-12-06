"""Abstract Base static Class for every service."""
from abc import abstractmethod
from typing import Any, Optional, Union, List

import requests
from requests import Response

from ..exceptions import MediaRetrievalError
from ..models.media import Media


class Service:
    """
    Abstract Base static Class for every service class.

    Summary
    -------
    This class contains all the common logic to the media retrieval process in
    all child services.

    This consists of the `get_media()` method, which executes the following
    steps (in order):

    * URL preprocessing
    * Media information get
    * re-authentication if necessary
    * URL postprocessing and Media object creation

    All the implementation logic is delegated to the child classes, since every
    service provider has custom logic, although the base class offers some basic
    implementation, which can be easily overwritten.

    Notes
    -----
    Authenticated services need to present an `__init__` method in which the
    specific service authentication method is called, in order to authenticate
    for the first time on the Service creation.

    """

    has_external_request: bool = True
    """
    True if the service needs to reach out to an external http endpoint, False
    otherwise.
    """
    is_authenticated: bool = False
    """
    True if the external request needs to be authenticated (i.e. with an
    Authorization header), False otherwise.

    .. note::
        This is taken into account only if `has_external_request` is set to True
    """
    access_token: Optional[str] = None
    """
    Contains the access token for the OAuth authentication if present, None
    otherwise.

    .. note::
        This is taken into account only if `is_authenticated` is set to True
    """

    request_stream: bool = True
    """
    True if the stream parameter in `request.get` must be set to True
    """

    @classmethod
    def get_request_headers(cls) -> Optional[dict]:
        """
        Get service-specific headers to be included in media retrieval request.
        """

    @classmethod
    def preprocess(cls, url: str, data: Any) -> Union[str, List[str]]:
        """
        Preprocess the media URL coming from Reddit json.

        Returned url should match the service provider API URL structure, from
        which to get the media information.

        Parameters
        ----------
        url : str
            Reddit media URL to preprocess.
        data : json
            Json from the Reddit API which contains the post data. Used to get
            fallback media urls for specific services.

        Returns
        -------
        str
            Preprocessed url related to the service provider API.

        """
        return url

    @classmethod
    def get(cls, url: Union[str, List[str]]) -> Union[Response, str]:
        """
        Get the media information.

        This is usually through an http request to the service provider API.

        .. note::
            In case the request needs to be authenticated, this method assumes a
            valid access token is stored in `access_token`.

        Parameters
        ----------
        url : str
            URL related to the specific service provider API, on which an http
            request can be fired to get the media information.

        Returns
        -------
        `requests.models.Response`
            Response from the service provider API.

        """
        return requests.get(
            url, headers=cls.get_request_headers(), stream=cls.request_stream
        )

    @classmethod
    @abstractmethod
    def postprocess(cls, response: Union[Response, str]) -> List[Media]:
        """
        From the service provider API response create the media object.

        .. warning::
            This is the only abstract method of the class. Thus it needs to be
            implemented in each child class. This is due to the intrinsic
            inexistence of a common pattern on which to create the media object.

        Parameters
        ----------
        response : `requests.models.Response`
            Response from the service provider API.

        Returns
        -------
        `pyreddit.models.media.Media`
            Media object related to the media retrieval process.

        """
        raise NotImplementedError()

    @classmethod
    def authenticate(cls) -> None:
        """
        Authenticate the service on the service provider API.

        Update the `access_code` variable with the newly refreshed valid access
        token.
        """

    @classmethod
    def get_media(cls, url: str, data: Any) -> List[Media]:
        """
        Entrypoint of the class.

        Takes care of the common logic of media information retrieval, which
        consists in executing the following steps (in order):

        * `Service.preprocess()`
        * `Service.get()`
        * `Sercice.authenticate()` if the access token is not valid.

            (and then again `Service.get()`)

        * `Service.preprocess()`

        .. caution::
            This method **should not** be overwritten by child classes.

        Parameters
        ----------
        url : str
            Media URL from the Reddit API json.
        data : json
            Json from the Reddit API which contains the post data. Used to get
            fallback media urls for specific services.

        Returns
        -------
        `pyreddit.models.media.Media`
            The media object accessible from the application.

        """
        processed_url = cls.preprocess(url, data)

        if cls.has_external_request:
            response = cls.get(processed_url)
            if cls.is_authenticated and response.status_code == 401:  # type: ignore
                cls.authenticate()
                response = cls.get(processed_url)
            if response.status_code >= 300:  # type: ignore
                raise MediaRetrievalError(
                    {
                        "service": cls.__name__,
                        "reddit_media_url": url,
                        "processed_media_url": processed_url,
                    }
                )
        else:
            response = processed_url
        return cls.postprocess(response)
