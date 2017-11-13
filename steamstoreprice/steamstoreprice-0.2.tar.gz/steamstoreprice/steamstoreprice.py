from steamstoreprice.exception import UrlNotSteam, PageNotFound, RequestGenericError
from bs4 import BeautifulSoup
import requests


class SteamStorePrice:

    def normalizeurl(self, url):
        """
        clean the url from referal and other stuff

        :param url(string): amazon url

        :return: string(url cleaned)

        """
        if "://store.steampowered.com/app" in url:
            return url
        else:
            raise UrlNotSteam("Please check the url, it doesn't contain store.steampowered.com/app*")

    def normalizeprice(self, price):
        """
        remove the currenty from price

        :param price(string): price tag find on amazon store

        :return: float(price cleaned)

        """
        listreplace = ["€", "$", "£", "\t", "\r\n"]
        for replacestring in listreplace:
            price = price.replace(replacestring, "")
        return float(price.replace(",", "."))

    def getpage(self, url):
        """
        Get the page and raise if status_code is not equal to 200

        :param url(string): normalized(url)

        :return: bs4(html)
        """
        url = self.normalizeurl(url)
        req = requests.get(url)
        if req.status_code == 200:
            return BeautifulSoup(req.text, "html.parser")
        elif req.status_code == 404:
            raise PageNotFound("Page not found, please check url")
        else:
            raise RequestGenericError("Return Code: %s, please check url" % req.status_code)

    def getprice(self, url):
        """
        Find the price on AmazonStore starting from URL

        :param url(string): url

        :return: float(price cleaned)
        """
        body_content = self.getpage(self.normalizeurl(url))
        try:
            return self.normalizeprice(body_content.find("div", {"class": "game_purchase_price"}).contents[0])
        except AttributeError:
            return self.normalizeprice(body_content.find("div", {"class": "discount_final_price"}).contents[0])
