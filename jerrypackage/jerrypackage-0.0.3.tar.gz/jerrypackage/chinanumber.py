# -*- coding: utf-8 -*-


class InvalidChinaNumberError(ValueError):
    pass


CN_NUM = {
    '〇': 0,
    '一': 1,
    '二': 2,
    '三': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7,
    '八': 8,
    '九': 9,

    '零': 0,
    '壹': 1,
    '贰': 2,
    '叁': 3,
    '肆': 4,
    '伍': 5,
    '陆': 6,
    '柒': 7,
    '捌': 8,
    '玖': 9,

    '貮': 2,
    '两': 2,
}
CN_UNIT = {
    '十': 10,
    '拾': 10,
    '百': 100,
    '佰': 100,
    '千': 1000,
    '仟': 1000,
    '万': 10000,
    '萬': 10000,
    '亿': 100000000,
    '億': 100000000,
    '兆': 1000000000000,
}


def from_china(cn):
    """
    convert chinese numeral to number
    :param cn:
        a chinese numeral
    :return:
        a  number
    """
    lcn = list(cn)
    unit = 0    # 当前的单位
    ldig = []   # 临时数组

    while lcn:
        cndig = lcn.pop()

        if cndig in CN_UNIT:
            unit = CN_UNIT.get(cndig)
            if unit == 10000:
                ldig.append('w')        # 标示万位
                unit = 1
            elif unit == 100000000:
                ldig.append('y')        # 标示亿位
                unit = 1
            elif unit == 1000000000000:     # 标示兆位
                ldig.append('z')
                unit = 1

            continue

        else:
            dig = CN_NUM.get(cndig)

            if dig is None:
                raise InvalidChinaNumberError('Input China number:{} is NOT valid'.format(cn))

            if unit:
                dig = dig*unit
                unit = 0

            ldig.append(dig)

    if unit == 10:    # 处理10-19的数字
        ldig.append(10)

    ret = 0
    tmp = 0

    while ldig:
        x = ldig.pop()

        if x == 'w':
            tmp *= 10000
            ret += tmp
            tmp = 0

        elif x == 'y':
            tmp *= 100000000
            ret += tmp
            tmp = 0

        elif x == 'z':
            tmp *= 1000000000000
            ret += tmp
            tmp = 0

        else:
            tmp += x

    ret += tmp
    return ret


def to_china(num):
    """
    convert integer to Chinese numeral
    TODO: only return '' for now
    :param num:
        a number
    :return:
        a string present Chinese number
    """
    return ''
