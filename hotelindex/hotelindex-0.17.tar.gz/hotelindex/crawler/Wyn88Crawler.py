
__author__ = 'zhoumx'

import aiohttp
import asyncio
from lxml import etree
from urllib.request import urlopen, Request
import json
import datetime



class Wyn88Crawler:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.cityCodes = {} # {'1101': '北京市'}
        self.hotelCodes = {}
        self.hotelDetais = []
        self.roomPrices = []
        self.event_loop = asyncio.get_event_loop();
        # asyncio.BoundedSemaphore(),限制同时运行协程数量
        self.sem = asyncio.BoundedSemaphore(30)

    def initCityCodes(self):
        if len(self.cityCodes) == 0:
            request = Request("http://wap.wyn88.com/Home/City")
            lines = urlopen(request, timeout=60).read()
            linestr = lines.decode('utf-8');
            html = etree.HTML(linestr)
            result = html.xpath("//li/a")
            for el_a in result:
                if len(el_a.xpath("@cityno")) == 1:
                    self.cityCodes[el_a.xpath("@cityno")[0]] = el_a.xpath("text()")[0]
            print("initCityCodes:Done,count={}".format(len(self.cityCodes)))

    def readHotel(self, json_resp):
        self.hotelDetais += json.loads(json_resp.get("JsonData"))["Rows"]

    def readRoomPrices(self, json_resp):
        # pass
        hotelStatus = json.loads(json_resp.get("JsonData"))["hotelStatus"]
        hotelDetail = json.loads(json_resp.get("JsonData"))["hotelDetail"]
        for hs in hotelStatus:
            hs.update({"HotelName": hotelDetail["HotelName"]})
            hs.update({"HotelNo": hotelDetail["HotelNo"]})
        self.roomPrices += hotelStatus

    async def fetch(self, urlstr, callback=None):
        with(await self.sem):
            async with self.session.get(urlstr) as resp:
                assert resp.status == 200
                resp_json = await resp.json()
                callback(resp_json)

    def initHotels(self):
        self.initCityCodes()
        if len(self.hotelCodes) == 0:
            urlstr = "http://wap.wyn88.com/Hotel/GetHotelList?pageindex=1&pagesize=1000&cityno={0}"
            tasks = [self.fetch(urlstr.format(k), self.readHotel) for k in self.cityCodes]
            results = self.event_loop.run_until_complete(asyncio.gather(*tasks))
            for h in self.hotelDetais:
                self.hotelCodes[h["HotelNo"]] = h["HotelName"]
            print("initHotels:Done,count={}".format(len(self.hotelCodes)))

    def initRoomPrices(self, indate, days):
        self.initHotels()
        urlstr = "http://wap.wyn88.com/Hotel/GetHotelInfo?hotelno={0}&Indate={1}&Outdate={2}"
        tasks = []
        for d in range(days):
            df = indate + datetime.timedelta(days=d)
            dn = indate + datetime.timedelta(days=d + 1)
            tasks.extend([self.fetch(urlstr.format(k, df, dn), self.readRoomPrices) for k in self.hotelCodes])
        results = self.event_loop.run_until_complete(asyncio.gather(*tasks))
        print("initRoomPrices:Done,count={}".format(len(self.roomPrices)))


    def getRoomPrice(self, sem=None, indate=datetime.date.today(), days=1):
        if sem:
            self.sem = asyncio.BoundedSemaphore(sem)
        self.initRoomPrices(indate, days)
        return self.roomPrices


