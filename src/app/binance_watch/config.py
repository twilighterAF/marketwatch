import os
from dotenv import load_dotenv

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                        'environments.env')


def api_key():
    load_dotenv(dotenv_path=ENV_PATH)
    key = os.getenv('API_KEY')
    return key


def secret_key():
    key = os.getenv('SECRET_KEY')
    return key
