from pathlib import Path

import factory

from arcgis_marketplace import factories


class WebMapingAppTxtFactory(factories.WebMapingAppFactory):
    file = factory.django.FileField(
        filename='test.txt',
        from_path=(Path(__file__).parent / 'test.txt').as_posix())


class WebMapingAppZipFactory(factories.WebMapingAppFactory):
    file__from_path = (Path(__file__).parent / 'test.zip').as_posix()
