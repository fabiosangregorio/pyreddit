"""
Reddit API interface module.

Contains all the functions to call Reddit APIs, retrieve the desired information
and build pyreddit objects.
"""

import random
from typing import Any
import os

import requests


from . import helpers
from .models.post import Post
from .models.content_type import ContentType
from .exceptions import (
    PostRequestError,
    SubredditPrivateError,
    SubredditDoesntExistError,
    PostRetrievalError,
    RedditError,
)
from .services.services_wrapper import ServicesWrapper


def _get_json(post_url: str) -> Any:
    """
    Get post json from Reddit API and handle all request/json errors.

    Parameters
    ----------
    post_url : str
        post url to fetch from the Reddit API.

    Returns
    -------
    json
        Json containing the post data.

    """
    try:
        response = requests.get(
            f"{post_url}.json",
            headers={"User-agent": os.getenv("REDDIT_USER_AGENT")},
        )
        json = response.json()
        # some subreddits have the json data wrapped in brackets, some do not
        json = json if isinstance(json, dict) else json[0]
    except Exception as e:
        raise PostRequestError({"post_url": post_url}) from e

    if json.get("reason") == "private":
        raise SubredditPrivateError()
    if (
        json.get("error") == 404
        or len(json["data"]["children"]) == 0
        or (len(response.history) > 0 and "search.json" in response.url)
    ):
        # r/opla redirects to search.json page but subreddit doesn't exist
        raise SubredditDoesntExistError()

    return json


def get_post(post_url: str) -> Post:
    """
    Get the post from the Reddit API and construct the Post object.

    Parameters
    ----------
    post_url : str
        post url to fetch from the Reddit API.

    Returns
    -------
    `pyreddit.models.post.Post`
        Post object containing all the retrieved post information.

    """
    json = _get_json(post_url)
    assert json is not None

    try:
        idx = random.randint(0, len(json["data"]["children"]) - 1)
        data = json["data"]["children"][idx]["data"]
        subreddit = data["subreddit_name_prefixed"]
        permalink = helpers.prefix_reddit_url(data["permalink"])
        post_title = data["title"]
        post_text = helpers.truncate_text(data["selftext"])
        content_url = data["url"]

        media = None
        if "/comments/" not in content_url:
            media = ServicesWrapper.get_media(content_url, data)
            assert media is not None
            if media.type == ContentType.YOUTUBE:
                post_text = (
                    f"{post_text}\n\n[Link to youtube video]({media.url})"
                )

        post = Post(subreddit, permalink, post_title, post_text, media)
        return post

    except Exception as e:
        if issubclass(type(e), RedditError):
            raise e
        raise PostRetrievalError({"post_url": post_url}) from e
