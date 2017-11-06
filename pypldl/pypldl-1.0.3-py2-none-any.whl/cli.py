import logging
from .core import Task, DownloadManager

def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(prog='pypldl')
    parser.add_argument('--list-handlers', action='store_true',
            help="list available plugins and exit")
    parser.add_argument('-o', '--output',
            help="download directory")
    parser.add_argument('-v', '--verbose', action='store_true',
            help="be verbose")
    parser.add_argument('uri', nargs='?',
            help="URI to download")
    args = parser.parse_args()

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(
            level=log_level,
            datefmt='%H:%M:%S',
            format='%(asctime)s %(levelname)s %(name)s - %(message)s')

    if args.list_handlers:
        from .core import plugin_handlers
        for cls in plugin_handlers:
            print cls.handler_name
        return
    elif not args.uri:
        parser.error("no URI to download")

    logging.debug("create task")
    task = Task.from_uri(args.uri)
    task.outdir = args.output

    logging.debug("create DownloadManager")
    dm = DownloadManager()
    logging.debug("start task")
    task.start(dm)
    while not task.join(2):
        progress, status = task.progress()
        logging.info("%3.f%% -- %s", progress * 100, status)


if __name__ == '__main__':
    main()
