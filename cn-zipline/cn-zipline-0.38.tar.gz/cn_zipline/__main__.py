import click
from zipline.data.bundles import register
from zipline.data import bundles as bundles_module
from zipline.utils.cli import Date, Timestamp
import pandas as pd
import os
import cn_stock_holidays.zipline.default_calendar
from cn_zipline.bundles.tdx_bundle import register_tdx
import logbook

logger = logbook.Logger('main')


@click.group()
def main():
    pass


@main.command()
@click.option(
    '-b',
    '--bundle',
    default='quantopian-quandl',
    metavar='BUNDLE-NAME',
    show_default=True,
    help='The data bundle to ingest.',
)
@click.option(
    '-a',
    '--assets',
    default=None,
    help='a file contains list of assets to ingest. the file have tow columns, separated by comma'
         'symbol: code of asset,'
         'name:   name of asset,'
         'examples:'
         '  510050,50ETF'
         '  510500,500ETF'
         '  510300,300ETF',
)
@click.option(
    '--minute',
    default=False,
    type=bool,
    help='whether to ingest minute, default False',
)
@click.option(
    '--start',
    default=None,
    type=Date(tz='utc', as_timestamp=True),
    help='start session',
)
@click.option(
    '-o',
    '--overwrite',
    default=False,
    type=bool,
    help='whether to overwrite default start session for minute data(3 years) with start.',
)
@click.option(
    '--assets-version',
    type=int,
    multiple=True,
    help='Version of the assets db to which to downgrade.',
)
@click.option(
    '--show-progress/--no-show-progress',
    default=True,
    help='Print progress information to the terminal.'
)
def ingest(bundle, assets, minute, start,overwrite, assets_version, show_progress):
    logger.warning("this project is no longer maintained, please go to https://github.com/JaysonAlbert/zipline for the new project.")
    if bundle == 'tdx':
        if assets:
            if not os.path.exists(assets):
                raise FileNotFoundError
            df = pd.read_csv(assets, names=['symbol', 'name'], dtype=str, encoding='utf8')
            register_tdx(df,minute,start,overwrite)
        else:
            register_tdx(None,minute,start,overwrite)

    bundles_module.ingest(bundle,
                          os.environ,
                          pd.Timestamp.utcnow(),
                          assets_version,
                          show_progress,
                          )


if __name__ == '__main__':
    import sys

    start_session = pd.to_datetime('20000124', utc=True)
    if len(sys.argv) >= 2:
        assets = sys.argv[1]
        if not os.path.exists(assets):
            raise FileNotFoundError
        df = pd.read_csv(assets, names=['symbol', 'name'], dtype=str, encoding='utf8')
        register_tdx(df,start=start_session)
    else:
        register_tdx(minute=True,start=start_session)
    bundles_module.ingest('tdx',
                          os.environ,
                          pd.Timestamp.utcnow(),
                          show_progress=True,
                          )
    # main()
