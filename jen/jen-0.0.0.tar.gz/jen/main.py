from .cli import CliApp

from .run import Run
from .build import Build


app = CliApp()
app.command(Run())
app.command(Build())


def run():
    app.call()


if __name__ == '__main__':
    run()
