"""Miscellaneous helpers for the whole application."""

from typing import List, Optional, Any
import re
import requests
from requests import Response
from requests.exceptions import RequestException
import icontract

from pyreddit.config.config import MAX_TITLE_LENGTH, secret
import telegram


@icontract.require(
    lambda subreddit: subreddit is not None and len(subreddit) > 0,
    "subreddit must not be None",
)
@icontract.ensure(lambda result, subreddit: subreddit in result)
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


@icontract.require(
    lambda text: text is not None and len(text) > 0,
    "text must not be None",
)
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


@icontract.require(
    lambda text, reverse: text is not None and len(text) > 0,
    "text must not be None",
)
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


@icontract.require(
    lambda text: text is not None,
    "text must not be None",
)
def escape_markdown(text: str) -> str:
    """
    Return the given text with escaped common markdown characters.

    .. seealso::
        Official Telegram supported Markdown documentation:
        https://core.telegram.org/bots/api#Markdown-style

    Parameters
    ----------
    text : str
        Unescaped text to escape.

    Returns
    -------
    str
        New string containing the escaped text.

    """
    return telegram.utils.helpers.escape_markdown(text, version=2)


@icontract.require(
    lambda text, length: text is not None,
    "text must not be None",
)
@icontract.require(
    lambda text, length: length > 0,
    "length must not be <= 0",
)
def truncate_text(text: str, length: int = MAX_TITLE_LENGTH) -> str:
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


@icontract.require(
    lambda text: text is not None and len(text) > 0,
    "text must not be None",
)
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


@icontract.require(
    lambda text: text is not None and len(text) > 0,
    "text must not be None",
)
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
                    headers={"User-agent": secret.REDDIT_USER_AGENT},
                    allow_redirects=False,
                )
                start = resp.text.find("https://")
                url = resp.text[start : resp.text.find('"', start)]
                if len(url) > 0:
                    urls.append(url.partition("/?")[0])
            except RequestException:
                pass
    return urls


@icontract.require(lambda obj, attr, default: obj is not None, "obj must not be None")
@icontract.require(lambda obj, attr, default: attr is not None, "attr must not be None")
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


@icontract.require(lambda obj, attrs, default: obj is not None, "obj must not be None")
@icontract.require(
    lambda obj, attrs, default: attrs is not None and len(attrs) > 0,
    "attrs must not be None",
)
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
