import time
__author__ = 'zhoumx'

import pandas as pd
from sqlalchemy import create_engine

from  hotelindex.config import configs
from hotelindex.crawler.Wyn88Crawler import  Wyn88Crawler

class Utility:

    def __init__(self):
        self.mysqlurl = "mysql+pymysql://{}:{}@{}/{}?charset=utf8".format(
            configs["mysql"]["user"],
            configs["mysql"]["password"],
            configs["mysql"]["host"],
            configs["mysql"]["database"]
        )
        self.engine = create_engine(self.mysqlurl)
        self.cr = Wyn88Crawler()

    def WYN88RoomPrice_to_mysql(self,retryCount=10,sem=30,days=1,pause=10):
        for _ in range(retryCount):
            time.sleep(pause)
            try:
                roomPrices = self.cr.getRoomPrice(sem=sem,days=days)
            except Exception as e:
                print(e)
                sem = sem - 5
            else:
                df = pd.DataFrame(roomPrices)
                fetchTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                df["FetchTime"] = fetchTime
                # 多值字段设置为字符串类型
                df['MemberDetails'] = df['MemberDetails'].astype(str)
                df['PromoDetails'] = df['PromoDetails'].astype(str)
                df.to_sql(configs["mysql"]["wyn88_room_price_tab_name"], self.engine, if_exists='append')
                # 更新酒店信息
                self.WYN88Hotel_to_mysql(self.hotelDetais)
                break

    def WYN88Hotel_to_mysql(self,hotels):
        df_hotels = pd.DataFrame(hotels)
        fetchTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        df_hotels["FetchTime"] = fetchTime
        # 多值字段设置为字符串类型
        df_hotels['Service'] = df_hotels['Service'].astype(str)
        df_hotels['ULogo'] = df_hotels['ULogo'].astype(str)
        df_hotels.to_sql(configs["mysql"]["wyn88_hotel_tab_name"], self.engine, if_exists='append')


if __name__ == "__main__":
    u =Utility()
    u.WYN88RoomPrice_to_mysql()