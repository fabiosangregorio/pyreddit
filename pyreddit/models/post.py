"""Module for Post class."""

from typing import Optional

from ..helpers import escape_markdown, prefix_reddit_url
from ..models.media import Media
from .content_type import ContentType


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
        msg = f"*{escape_markdown(self.title)}*"
        if self.text is not None and len(self.text) > 0:
            msg += f"\n{escape_markdown(self.text)}"
        if self.media is not None and self.media.type == ContentType.YOUTUBE:
            # HACK: creating an empty link with the youtube video results in
            #   telegram generating the web preview for the video
            msg += f"[ ]({self.media.url})"
        msg += f"\n\n{self.get_footer()}"

        return msg

    def get_type(self) -> ContentType:
        """Return the post type: this is determined by the media type, if present."""
        return self.media.type if self.media else ContentType.TEXT
