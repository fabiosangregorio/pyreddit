"""Miscellaneous helpers for the whole application."""

import os
import re
from typing import Any, List, Optional

import requests
from requests import Response
from requests.exceptions import RequestException

from .config import config


def get_random_post_url(subreddit: str) -> str:
    """
    Return the "random post" url relative to the Reddit API.

    Parameters
    ----------
    subreddit : str
        Subreddit for which to get the url.

    Returns
    -------
    str
        A new string representing the url, including the base url of reddit.

    """
    return f"https://www.reddit.com/{subreddit}/random"


def get_subreddit_names(text: str) -> List[str]:
    """
    Return a list of the ("r/" prefixed) subreddit names present in the text.

    Subreddits are searched using the official subreddit name validation.

    .. seealso::
        Subreddit name validation regex:
        https://github.com/reddit-archive/reddit/blob/master/r2/r2/models/subreddit.py#L114

    Parameters
    ----------
    text : str
        String of text in which to search for subreddit names.

    Returns
    -------
    array
        Array of valid subreddit names present in the given text ("r/" prefixed).

    """
    regex = r"\br/[A-Za-z0-9][A-Za-z0-9_]{2,20}(?=\s|\W |$|\W$|/)\b"
    return re.findall(regex, text, re.MULTILINE)


def get_subreddit_name(text: str, reverse: bool = False) -> Optional[str]:
    """
    Return the first (or last) ("r/" prefixed) subreddit name in the given text.

    Parameters
    ----------
    text : str
        String of text in which to search for the subreddit name.

    reverse : Boolean
        (Default value = False)

        Whether to return the first or last match in the string.

    Returns
    -------
    str or None
        The subreddit name if present in the text, None otherwise.

    """
    subs = get_subreddit_names(text)
    if len(subs) > 0:
        return subs[-1] if reverse else subs[0]
    return None


def escape_markdown(text: str, version=2, entity_type=None) -> str:
    """
    Escape markup symbols.

    Args:
    ----
        text (:obj:`str`): The text.
        version (:obj:`int` | :obj:`str`): Use to specify the version of telegrams Markdown.
            Either ``1`` or ``2``. Defaults to ``1``.
        entity_type (:obj:`str`, optional): For the entity types ``PRE``, ``CODE`` and the link
            part of ``TEXT_LINKS``, only certain characters need to be escaped in ``MarkdownV2``.
            See the official API documentation for details. Only valid in combination with
            ``version=2``, will be ignored else.

    """
    if int(version) == 1:
        escape_chars = r"_*`["
    elif int(version) == 2:
        if entity_type == "pre" or entity_type == "code":
            escape_chars = r"\`"
        elif entity_type == "text_link":
            escape_chars = r"\)"
        else:
            escape_chars = r"_*[]()~`>#+-=|{}.!"
    else:
        raise ValueError("Markdown version must be either 1 or 2!")

    return re.sub("([{}])".format(re.escape(escape_chars)), r"\\\1", text)


def truncate_text(text: str, length: int = config.MAX_TITLE_LENGTH) -> str:
    """
    Return the given text, truncated at `length` characters, plus ellipsis.

    Parameters
    ----------
    text : str
        String to truncate.

    length : int
        (Default value = MAX_TITLE_LENGTH)

        Length to which to truncate the text, not including three characters of
        ellipsis.

    Returns
    -------
    str
        New string containing the truncated text, plus ellipsis.

    """
    return text[:length] + (text[length:] and "...")


def polish_text(text: str) -> str:
    """
    Return the given text without newline characters.

    Parameters
    ----------
    text : str
        Text to polish

    Returns
    -------
    str
        New string containing the polished text.

    """
    return text.replace("\n", " ")


def prefix_reddit_url(url: str) -> str:
    """
    Return the url with reddit's base url as a prefix.

    Parameters
    ----------
    url : str
        Url to prefix

    Returns
    -------
    str
        New string containing the prefixed url

    """
    if url is None or len(url) == 0 or url.startswith("http"):
        return url
    if url[0] != "/":
        url = "/" + url
    return f"https://www.reddit.com{url}"


def get_urls_from_text(text: str) -> List[str]:
    """
    Return a list of the reddit urls present in the given text.

    Parameters
    ----------
    text : str
        Text to search for urls.

    Returns
    -------
    array
        Array containing all the reddit links extracted from the text.

    """
    polished = polish_text(text)
    urls = list()
    for word in polished.split(" "):
        w_lower = word.lower()
        if "reddit.com" in w_lower:
            urls.append(word.partition("/?")[0])
        if "redd.it" in w_lower:
            urls.append(
                f'https://www.reddit.com/comments/{word.partition("redd.it/")[2]}'
            )
        if "reddit.app.link" in w_lower:
            try:
                resp: Response = requests.get(
                    word,
                    headers={"User-agent": os.getenv("REDDIT_USER_AGENT")},  # type: ignore
                    allow_redirects=False,
                    timeout=config.REQUESTS_TIMEOUT,
                )
                start = resp.text.find("https://")
                url = resp.text[start : resp.text.find('"', start)]
                if len(url) > 0:
                    urls.append(url.partition("/?")[0])
            except RequestException:
                pass
    return urls


def get(obj: Any, attr: str, default: Any = None) -> Any:
    """
    Return the value of `attr` if it exists and is not None, default otherwise.

    Useful when you don't want to have a `KeyError` raised if the attribute is
    missing in the object.

    Parameters
    ----------
    obj : object
        The object for which to return the attribute.
    attr : str
        The key of the attribute to return.
    default : any
        (Default value = None)

        What to return if `obj` doesn't have the `attr` attribute, or if it is
        None.

    Returns
    -------
    any
        The attribute or `default`.

    """
    return obj[attr] if attr in obj and obj[attr] is not None else default


def chained_get(obj: object, attrs: List[str], default: Any = None) -> Any:
    """
    Get for nested objects.

    Travel the nested object based on `attrs` array and return the value of
    the last attr if not None, default otherwise.

    Useful when you don't want to have a `KeyError` raised if an attribute of
    the chain is missing in the object.

    Parameters
    ----------
    obj : object
        The object for which to return the attribute.
    attrs : array
        Array of keys to search for recursively.
    default : any
        (Default value = None)

        What to return if `obj` doesn't have any of the `attrs` attributes, or
        if they are None.

    Returns
    -------
    any
        The attribute corresponding to the right-most key in `attrs`, if it
        exists and is not None, `default` otherwise.

    """
    for attr in attrs:
        obj = get(obj, attr, default)
        if obj == default:
            break
    return obj
