"""
Tâches flumel

Elles sont gérées par [huey](https://huey.readthedocs.io)

Les instances Feed / Subscription ne sont pas passées en paramètres des tâches
car les connexions à la bdd ne peuvent être pickle-isées par huey

Pour lancer l’ordonnanceur: `huey_consumer flumel.tasks.huey`

Voir le dossier [systemd](https://gitlab.com/canarduck/flumel/tree/master/systemd)
pour piloter le service
"""

import re
from datetime import datetime
from email.utils import parseaddr
from time import mktime

import feedfinder2
import feedparser
from huey import crontab
from huey.contrib.sqlitedb import SqliteHuey
from newspaper import Article

from . import settings
from .loggers import logger
from .models import Feed, Subscription
from .tools import IMAP, decode_email_header, format_template, sendmail

# Si always_eager est True, on execute sans attendre
# Si blocking est True, la tâche n'est pas lancée en asynchrone
# settings.TESTING est True si le module unittest est chargé
# pylint: disable=C0103
huey = SqliteHuey(
    'flumel',
    filename=settings.QUEUE_PATH,
    always_eager=settings.TESTING,
    blocking=settings.TESTING)


@huey.task()
def subscribe(url, email):
    """
    Abonnement de `email` à `url`
    Cas de figure :
    * flux invalide
    * déjà abonné à `url`
    * abonnement réussi
    """
    logger.debug('Demande d’abonnement de %s à %s', email, url)
    parsed_feed = feedparser.parse(url)
    if not parsed_feed.entries:  # si entries est vide ça n’est pas un flux
        logger.info('%s n’est pas un flux', url)
        return find_feeds(url, email)
    feed, created = Feed.get_or_create(url=url)
    if created:
        feed.title = parsed_feed.feed.title
        feed.save()
        logger.info('Nouveau flux %s (%s)', feed.title, feed.url)
    return feed.subscribe(email)


@huey.task(retries=3, retry_delay=60)
def find_feeds(url, email):
    """
    Peut être que l’url transmise n’est pas un flux, mais un site.
    On cherche les flux, si :
    * 0 -> erreur
    * 1 -> abonnement à ce flux
    * n -> email de la liste des flux par mail pour que l’utilisateur décide
    """
    logger.debug('Recherche de flux sur %s', url)
    feeds = feedfinder2.find_feeds(url)
    if not feeds:
        subscribe_invalid(url, email)
        return False
    if len(feeds) == 1:
        subscribe(feeds[0], email)
        return True
    subscribe_choices(url, feeds, email)
    return True


@huey.task()
def unsubscribe(url, email):
    """
    Désabonnement de `email` à `url`
    Cas de figure :
    * flux inconnu
    * `email` n’est pas abonné à `url`
    * désabonnement réussi
    Si après le désabonnement plus personne n'est inscrit au flux, on le supprime
    """
    try:
        feed = Feed.get(url=url)
    except Feed.DoesNotExist:
        unsubscribe_failure(url, email)
        return False
    return feed.unsubscribe(email)


@huey.periodic_task(crontab(hour=settings.QUEUE_SUBSCRIPTIONS_PERIOD))
def subscriptions():
    """
    Boucle sur les flux en base et envoi les articles dont la date
    est > à la dernière vérification

    Une fois traité on met à jour les dates

    La vérification prend en compte les headers des flux
    @see https://pythonhosted.org/feedparser/http-etag.html
    """
    for feed in Feed.select():
        logger.info('Début analyse du flux %s', feed.url)
        parsed_feed = feedparser.parse(
            feed.url, etag=feed.etag, modified=feed.modified_at)
        logger.debug('Pas de modification depuis le %s', feed.sent_at)
        for entry in parsed_feed.entries:
            # published_parsed est un timetuple pas une datetime
            published_at = datetime.fromtimestamp(
                mktime(entry.published_parsed))
            logger.debug('Entrée %s publiée le %s', entry.id, published_at)
            if not feed.sent_at or published_at > feed.sent_at:
                logger.info('Analyse de l’article %s avant envoi', entry.link)
                article = Article(
                    entry.link,
                    keep_article_html=True,
                    fetch_images=False,
                    verbose=False)
                article.download()
                article.parse()
                logger.info('%d abonnement(s) pour ce flux',
                            feed.subscriptions.count())
                for subscription in feed.subscriptions:
                    send_article(article, feed.url, subscription.email)
        # mise à jour des infos sur le cache du flux
        feed.sent_at = datetime.now()
        feed.save()
        logger.debug('Fin analyse du flux %s', feed.url)


