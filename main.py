import json
from configparser import ConfigParser

import requests
from fastapi import FastAPI

from deezer_interface import get_arl

config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

bot_token = config.get('telegram', 'bot_token')
telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
chat_id = config.get('telegram', 'chat_id')

deezer = {
    'login_url': 'https://www.deezer.com/en/login',
    'username': config.get('deezer', 'username'),
    'password': config.get('deezer', 'password'),
}


def send_telegram_notification(authorization):
    requests.get(
        telegram_api_url,
        data={
            'chat_id': chat_id,
            'text': f"Deezer ARL issued to {authorization['name']}"
        })


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{app_id}/{token}")
def read_item(app_id: int, token: str):
    authorizations = json.loads(open('authorizations.json').read())

    for x in authorizations:
        if x['app_id'] == app_id and x['token'] == token:
            arl = get_arl(deezer)
            if arl is not None:
                send_telegram_notification(x)
                return {
                    'arl': arl,
                    'for': x['name']
                }

        return {'arl': None, 'for': x['name']}

    return {'error': 'Unauthenticated'}
