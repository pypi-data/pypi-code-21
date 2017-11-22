from .base import *


class UserRegisterData(BaseData):
    def __init__(self, user_tag=None, nick_name=None, avatar=None, wx_union_id=None,
                 phone=None, gender=None, age=None, birth=None, country=None,
                 province=None, city=None, language=None, address=None,
                 industry=None, company=None, job=None, interest=None):
        self.data = OptionalDict()
        self.data['user_tag'] = user_tag
        self.data['nick_name'] = nick_name
        self.data['avatar'] = avatar
        self.data['wx_union_id'] = wx_union_id
        self.data['phone'] = phone
        self.data['gender'] = gender
        self.data['age'] = age
        self.data['birth'] = birth
        self.data['country'] = country
        self.data['province'] = province
        self.data['city'] = city
        self.data['language'] = language
        self.data['address'] = address
        self.data['industry'] = industry
        self.data['company'] = company
        self.data['job'] = job
        self.data['interest'] = interest


class UserUpdateData(BaseData):
    def __init__(self, user_id=None, user_tag=None, nick_name=None, avatar=None,
                 wx_union_id=None, phone=None, gender=None, age=None, birth=None,
                 country=None, province=None, city=None, language=None, address=None,
                 industry=None, company=None, job=None, interest=None):
        self.data = OptionalDict()
        self.data['user_id'] = user_id
        self.data['user_tag'] = user_tag
        self.data['nick_name'] = nick_name
        self.data['avatar'] = avatar
        self.data['wx_union_id'] = wx_union_id
        self.data['phone'] = phone
        self.data['gender'] = gender
        self.data['age'] = age
        self.data['birth'] = birth
        self.data['country'] = country
        self.data['province'] = province
        self.data['city'] = city
        self.data['language'] = language
        self.data['address'] = address
        self.data['industry'] = industry
        self.data['company'] = company
        self.data['job'] = job
        self.data['interest'] = interest


class UserQueryData(BaseData):
    def __init__(self, user_id=None, phone=None, wx_union_id=None):
        self.data = OptionalDict()
        self.data['user_id'] = user_id
        self.data['phone'] = phone
        self.data['wx_union_id'] = wx_union_id
