# -*- coding: utf-8 -*-


def post_install(context):
    """Post install script"""
    if context.readDataFile('collectivequerynextprev_default.txt') is None:
        return  # pragma: no cover
    # Do something during the installation of this package
