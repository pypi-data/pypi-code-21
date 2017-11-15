import random

from gabc_generator import Generator

FIRST_NAMES = ("李", "王", "张",
               "刘", "陈", "杨", "黄", "赵", "周", "吴", "徐", "孙", "朱", "马", "胡", "郭", "林",
               "何", "高", "梁", "郑", "罗", "宋", "谢", "唐", "韩", "曹", "许", "邓", "萧", "冯",
               "曾", "程", "蔡", "彭", "潘", "袁", "於", "董", "余", "苏", "叶", "吕", "魏", "蒋",
               "田", "杜", "丁", "沈", "姜", "范", "江", "傅", "钟", "卢", "汪", "戴", "崔", "任",
               "陆", "廖", "姚", "方", "金", "邱", "夏", "谭", "韦", "贾", "邹", "石", "熊", "孟",
               "秦", "阎", "薛", "侯", "雷", "白", "龙", "段", "郝", "孔", "邵", "史", "毛", "常",
               "万", "顾", "赖", "武", "康", "贺", "严", "尹", "钱", "施", "牛", "洪", "龚", "东方",
               "夏侯", "诸葛", "尉迟", "皇甫", "宇文", "鲜于", "西门", "司马", "独孤", "公孙", "慕容", "轩辕",
               "左丘", "欧阳", "皇甫", "上官", "闾丘", "令狐")


class NameGenerator(Generator):
    """用于随机生成汉字"""

    @staticmethod
    def get_one_char():
        val = random.randint(0x4E00, 0x9FBF)
        return chr(val)

    @staticmethod
    def get_first_name():
        return random.choice(FIRST_NAMES)

    @staticmethod
    def get_last_name():
        return '{}{}'.format(NameGenerator.get_one_char(), NameGenerator.get_one_char())

    @staticmethod
    def get():
        return '{}{}'.format(NameGenerator.get_first_name(), NameGenerator.get_last_name())
