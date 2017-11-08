# -*- coding:utf-8 -*- 
from django.db import models
from . import choices
from django.contrib.auth.models import User as SiteUser


class Message(models.Model):
    class Meta:
        verbose_name = u'消息'
        verbose_name_plural = verbose_name

    to_id = models.CharField(u"接收者ID", max_length=64)
    from_id = models.CharField(u"发送者ID", max_length=64)
    create_time = models.DateTimeField(u"创建时间", editable=False, auto_now_add=True)
    type = models.CharField(u'类别', max_length=16, choices=choices.CHOICES_MESSAGE_TYPE,
                            default=choices.MESSAGE_TYPE_TEXT)
    msg_id = models.IntegerField(u'编号', blank=True, null=True)
    content = models.CharField(u'内容', max_length=256, blank=True, null=True)

    def __unicode__(self):
        return "%s:%s:%s" % (self.createTime, self.toUserName, self.fromUserName)


class User(models.Model):
    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = verbose_name

    user = models.OneToOneField(SiteUser, verbose_name=u"网站用户", null=True,
                                related_name="as_wechat_user")
    openid = models.CharField(u"openId", max_length=64, primary_key=True)
    unionid = models.CharField(u"unionId", max_length=64, null=True, blank=True)
    nickname = models.CharField(u"昵称", max_length=64, null=True, blank=True)
    headimgurl = models.CharField(u"头像", max_length=255, null=True, blank=True)
    city = models.CharField(u"城市", max_length=64, null=True, blank=True)
    province = models.CharField(u"省份", max_length=64, null=True, blank=True)
    longitude = models.FloatField(u"经度", null=True, blank=True)
    latitude = models.FloatField(u"纬度", null=True, blank=True)

    def __unicode__(self):
        return self.nickname or self.openid

    def save(self, **kwargs):
        if self.user is None:
            from django.utils.crypto import get_random_string
            user_name = "%s@wechat" % get_random_string(10)
            self.user = SiteUser.objects.create_user(user_name, "", first_name=self.nickname)
        return super(User, self).save(**kwargs)


class OrderPrepayId(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = u'订单预下单号'

    order_number = models.CharField(u"订单编号", max_length=64, primary_key=True)
    prepay_id = models.CharField(u"订单编号", max_length=64)
