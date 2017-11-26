"""
Interface en ligne de commande pour flumel
cli.py --help pour plus d’informations
"""

import argparse

# pylint: disable=C0103
parser = argparse.ArgumentParser(
    description='Interface en ligne de commande pour flumel')
parser.add_argument('command', help='''init (création du fichier de conf)''')
# pylint: disable=C0103
args = parser.parse_args()


def user_input(label, default=''):
    """
    Simplifie la récupération des variables pour la configuration
    """
    question = '{label} [{default}] ?'.format(label=label, default=default)
    return str(input(question) or default)


def init():
    """
    Génération du fichier de configuration

    Quand il n’y a pas de valeur par défaut (entre crochets) dans la question
    il faut impérativement répondre quelque chose.

    Une fois généré, le fichier flumel.cfg peut être modifié.
    """
    import configparser
    config = configparser.ConfigParser()
    config.read('flumel.cfg')
    print(init.__doc__)

    try:
        config.add_section('Bot')
    except configparser.DuplicateSectionError:
        print('Erreur : fichier flumel.cfg déjà présent')
        return False

    print('Réglages du bot')
    config.set('Bot', 'Email', user_input('Adresse email du bot'))
    config.set('Bot', 'Login', user_input('Identifiant email'))
    config.set('Bot', 'Password', user_input('Mot de passe email'))

    print('Réglages IMAP')
    config.add_section('IMAP')
    config.set('IMAP', 'Host', user_input('Adresse du serveur IMAP'))
    config.set('IMAP', 'Port',
               user_input('Port (465 SSL, 587 StartTLS)', '465'))

    print('Réglages SMTP')
    config.add_section('SMTP')
    config.set('SMTP', 'Host', user_input('Adresse du serveur SMTP'))
    config.set('SMTP', 'Port',
               user_input('Port (993 SSL, 143 StartTLS)', '993'))

    print('Commandes')
    config.add_section('Keywords')
    config.set('Keywords', 'Subscribe',
               user_input('Pour s’abonner', 'Abonnement'))
    config.set('Keywords', 'Unsubscribe',
               user_input('Pour se désabonner', 'Désabonnement'))

    print('Base de données')
    config.add_section('DB')
    config.set('DB', 'Path',
               user_input('Nom et chemin de la base', 'flumel.sqlite'))
    config.set('DB', 'Debug', user_input('Debug activé', 'no'))

    print('Tâches')
    config.add_section('Queue')
    config.set('Queue', 'Path',
               user_input('Nom et chemin de la base', 'huey.sqlite'))
    config.set(
        'Queue', 'Management',
        user_input(
            'Fréquence de vérification IMAP (*/n = toutes les n minutes)',
            '*/3'))
    config.set(
        'Queue', 'Subscriptions',
        user_input(
            'Fréquence de vérification des flux (*/n = toutes les n heures)',
            '*/'))

    print('Journalisation')
    config.add_section('Logging')
    config.set('Logging', 'Path',
               user_input('Nom et chemin du journal', 'flumel.log'))
    config.set('Logging', 'Level',
               user_input('Niveau (DEBUG, INFO, WARN, ERROR, CRITICAL)',
                          'INFO'))

    with open('flumel.cfg', 'w') as f:
        config.write(f)

    print('flumel.cfg généré !')


def stats():
    """
    Statistiques
    """
    pass


if args.command == 'init':
    init()
elif args.command == 'stats':
    stats()
else:
    print('commande inconnue')
