"""."""
import re
import time
import jieba


class Address(object):
    """docstring for Address."""

    def __init__(self):
        """."""
        self.gcountry = []
        self.gcountryAdd = []
        self.gcountryMap = dict()
        self.gprovince = ""
        self.gcity = ""
        self.gdistrict = ""
        self.gdistrictMap = dict()
        self.gcityMap1 = dict()
        self.gcityMap2 = dict()

    def get_address(
            self, id, business_address, address, registered_address):
        """."""
        country = ''
        province = ''
        city = ''
        district = ''
        detail = ''
        ctime = time.strftime('%Y-%m-%d %H:%M:%S')
        params = []
        if business_address:
            country, province, city, district, detail = self.parse_address(
                business_address)
            params.append((id, address, 3, country, province,
                           city, district, detail, ctime))
            # print('%s,%s,%s,%s' % (ctime, id, country, province))
        if address:
            country, province, city, district, detail = self.parse_address(
                address)
            params.append((id, address, 2, country, province,
                           city, district, detail, ctime))
            # print('%s,%s,%s,%s' % (ctime, id, country, province))
        if registered_address:
            country, province, city, district, detail = self.parse_address(
                registered_address)
            params.append((id, address, 1, country, province,
                           city, district, detail, ctime))
            # print('%s,%s,%s,%s' % (ctime, id, country, province))
        return country, params

    def parse_address(self, address):
        """
        地址解析.

        return:country,province,city,district,detail
        """
        country = ''
        province = ''
        city = ''
        district = ''
        detail = ''
        addCut = jieba.lcut(address)
        try:
            if addCut[0] in self.gcountry:
                country = self.gcountryMap.get(addCut[0])
            elif addCut[0] in self.gcountryAdd:
                country = addCut[0]
            if country:
                addCut.remove(addCut[0])

            if country and country != '中国':
                return (country, '', '', '', ''.join(addCut))

            # 解析省份，直辖市为特殊情况解析出市
            if not province:
                match = re.search(self.gprovince, addCut[0])
                if match:
                    country = '中国'
                    province = match.group(1)
                    if match.group(1) in ['北京', '天津', '上海', '重庆']:
                        city = match.group(1)
                    addCut.remove(addCut[0])
            if not city:
                match = re.search(self.gcity, addCut[0])
                if match:
                    city = match.group(1)
                    if not province:
                        id = self.gcityMap2.get(match.group(1))
                        province = self.gcityMap1.get(int(id / 10000) * 10000)
                        country = "中国"
                    addCut.remove(addCut[0])
            if city:
                match = re.search(self.gdistrict, addCut[0])
                if match:
                    district = match.group()
                    addCut.remove(addCut[0])
            elif province and not city and not district:
                match = re.findall(self.gdistrict, addCut[0])
                provinceNum = self.gcityMap2.get(province)
                if provinceNum:
                    provinceNum = int(provinceNum / 10000)
                    for m in match:
                        districtNum = self.gdistrictMap.get(m)
                        if provinceNum == int(districtNum / 10000):
                            district = m
                            city = self.gcityMap1.get(
                                int(districtNum / 100) * 100)
                            addCut.remove(addCut[0])
            detail = ''.join(addCut)
        except IndexError as e:
            print(e)
        return (country, province, city, district, detail)
