from modislock_monitor.tasks import app
from modislock_monitor.config import load_config

config = load_config()


def main():
    argv = [
        'worker',
        '--loglevel=INFO'
    ]
    app.worker_main(argv)


if __name__ == '__main__':
    main()

