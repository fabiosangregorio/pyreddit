import unittest

from parameterized import param, parameterized

from pyreddit.models.content_type import ContentType
from pyreddit.models.media import Media
from pyreddit.models.post import Post

from .tests_initializer import init_tests


class TestPost(unittest.TestCase):
    def setUp(self):
        init_tests()

    def test_get_msg(self):
        post = Post("r/subreddit", "https://permalink", "title", "text")
        msg = post.get_msg()

        self.assertIn("r/subreddit", msg)
        self.assertIn("https://permalink", msg)
        self.assertIn("title", msg)
        self.assertIn("text", msg)

    @parameterized.expand(
        [
            param(
                media=Media("", ContentType.VIDEO), expected=ContentType.VIDEO
            ),
            param(
                media=Media("", ContentType.PHOTO), expected=ContentType.PHOTO
            ),
            param(
                media=Media("", ContentType.YOUTUBE),
                expected=ContentType.YOUTUBE,
            ),
            param(media=None, expected=ContentType.TEXT),
        ]
    )
    def test_get_type(self, media, expected):
        post = Post("", "", "", "", media)
        self.assertEqual(post.get_type(), expected)
