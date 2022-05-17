import os
from dotenv import load_dotenv

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        'environments.env')


def bot_token():
    load_dotenv(dotenv_path=ENV_PATH)
    token = os.getenv('BOT_TOKEN')
    return token


def client_id():
    self_id = os.getenv('CLIENT_ID')
    return int(self_id)
