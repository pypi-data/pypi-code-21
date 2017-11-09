import click
from zipline.data.bundles import register
from zipline.data import bundles as bundles_module
from cn_zipline.bundles.tdx_bundle import tdx_bundle
import pandas as pd
import os
from functools import partial
import cn_stock_holidays.zipline.default_calendar


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
def ingest(bundle, assets, minute, assets_version, show_progress):
    if bundle == 'tdx':
        if assets:
            if not os.path.exists(assets):
                raise FileNotFoundError
            df = pd.read_csv(assets, names=['symbol', 'name'], dtype=str, encoding='gbk')
            register('tdx', partial(tdx_bundle, df, minute), 'SHSZ')
        else:
            register('tdx', partial(tdx_bundle, None, minute), 'SHSZ')

    bundles_module.ingest(bundle,
                          os.environ,
                          pd.Timestamp.utcnow(),
                          assets_version,
                          show_progress,
                          )


def register_tdx():
    register('tdx', partial(tdx_bundle, None, False), 'SHSZ')


if __name__ == '__main__':
    import sys

    if sys.argv[1]:
        assets = sys.argv[1]
        if not os.path.exists(assets):
            raise FileNotFoundError
        df = pd.read_csv(assets, names=['symbol', 'name'], dtype=str, encoding='gbk')
        register('tdx', partial(tdx_bundle, df, False), 'SHSZ')
    else:
        register('tdx', partial(tdx_bundle, None, False), 'SHSZ')
    bundles_module.ingest('tdx',
                          os.environ,
                          pd.Timestamp.utcnow(),
                          show_progress=True,
                          )
    # main()
