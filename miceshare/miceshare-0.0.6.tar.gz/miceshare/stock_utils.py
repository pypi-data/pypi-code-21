# coding: utf-8


def get_stock_code(stock_code):
    """
    转换数字股票代码id,600136.XSHG->600136
    :param stock_code:
    :return:
    """
    code = stock_code
    idx = stock_code.find('.')
    if idx > 0:
        code = code[0:idx]
    return code

def get_stock_type(stock_code):
    """
    TODO 抽到工具类
    判断股票ID对应的证券市场
    匹配规则
    ['50', '51', '60', '90', '110'] 为 sh
    ['00', '13', '18', '15', '16', '18', '20', '30', '39', '115'] 为 sz
    ['5', '6', '9'] 开头的为 sh， 其余为 sz
    :param stock_code:股票ID, 若以 'sz', 'sh' 开头直接返回对应类型，否则使用内置规则判断
    :return 'sh' or 'sz'"""
    stock_code = str(stock_code)
    if stock_code.startswith(('sh', 'sz')):
        return stock_code[:2]
    if stock_code.startswith(('50', '51', '60', '73', '90', '110', '113', '132', '204', '78')):
        return 'sh'
    if stock_code.startswith(('00', '13', '18', '15', '16', '18', '20', '30', '39', '115', '1318')):
        return 'sz'
    if stock_code.startswith(('5', '6', '9')):
        return 'sh'
    return 'sz'