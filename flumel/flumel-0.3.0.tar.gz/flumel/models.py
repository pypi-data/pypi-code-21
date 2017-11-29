"""
Modèles de la base de données
"""
from datetime import datetime

import peewee

from .loggers import logger
from . import settings
from . import tasks

logger.info('Ouverture BDD %s', settings.DB_PATH)
# pylint: disable=C0103
db = peewee.SqliteDatabase(settings.DB_PATH)


class Feed(peewee.Model):
    """
    Un flux
    """
    url = peewee.TextField(primary_key=True)
    title = peewee.TextField(null=True)
    created_at = peewee.DateTimeField(default=datetime.now)
    sent_at = peewee.DateTimeField(null=True, index=True)
    # @see https://pythonhosted.org/feedparser/http-etag.html
    modified_at = peewee.DateTimeField(null=True, index=True)
    etag = peewee.CharField(null=True, index=True)

    # pylint: disable=R0903
    class Meta:
        """Classement"""
        database = db
        order_by = ('title', )

    def subscribe(self, email):
        """
        Abonnement de `email` à ce flux
        """
        _, created = Subscription.get_or_create(feed=self, email=email)
        if created:
            logger.debug('[DB] Abonnement de %s à %s', email, self.url)
            tasks.subscribe_success(url=self.url, email=email)
            return True
        logger.debug('[DB] %s déjà abonne à %s', email, self.url)
        tasks.subscribe_duplicate(url=self.url, email=email)
        return False

    def unsubscribe(self, email):
        """
        Désabonnement de `email` à ce flux. Si plus personne d’abonné on
        delete le flux
        """
        try:
            subscription = Subscription.get(feed=self, email=email)
            subscription.delete_instance()
            logger.debug('[DB] Désabonnement de %s à %s', email, self.url)
            tasks.unsubscribe_success(self.url, email)
            if not self.subscriptions.count():
                logger.info('[DB] Faute d’abonnés, flux %s supprimé', self.url)
                self.delete_instance()
            return True
        except Subscription.DoesNotExist:  # échoue silencieusement
            logger.debug(
                '[DB] Désabonnement de %s à %s impossible car non abonné',
                email, self.url)
            tasks.unsubscribe_failure(self.url, email)
            return False


class Subscription(peewee.Model):
    """
    Un abonnement (un flux + un email)
    """
    feed = peewee.ForeignKeyField(Feed, related_name='subscriptions')
    email = peewee.TextField()
    created_at = peewee.DateTimeField(default=datetime.now)

    # pylint: disable=R0903
    class Meta:
        """Classement et clé primaire composite feed+email"""
        database = db
        primary_key = peewee.CompositeKey('feed', 'email')
        order_by = ('feed', 'email', 'created_at')


logger.info('Création des tables si nécessaire')
db.create_tables([Feed, Subscription], safe=True)
