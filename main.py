import json
from configparser import ConfigParser
from time import sleep

import chromedriver_autoinstaller
import requests
from fake_useragent import UserAgent
from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chromedriver_autoinstaller.install()

config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

bot_token = config.get('telegram', 'bot_token')
telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
chat_id = config.get('telegram', 'chat_id')

field_ids = {
    'gdpr': 'gdpr-btn-accept-all',
    'username': 'login_mail',
    'password': 'login_password',
    'button': 'login_form_submit'
}

deezer = {
    'login_url': 'https://www.deezer.com/en/login',
    'username': config.get('deezer', 'username'),
    'password': config.get('deezer', 'password'),
}


def get_arl():
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
    options.add_argument('--headless')

    driver = webdriver.Chrome(chrome_options=options, executable_path='/usr/local/bin/chromedriver')

    driver.get(deezer['login_url'])

    sleep(5)
    driver.find_element(value=field_ids['gdpr']).click()
    sleep(2)
    driver.find_element(value=field_ids['username']).send_keys(deezer['username'])
    driver.find_element(value=field_ids['password']).send_keys(deezer['password'])
    sleep(2)
    driver.find_element(value=field_ids['button']).click()
    sleep(5)

    cookies = driver.get_cookies()

    for x in cookies:
        if x['name'] == 'arl':
            driver.quit()
            return x['value']

    driver.quit()
    return None


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
            arl = get_arl()
            if arl is not None:
                send_telegram_notification(x)
                return {
                    'arl': arl,
                    'for': x['name']
                }

        return {'arl': None, 'for': x['name']}

    return {'error': 'Unauthenticated'}
