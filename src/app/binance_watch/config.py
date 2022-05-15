from os import getenv


def api_key():
    key = getenv('API_KEY')
    return key


def secret_key():
    key = getenv('SECRET_KEY')
    return key
