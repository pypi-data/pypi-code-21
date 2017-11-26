import requests
import selenium
from urllib.parse import urlparse


def cookietransfer(source, target, url):
    acceptable_browser_list = [selenium.webdriver.chrome.webdriver.WebDriver]
    if (isinstance(source, requests.sessions.Session) and
            type(target) in acceptable_browser_list):
        __from_session_to_driver(source, target, url)
    elif (type(source) in acceptable_browser_list and
            isinstance(target, requests.sessions.Session)):
        __from_driver_to_session(source, target, url)
    else:
        raise TypeError("Unacceptable source and target combination")


def __from_session_to_driver(session, driver, url):
    url_info = urlparse(url)
    driver.get("{}://{}".format(url_info.scheme, url_info.netloc))
    for cookie in session.cookies:
        driver.add_cookie(
            {'name': cookie.name, 'value': cookie.value,
             'path': cookie.path, 'expiry': cookie.expires,
             'domain': cookie.domain})


def __from_driver_to_session(driver, session, url):
    for cookie in driver.get_cookies():
        session.cookies.set(
            cookie['name'], cookie['value'], domain=cookie['domain'])
