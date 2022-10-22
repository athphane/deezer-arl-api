from time import sleep

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

field_ids = {
    'gdpr': 'gdpr-btn-accept-all',
    'username': 'login_mail',
    'password': 'login_password',
    'button': 'login_form_submit'
}


def get_arl(deezer):
    options = Options()
    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--headless')

    driver = webdriver.Chrome(chrome_options=options, executable_path='/usr/local/bin/chromedriver')

    driver.get(deezer['login_url'])

    # sleep(5)

    # driver.find_element(value=field_ids['gdpr']).click()

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
