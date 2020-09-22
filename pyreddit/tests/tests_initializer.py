import logging

from .. import reddit


def init_tests():
    reddit.init()
    logging.disable(logging.ERROR)
