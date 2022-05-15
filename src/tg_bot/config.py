from os import getenv


def bot_token():
    token = getenv('BOT_TOKEN')
    return token


def client_id():
    self_id = getenv('CLIENT_ID')
    return int(self_id)

