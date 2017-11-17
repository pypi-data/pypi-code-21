# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import click

from fpt import api


click.disable_unicode_literals_warning = True


def show_relegation():
    """Display relegation table."""
    rows = api.get_relegation()
    total = len(rows)

    click.secho('Descenso', bold=True)
    click.secho(
        "%-3s %-25s %-5s %-3s %-10s" %
        ("POS", "EQUIPO", "  PTS", " PJ", "  PROMEDIO"))
    for i, r in enumerate(rows, start=1):
        team_str = ("{pos:<3} {row.team:<25} {row.pts:>5} "
                    "{row.p:>3} {row.average:>10}").format(pos=i, row=r)
        color = 'blue'
        if (total - 4) <= i <= total:
            # 4 last
            color = 'red'
        click.secho(team_str, fg=color)
    click.echo()
    click.secho('En zona de descenso', fg='red')


def show_standings():
    """Display standings table."""
    rows = api.get_standings()

    click.secho('Posiciones', bold=True)
    click.secho(
        "%-3s %-25s %-5s %-3s %-3s %-3s %-3s %-3s %-3s %-3s" %
        ("POS", "EQUIPO", "  PTS",
         " PJ", " PG", " PE", " PP",
         " GF", " GC", " DG")
    )
    for i, r in enumerate(rows, start=1):
        team_str = ("{pos:<3} {row.team:<25} {row.pts:>5} "
                    "{row.p:>3} {row.w:>3} {row.d:>3} {row.l:>3} "
                    "{row.f:>3} {row.a:>3} {row.gd:>3}").format(pos=i, row=r)
        color = 'blue'
        if i <= 5:
            # libertadores
            color = 'green'
        elif 5 < i <= 11:
            # sudamericana
            color = 'yellow'
        click.secho(team_str, fg=color)
    click.echo()
    click.secho('En zona de clasificación a Copa Libertadores', fg='green')
    click.secho('En zona de clasificación a Copa Sudamericana', fg='yellow')


def _show_matches(matches, enum=False):
    """Display given matches."""
    for i, m in enumerate(matches, start=1):
        home_color = away_color = 'yellow'
        if m.is_finished and m.home_goals > m.away_goals:
            home_color = 'green'
            away_color = 'red'
        elif m.is_finished and m.home_goals < m.away_goals:
            home_color = 'red'
            away_color = 'green'

        click.secho('%s  ' % m.datetime.strftime('%a %d %b, %I:%M %p'),
                    nl=False, fg='cyan')
        if enum:
            click.secho("  Fecha %2d  " % i, nl=False)
        click.secho('%-25s %2s' % (m.home, m.home_goals), fg=home_color,
                    nl=False)
        click.secho("  - ", nl=False)
        click.secho('%2s %s' % (m.away_goals, m.away.rjust(25)),
                    fg=away_color, nl=not m.in_progress)
        if m.in_progress:
            click.secho(' (%s)' % m.status)


def show_in_progress():
    """Display matches in progress."""
    matches = api.get_matches_in_progress()
    if not matches:
        click.echo('No hay partidos en juego.')
    else:
        click.secho('En juego', bold=True)
        _show_matches(matches)


def show_team_matches(team):
    """Display matches for given team."""
    matches = api.get_matches_for_team(team)
    if not matches:
        click.echo('No hay partidos para %s.' % team)
    else:
        click.secho('Fixture para %s' % team, bold=True)
        _show_matches(matches, enum=True)


def show_round(n=None):
    """Display matches for given round (or current if n is None)."""
    r = api.get_round(n=n)
    if r is None:
        click.echo('Fecha no válida.')
    else:
        click.secho(r.title, bold=True)
        _show_matches(r.matches)


@click.command()
@click.option('-f', '--fecha-nro', default=None, metavar='<fecha número>',
              help="Mostrar los partidos/resultados de la fecha dada.")
@click.option('-a', '--fecha-actual', is_flag=True,
              help="Mostrar los partidos/resultados de la fecha actual.")
@click.option('-j', '--en-juego', is_flag=True,
              help="Mostrar los partidos en juego.")
@click.option('-e', '--equipo', default=None, metavar='<nombre equipo>',
              help="Mostrar los partidos/resultados del equipo dado.")
@click.option('-p', '--posiciones', is_flag=True,
              help="Mostrar las posiciones del torneo.")
@click.option('-d', '--descenso', is_flag=True,
              help="Mostrar la tabla del descenso.")
def main(fecha_nro, fecha_actual, en_juego, equipo, posiciones, descenso):
    """
    Facilitame los Partidos del Torneo.

    Estadísticas de la primera división del fútbol argentino.
    """

    if fecha_nro:
        try:
            int(fecha_nro)
        except ValueError:
            click.echo('Fecha no válida.')
        else:
            show_round(n=fecha_nro)
        return

    if fecha_actual:
        show_round()
        return

    if en_juego:
        show_in_progress()
        return

    if equipo:
        show_team_matches(equipo)
        return

    if posiciones:
        show_standings()
        return

    if descenso:
        show_relegation()
        return

    with click.Context(main) as ctx:
        click.echo(main.get_help(ctx))


if __name__ == '__main__':
    main()
