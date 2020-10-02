"""
Catched exceptions of the software.

The application follows the try/catch pattern to return errors in the program
flow between two functions.
"""

import logging
import os
from typing import Any

import sentry_sdk as sentry


class RedditError(Exception):
    """
    Base class for all catched exceptions.

    Parameters
    ----------
    msg : str
        Exception message to be bubbled up.

    data : dict (Default value = None)
        Extra data to be sent to Sentry if `capture` is set to True.

    capture : Boolean (Default value = False)
        Whether to send the exception to Sentry issue tracking service, if
        Sentry is configured.

    Notes
    -----
    All children exceptions have the same parameters.

    """

    def __init__(self, msg: Any, data: Any = None, capture: bool = False):
        super().__init__(msg)
        if (
            os.getenv("SENTRY_TOKEN") is not None
            and len(os.getenv("SENTRY_TOKEN")) > 0  # type: ignore
        ):
            if data is not None:
                with sentry.configure_scope() as scope:
                    for key, value in data.items():
                        scope.set_extra(key, value)
            if capture:
                sentry.capture_exception()
        logging.error(
            f"{self.__class__.__name__}, {('data: '+ str(data)) if data else ''}"
        )


class AuthenticationError(RedditError):
    """Raised when a service cannot authenticate to the API provider."""

    def __init__(self, data: Any = None, capture: bool = True):
        super().__init__("Authentication failed", data, capture)


class SubredditError(RedditError):
    """
    Base class for subreddit related exceptions.

    Capture
    -------
    Unless specified otherwise, these are not a true error of the application
    and originate from a "correct" subreddit property, such as it being private
    or not existing, and therfore **should not** be captured by Sentry.
    """


class PostError(RedditError):
    """
    Base class for post related exceptions.

    Capture
    -------
    Unless specified otherwise, these are true errors of the application and
    **should** be captured by Sentry.
    """

    def __init__(self, msg: Any, data: Any = None, capture: bool = True):
        super().__init__(msg, data, capture)


class MediaError(RedditError):
    """
    Base class for media related exceptions.

    Capture
    -------
    These errors cause the retrieved post not to be sent, or to be sent not as
    it should be. Therefore they represent a critical part of the application.
    For this, unless specified otherwise, they **should** be captured by Sentry.
    """

    def __init__(self, msg: Any, data: Any = None, capture: bool = True):
        super().__init__(msg, data, capture)


class SubredditPrivateError(SubredditError):
    """Raised when the subreddit is private, and therefore cannot be fetched."""

    def __init__(self, data: Any = None, capture: bool = False):
        super().__init__("This subreddit is private.", data, capture)


class SubredditDoesntExistError(SubredditError):
    """Raised when the subreddit does not exist."""

    def __init__(self, data: Any = None, capture: bool = False):
        super().__init__("This subreddit doesn't exist.", data, capture)


class PostRequestError(PostError):
    """
    Raised when there's an error in the post request.

    .. note:: Not to be confused with `PostRetrievalError`
    """

    def __init__(self, data: Any = None, capture: bool = True):
        super().__init__("I can't find that subreddit.", data, capture)


class PostRetrievalError(PostError):
    """
    Raised when there's an error in the post json.

    E.g. a mandatory json field is missing or the json is not strucutred as
    expected.
    """

    def __init__(self, data: Any = None, capture: bool = True):
        super().__init__("The retrieval of the post failed.", data, capture)


class MediaRetrievalError(MediaError):
    """Raised when there's an error in the media retrieval request."""

    def __init__(self, data: Any = None, capture: bool = True):
        super().__init__("Error in getting the media", data, capture)
