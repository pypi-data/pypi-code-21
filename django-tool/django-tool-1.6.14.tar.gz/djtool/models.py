from django.db import models
import shortuuid
from djtool import Common


def createuuid():
    return shortuuid.uuid()


class BaseSimple(models.Model):
    uuid = models.CharField(
        'ID',
        max_length=22,
        primary_key=True,
        default=createuuid,
        editable=False)

    class Meta:
        abstract = True


class BaseMiddle(BaseSimple):
    add_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-add_time']

    def add_time_local(self):
        return Common.utcToLocal(self.add_time).strftime('%F %T')


class Base(BaseMiddle):
    del_state_type = ((0, '已删除'), (1, '默认'))
    modified_time = models.DateTimeField('修改时间', auto_now=True)
    del_state = models.IntegerField(
        '删除状态', choices=del_state_type, default=1, db_index=True)

    class Meta:
        abstract = True


class AdminBase(Base):
    unionuuid = models.CharField('统一用户ID', max_length=22)
    showname = models.CharField('姓名', max_length=50)

    class Meta:
        abstract = True

    def __str__(self):
        return self.showname
