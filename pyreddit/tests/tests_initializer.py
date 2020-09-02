from dotenv import load_dotenv
import os

from ..services.services_wrapper import ServicesWrapper


def init_tests():
    load_dotenv(
        dotenv_path=os.path.join(os.path.dirname(__file__), "../config/.env")
    )

    ServicesWrapper.init_services()
