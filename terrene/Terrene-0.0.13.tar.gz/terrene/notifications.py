from .api import BaseModelManager


class NotificationManager(BaseModelManager):
    namespace = ['notifications', 'notifications']


class NotificationManagerManager(BaseModelManager):
    namespace = ['notifications', 'managers']
