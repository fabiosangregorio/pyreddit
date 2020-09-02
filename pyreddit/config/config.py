"""
Project-wide configuration variables.

.. note::
    This configuration architecture is ugly and might be changed in the Future
    for a leaner one.
"""

import os
import importlib
import logging
from typing import Any

# Dynamic environment secret configuration
secret: Any = None
_env_key = os.environ.get("PYREDDIT_MACHINE")
if _env_key is not None:
    ENV = _env_key.lower()
    secret = importlib.import_module(
        f"pyreddit.config.secret_{_env_key.lower()}"
    ).secret_config  # type: ignore
else:
    logging.warning(
        'No "PYREDDIT_MACHINE" environment variable found. Using generic secret.'
    )
    ENV = "generic"
    secret = importlib.import_module(
        "pyreddit.config.secret_generic"
    ).secret_config  # type: ignore

REDDIT_DOMAINS = ["reddit.com", "redd.it", "reddit.app.link"]
MAX_POST_LENGTH = 500
MAX_TITLE_LENGTH = 200

SENTRY_ENABLED = secret.SENTRY_TOKEN is not None and len(secret.SENTRY_TOKEN) > 0
