# -*- coding=utf-8 -*-
"""
Command line FLOIP XForm converter.
"""

import click

from floip import FloipSurvey


@click.command()
@click.argument('descriptor')
def cli(descriptor):
    """
    Outputs the XForm of a given FlOIP results data package descriptor.
    """
    survey = FloipSurvey(descriptor)
    click.echo(survey.xml())
