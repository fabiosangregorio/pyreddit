"""Module for Post class."""

from typing import Optional

from .content_type import ContentType
from ..helpers import escape_markdown, prefix_reddit_url
from ..models.media import Media


class Post:
    """
    Represents a Reddit post.

    Parameters
    ----------
    subreddit : str
        Subreddit within which the post was created (or crossposted).
    permalink : str
        Reddit permalink of the post.
    title : str
        Title of the post.
    text : str
        Description of the post.
    media : `pyreddit.models.media.Media`
        (Default value = None)

        Media associated with the post (if present), None otherwise. This
        determines the post type.

    """

    def __init__(
        self,
        subreddit: str,
        permalink: str,
        title: str,
        text: str,
        media: Optional[Media] = None,
    ):

        self.subreddit = subreddit
        self.permalink = permalink
        self.title = title
        self.text = text
        self.media = media

    def get_footer(self) -> str:
        """
        Get footer of the post.

        This includes a link to the subreddit and a link to the post.
        """
        subreddit_url = prefix_reddit_url(self.subreddit)
        return (
            f"[Link to post]({self.permalink}) \\| "
            f"[{escape_markdown(self.subreddit)}]({subreddit_url})"
        )

    def get_msg(self) -> str:
        """
        Get the full message of the post.

        This includes post title, description and footer.
        """
        return (
            f"*{escape_markdown(self.title)}*"
            f"\n{escape_markdown(self.text)}"
            f"\n\n{self.get_footer()}"
        )

    def get_type(self) -> ContentType:
        """Return the post type: this is determined by the media type, if present."""
        return self.media.type if self.media else ContentType.TEXT
