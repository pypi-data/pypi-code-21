import asyncio
import argparse
import logging
import pprint

import drophi.client

LOGGER = logging.getLogger(__name__)

def setup_log(level=logging.INFO):
    logging.basicConfig(level=level, format="[%(asctime)s] %(levelname)s pid:%(process)d %(name)s:%(lineno)d %(message)s")

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help="Show more verbose logging")

    subparsers = parser.add_subparsers(help='The command to perform')

    parser_ps = subparsers.add_parser('ps', help='Show the running containers')
    parser_ps.set_defaults(command=_ps)

    parser_events = subparsers.add_parser('events', help='Show events captured in real time')
    parser_events.set_defaults(command=_events)

    parser_service = subparsers.add_parser('service', help='Show information on docker swarm services')
    parser_service.add_argument('action', choices=['ls'], help='Show information on all services in the swarm')
    parser_service.set_defaults(command=_services)

    args = parser.parse_args()

    setup_log(level=logging.DEBUG if args.verbose else logging.INFO)

    if not hasattr(args, 'command'):
        LOGGER.info("You must select a sub-command")
        return 1

    client = drophi.client.Client()

    loop = asyncio.get_event_loop()
    try:
        result = loop.run_until_complete(args.command(args, client))
    except KeyboardInterrupt:
        result = 0
    loop.run_until_complete(client.close())
    loop.close()
    return result or 0

async def _ps(args, client):
    LOGGER.info("Running ps")
    pprint.pprint(await client.ps())

async def _events(args, client):
    async for event in client.streamevents():
        pprint.pprint(event.data)
        print('-'*20)

async def _services(args, client):
    if args.action == 'ls':
        pprint.pprint(await client.service_ls())
