from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe
from django.contrib.sites.models import Site
from bs4 import BeautifulSoup

class User(AbstractUser):

    def unread_notification_no(self):
        return self.usersystemnotification_set.filter(read=False,site=2).count()

    def unread_notifications(self):
        return self.usersystemnotification_set.filter(read=False,site=2).order_by('-created_at')[:3]

    def read_notifications(self):
        return self.usersystemnotification_set.filter(read=True,site=2).order_by('-created_at')[:3]

    def read_notification_no(self):
        return self.usersystemnotification_set.filter(read=True,site=2).count()

    def unread_message_no(self):
        return self.usersystemmessage_set.filter(read=False,site=2).count()

    def unread_messages(self):
        return self.usersystemmessage_set.filter(read=False,site=2).order_by('-created_at')[:3]

    def read_messages(self):
        return self.usersystemmessage_set.filter(read=True,site=2).order_by('-created_at')[:3]

    def read_message_no(self):
        return self.usersystemmessage_set.filter(read=True,site=2).count()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'%s' % (self.username)

class UserSystemMessage(models.Model):
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    subject = models.CharField(max_length=30)
    message = models.TextField()
    def short_message(self):
        msg_no_html = BeautifulSoup(self.message, "lxml").get_text()
        return msg_no_html[:30]+'..'
    image_path = models.CharField(max_length=100, blank=True, default='')
    def image_tag(self):
        if self.image_path != '':
            url = mark_safe('<img src="%s" height="40" />' % (self.image_path))
        else:
            url = ''
        return url
    read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'%s - %s %s' % (self.user, self.subject, self.short_message())

class UserSystemNotification(models.Model):
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    notification = models.TextField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    def short_notification(self):
        notification_no_html = BeautifulSoup(self.notification, "lxml").get_text()
        return notification_no_html[:30]+'..'
    icon_class = models.CharField(max_length=50, blank=True)
    read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'%s - %s' % (self.user, self.short_notification())
