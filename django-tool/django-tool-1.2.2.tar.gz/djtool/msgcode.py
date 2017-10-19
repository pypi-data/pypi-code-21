tips = {}

# 通用模块
common_seccess = {
    '20000': '成功',
    '20001': '添加成功',
    '20002': '修改成功',
    '20003': '保存成功',
    '20004': '发送成功',
    '20005': '获取成功',
}

common_fail = {
    '50000': '失败',
    '50001': '添加失败',
    '50002': '修改失败',
    '50003': '保存失败',
    '50004': '发送失败',
    '50005': '获取失败',
    '50007': '已存在',
    '50008': '验证码错误',
    '50010': '内部错误',
    '50011': '请求缺少参数',
    '50012': '请求参数不合法',
    '50013': 'post内容不合法',
    '50014': '未找到链接',
    '50015': 'access_token不合法',
    '50016': 'refresh_token不合法',
    '50017': '请求认证不合法(主要是check_sum不合法)',
    '50018': '重复发送相同请求',
    '50019': '请求超出最大调用频率',
    '50020': '文件格式不对，请使用CSV格式',
    '50021': 'access_token过期',
}

common = dict(common_seccess, **common_fail)

user_seccess = {
    '21001': '登录成功',
    '21002': '注册成功',
}

user_fail = {
    '61000': '请重新登录',
    '61001': '用户未注册',
    '61002': '密码不正确',
    '61003': '用户已存在',
    '61004': '手机号已存在',
    '61005': '用户ID不存在',
    '61006': '该用户处于封号期间',
    '61007': '用户名或密码错误',
    '61008': '手机号格式不正确',
    '61009': '手机号不能为空',
    '61010': '密码不能为空',
}

user = dict(user_seccess, **user_fail)

m = [common, user]
for row in m:
    tips.update(row)
