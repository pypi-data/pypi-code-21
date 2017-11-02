from .dns import dns
from .ssl import ssl
from .host import host
from .whois import whois
from .setup import setup
from .account import account
from .actions import actions
from .monitor import monitor
from .trackers import trackers
from .enrich import enrich, bulkenrich
from . import project
from . import artifact


def main():
    from ..userinput import get_args
    client, args = get_args()

    if args.cmd == 'dns':
        data = dns(client, **vars(args))
    elif args.cmd == 'setup':
        data = setup(**vars(args))
    elif args.cmd == 'trackers':
        data = trackers(client, **vars(args))
    elif args.cmd == 'host':
        data = host(client, **vars(args))
    elif args.cmd == 'monitor':
        data = monitor(client, **vars(args))
    elif args.cmd == 'actions':
        data = actions(client, **vars(args))
    elif args.cmd == 'ssl':
        data = ssl(client, **vars(args))
    elif args.cmd == 'account':
        data = account(client, **vars(args))
    elif args.cmd == 'whois':
        data = whois(client, **vars(args))
    elif args.cmd == 'enrich':
        data = enrich(client, **vars(args))
    elif args.cmd == 'bulkenrich':
        data = bulkenrich(client, **vars(args))
    elif args.cmd == 'project':
        if args.subcmd == 'find':
            data = project.find(client, **vars(args))
        elif args.subcmd == 'create':
            data = project.create(client, **vars(args))
        elif args.subcmd == 'update':
            data = project.update(client, **vars(args))
        elif args.subcmd == 'delete':
            data = project.delete(client, **vars(args))
        elif args.subcmd == 'tag':
            data = project.tag(client, **vars(args))
    elif args.cmd == 'artifact':
        if args.subcmd == 'find':
            data = artifact.find(client, **vars(args))
        elif args.subcmd == 'create':
            data = artifact.create(client, **vars(args))
        elif args.subcmd == 'update':
            data = artifact.update(client, **vars(args))
        elif args.subcmd == 'delete':
            data = artifact.delete(client, **vars(args))
        elif args.subcmd == 'tag':
            data = artifact.tag(client, **vars(args))
    if data is not None:
        print(data)
