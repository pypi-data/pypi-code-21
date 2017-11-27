# -*- coding: utf-8 -*-
from modelhub import __version__

from .base import BaseCommand, argument, option, types, register


@register('version')
class Command(BaseCommand):

    def run(self):
        """Show modelhub version"""
        self.echo(__version__)
