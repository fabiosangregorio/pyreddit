import json
import pathlib
import unittest
from unittest.mock import patch

from parameterized import param, parameterized

from pyreddit.exceptions import (
    PostRequestError,
    PostRetrievalError,
    SubredditDoesntExistError,
    SubredditPrivateError,
)
from pyreddit.models.content_type import ContentType
from pyreddit.models.media import Media
from pyreddit.models.post import Post

from .. import reddit
from .tests_initializer import init_tests


class TestReddit(unittest.TestCase):
    def setUp(self):
        init_tests()

    def _get_json(self, filename):
        with open(pathlib.Path(__file__).parent / "json" / filename) as f:
            return json.load(f)

    @patch("pyreddit.reddit.requests.get")
    def test_get_json_exception(self, mock_get):
        mock_get.return_value.ok = True
        mock_get.return_value.json = None
        with self.assertRaises(PostRequestError):
            reddit._get_json("https://reddit.com/r/test")

    @patch("pyreddit.reddit.requests.get")
    def test_get_json_404(self, mock_get):
        mock_get.return_value.ok = False
        mock_get.return_value.json = lambda: {
            "message": "Not Found",
            "error": 404,
        }
        mock_get.return_value.status_code = 404
        with self.assertRaises(SubredditDoesntExistError):
            reddit._get_json(
                "https://reddit.com/r/n_o_t_a_n_a_m_e_i_h_ox_p_e/random"
            )

    @patch("pyreddit.reddit.requests.get")
    def test_get_json_private(self, mock_get):
        mock_get.return_value.ok = False
        mock_get.return_value.json = lambda: {
            "reason": "private",
            "message": "Forbidden",
            "error": 403,
        }
        mock_get.return_value.status_code = 403
        with self.assertRaises(SubredditPrivateError):
            reddit._get_json(
                "https://reddit.com/r/n_o_t_a_n_a_m_e_i_h_ox_p_e/random",
            )

    @patch("pyreddit.reddit.requests.get")
    def test_get_json_valid(self, mock_get):
        mock_json = self._get_json(
            "r-funny-my_weather_app_nailed_it_today.json"
        )
        mock_get.return_value.ok = True
        mock_get.return_value.json = lambda: mock_json
        mock_get.return_value.status_code = 200

        json_data = reddit._get_json(
            "https://www.reddit.com/r/funny/comments/fxuefa/my_weather_app_nailed_it_today.json"
        )
        self.assertEqual(json_data, mock_json[0])

    @patch("pyreddit.reddit.requests.get")
    def test_get_json(self, mock_get):
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 200
        mock_get.return_value.history = [0]
        mock_get.return_value.json = lambda: {
            "data": {"children": [{"mock": True}]}
        }
        mock_get.return_value.url = "https://www.reddit.com/search.json"
        with self.assertRaises(SubredditDoesntExistError):
            reddit._get_json(
                "https://www.reddit.com/r/funny/comments/fxuefa/my_weather_app_nailed_it_today.json"
            )

    @parameterized.expand(
        [
            # text post
            param(
                subreddit="r/showerthoughts",
                mock_json_filename="showerthoughts-text_post.json",
                expected=Post(
                    subreddit="r/Showerthoughts",
                    permalink="https://www.reddit.com/r/Showerthoughts/comments/gjpq1t/we_will_be_slaves_to_our_dental_health_for_the/",
                    title="We will be slaves to our dental health for the rest of our lives.",
                    text="",
                ),
            ),
            # photo post
            param(
                subreddit="r/pics",
                mock_json_filename="pics-photo_post.json",
                expected=Post(
                    subreddit="r/pics",
                    permalink="https://www.reddit.com/r/pics/comments/gjm3ik/hadnt_drawn_for_10_years_pre_lockdown_this_is_my/",
                    title="Hadn't drawn for 10 years pre lockdown. This is my 2nd piece during lockdown. Pencil on paper.",
                    text="",
                ),
            ),
            # crosspost
            param(
                subreddit="r/bicycling",
                mock_json_filename="bicycling_crosspost.json",
                expected=Post(
                    subreddit="r/bicycling",
                    permalink="https://www.reddit.com/r/bicycling/comments/aevkgj/finally_know_how_to_crosspost/",
                    title="Finally know how to crosspost",
                    text="",
                ),
            ),
        ]
    )
    @patch("pyreddit.reddit._get_json")
    @patch("pyreddit.services.services_wrapper.ServicesWrapper.get_media")
    def test_get_post(
        self,
        mock_get_media,
        mock_get_json,
        subreddit,
        mock_json_filename,
        expected,
    ):
        mock_get_json.return_value = self._get_json(mock_json_filename)[0]
        mock_get_media.return_value = Media("", ContentType.PHOTO)
        post = reddit.get_post(subreddit)

        self.assertEqual(post.subreddit, expected.subreddit)
        self.assertEqual(post.permalink, expected.permalink)
        self.assertEqual(post.title, expected.title)
        self.assertEqual(post.text, expected.text)

    @parameterized.expand(
        [
            # text post
            param(
                subreddit="r/videos",
                mock_json_filename="videos_youtube-post.json",
                expected=Post(
                    subreddit="r/videos",
                    permalink="https://www.reddit.com/r/videos/comments/gm1m12/its_been_ten_years_since_the_if_my_grandmother/",
                    title='It\'s been ten years since the "If my Grandmother had wheels she would have been a bike" moment',
                    text="",
                ),
            )
        ]
    )
    @patch("pyreddit.reddit._get_json")
    @patch("pyreddit.services.services_wrapper.ServicesWrapper.get_media")
    def test_get_post_youtube(
        self,
        mock_get_media,
        mock_get_json,
        subreddit,
        mock_json_filename,
        expected,
    ):
        media = Media(
            "https://www.youtube.com/watch?v=A-RfHC91Ewc", ContentType.YOUTUBE
        )
        mock_get_json.return_value = self._get_json(mock_json_filename)[0]
        mock_get_media.return_value = media
        post = reddit.get_post(subreddit)

        # self.assertEqual(post, expected)
        self.assertEqual(post.subreddit, expected.subreddit)
        self.assertEqual(post.permalink, expected.permalink)
        self.assertEqual(post.title, expected.title)
        self.assertIn(media.url, post.text)

    @patch("pyreddit.reddit._get_json")
    @patch("pyreddit.services.services_wrapper.ServicesWrapper.get_media")
    def test_get_post_exception(
        self,
        mock_get_media,
        mock_get_json,
    ):
        mock_get_json.return_value = {"data": {"children": []}}
        mock_get_media.return_value = Media("", ContentType.PHOTO)
        with self.assertRaises(PostRetrievalError):
            reddit.get_post("r/test")