@huey.periodic_task(crontab(minute=settings.QUEUE_MANAGEMENT_PERIOD))
def management():
    """
    Consulte la boite mail et execute les commandes
    Une fois le mail traité il est marqué à supprimer et la boite est purgée
    """
    logger.info('Vérification de la boite mail %s', settings.BOT_EMAIL)
    server = IMAP()
    for number in server.inbox:
        message = server.get(number)
        _, sender = parseaddr(message['From'])  # (nom, email)
        subject = decode_email_header(message['Subject'])
        logger.debug('message %s « %s » par %s', number, subject, sender)
        # Abonnement ?
        match_subscribe = re.search(settings.REGEX_SUBSCRIBE, subject,
                                    re.IGNORECASE | re.DOTALL)
        if match_subscribe:
            subscribe(match_subscribe.group('url'), sender)
        # Désabonnement ?
        match_unsubscribe = re.search(settings.REGEX_UNSUBSCRIBE, subject,
                                      re.IGNORECASE | re.DOTALL)
        if match_unsubscribe:
            unsubscribe(match_unsubscribe.group('url'), sender)
        # On supprime le mail
        server.delete(number)
    server.close()


@huey.periodic_task(crontab(day='*/1'))
def page():
    """
    Génération de la page dédiée à cette instance flumel
    """
    pass


@huey.task()
def subscribe_success(url, email):
    """
    Email de confirmation d'inscription
    """
    feed = Feed.get(url=url)
    subscription = Subscription.get(feed=feed, email=email)
    logger.info('Abonnement de %s à %s', subscription.email,
                subscription.feed.url)
    html = format_template(
        'subscribe_success.html',
        url=subscription.feed.url,
        title=subscription.feed.title)
    title = 'Abonnement réussi à {title}'.format(title=subscription.feed.title)
    sendmail(subscription.email, title, html)


@huey.task()
def subscribe_choices(url, feeds, email):
    """
    Email avec la liste des flux trouvés sur l’url
    """
    logger.info('%d flux trouvés sur %s', len(feeds), url)
    links = '<ul>'
    for feed in feeds:
        links += '<li><a href="mailto:{mailto}?subject={keyword}%20{feed}">{feed}</a></li>'.format(
            mailto=settings.BOT_EMAIL,
            keyword=settings.SUBSCRIBE_KEYWORD,
            feed=feed)
    links += '</ul>'

    html = format_template('subscribe_choices.html', url=url, links=links)
    title = 'Choix du flux pour {url}'.format(url=url)
    sendmail(email, title, html)


@huey.task()
def unsubscribe_success(url, email):
    """
    Email de confirmation de désinscription
    """
    logger.info('Désabonnement de %s à %s', email, url)
    html = format_template('unsubscribe_success.html', url=url)
    title = 'Désabonnement du flux {url}'.format(url=url)
    sendmail(email, title, html)


@huey.task()
def subscribe_duplicate(url, email):
    """
    Email de notification déjà inscrit au flux
    """
    feed = Feed.get(url=url)
    subscription = Subscription.get(feed=feed, email=email)
    logger.info('%s est déjà inscrit à %s', subscription.email, feed.url)
    html = format_template(
        'subscribe_duplicate.html',
        url=subscription.feed.url,
        title=subscription.feed.title)
    title = 'Déjà abonné à {title}'.format(title=feed.title)
    sendmail(subscription.email, title, html)


@huey.task()
def subscribe_invalid(url, email):
    """
    Email de notification url du flux invalide
    """
    logger.info('Flux %s invalide demandé par %s', url, email)
    html = format_template('subscribe_invalid.html', url=url)
    title = 'Flux RSS non trouvé sur {url}'.format(url=url)
    sendmail(email, title, html)


@huey.task()
def unsubscribe_failure(url, email):
    """
    Email d’échec d’une désinscription car soit :
    * le flux est inconnu
    * la personne n’y est pas abonné
    """
    logger.info('Impossible de désabonner %s à %s', email, url)
    html = format_template('unsubscribe_failure.html', url=url)
    title = 'Échec de désabonnement au flux {url}'.format(url=url)
    sendmail(email, title, html)


@huey.task()
def send_article(article, url, email):
    """
    Email contenant un nouvel article du flux `url`
    """
    feed = Feed.get(url=url)
    logger.info('Envoi de %s à %s', article.title, email)
    html = format_template(
        'article.html',
        title=article.title,
        body=article.article_html,
        feed_url=feed.url,
        feed_title=feed.title,
        bot=settings.BOT_EMAIL)
    title = '[{feed}] {title}'.format(feed=feed.title, title=article.title)
    article.nlp()
    sendmail(
        email,
        title,
        html,
        Title=feed.title,
        Keywords=', '.join(article.keywords))
