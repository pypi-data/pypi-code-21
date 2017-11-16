import random

from .area_generator import AreaGenerator
from .birthday_generator import BirthdayGenerator
from .gabc_generator import Generator
from .mobile_generator import MobileGenerator
from .name_generator import NameGenerator


def ck_num17(nums):
    if len(nums) != 17:
        raise IndexError()
    CKS = {  # 此处实际是无需使用字典的，使用一个包含11个元素的数组便可，数组中存放
        0: '1',  # 相应位置的号码，但是这也正好演示了Python高级数据结构的使用
        1: '0',
        2: 'x',
        3: '9',
        4: '8',
        5: '7',
        6: '6',
        7: '5',
        8: '4',
        9: '3',
        10: '2'
    }
    wi = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    total = 0
    for index, val in enumerate(nums):
        total = total + val * wi[index]
    return CKS[total % 11]


class PersonGenerator(Generator):
    @staticmethod
    def get():
        name = NameGenerator.get()
        area = AreaGenerator.get()
        birthday = BirthdayGenerator.get()
        index = random.randrange(111, 999)
        gender = '男' if index % 2 == 1 else '女'
        mobile = MobileGenerator.get()
        num17 = '{area}{birth}{index}'.format(area=area[0], birth=birthday, index=index)
        ck = ck_num17([int(i) for i in num17])
        return {
            'name': name,
            'id_no': '{}{}'.format(num17, ck),
            'address': '{area} {road}路 {no}号 {block}小区 {party}单元 {house}室'.format(area=area[1],
                                                                                  road=NameGenerator.get_last_name(),
                                                                                  no=random.randint(100, 2000),
                                                                                  block=NameGenerator.get_last_name(),
                                                                                  party=random.randint(1, 3),
                                                                                  house=random.randint(100, 600)
                                                                                  ).replace('\n', ''),
            'gender': gender,
            'mobile': mobile
        }
