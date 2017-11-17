# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools

from datetime import datetime

import demiurge


BASE_URL = ('http://staticmd1.lavozdelinterior.com.ar/sites/default/'
            'files/Datafactory/html/v3/htmlCenter/data/deportes/'
            'futbol/primeraa/pages/es/')


class Match(demiurge.Item):
    home = demiurge.TextField(selector='div.local div.equipo')
    away = demiurge.TextField(selector='div.visitante div.equipo')
    home_goals = demiurge.TextField(selector='div.local div.resultado')
    away_goals = demiurge.TextField(selector='div.visitante div.resultado')
    status = demiurge.TextField(selector='div.detalles div.estado')

    _date = demiurge.TextField(selector='div.detalles div.dia')
    _time = demiurge.TextField(selector='div.detalles div.hora')

    @property
    def is_finished(self):
        return self.status.lower() == 'finalizado'

    @property
    def in_progress(self):
        return self.status.lower() in [
            '1er tiempo', 'entretiempo', '2do tiempo']

    @property
    def datetime(self):
        if self._time is None:
            return None

        if self._time.startswith('-'):
            match_time = "00:00"
        else:
            match_time = self._time[:5]

        date_and_time = "%s %s" % (self._date, match_time)
        value = datetime.strptime(date_and_time, "%d-%m-%Y %H:%M")
        return value

    class Meta:
        selector = 'div.mc-matchContainer'
        encoding = 'utf-8'


class Round(demiurge.Item):
    _css_class = demiurge.AttributeValueField(attr='class')
    title = demiurge.TextField(selector='div.subHeader')
    matches = demiurge.RelatedItem(Match)

    class Meta:
        selector = 'div.fase div.fecha'
        encoding = 'utf-8'
        base_url = BASE_URL + 'fixture.html'

    @property
    def is_current(self):
        return 'show' in self._css_class


class StandingsRow(demiurge.Item):
    team = demiurge.TextField(selector='td.team')
    pts = demiurge.TextField(selector='td.puntos')
    p = demiurge.TextField(selector='td.hidden-xs:eq(0)')
    w = demiurge.TextField(selector='td.hidden-xs:eq(1)')
    d = demiurge.TextField(selector='td.hidden-xs:eq(2)')
    l = demiurge.TextField(selector='td.hidden-xs:eq(3)')
    f = demiurge.TextField(selector='td.hidden-xs:eq(4)')
    a = demiurge.TextField(selector='td.hidden-xs:eq(5)')
    gd = demiurge.TextField(selector='td.hidden-xs:eq(6)')

    class Meta:
        selector = 'tr.linea'
        encoding = 'utf-8'


class Standings(demiurge.Item):
    rows = demiurge.RelatedItem(StandingsRow)

    class Meta:
        selector = 'div.posiciones table.table'
        encoding = 'utf-8'
        base_url = BASE_URL + 'posiciones.html'


class RelegationRow(demiurge.Item):
    team = demiurge.TextField(selector='td.team')
    average = demiurge.TextField(selector='td.promediodescenso')

    before1 = demiurge.TextField(selector='td.hidden-xs:eq(0)')
    before2 = demiurge.TextField(selector='td.hidden-xs:eq(1)')
    before3 = demiurge.TextField(selector='td.hidden-xs:eq(2)')
    current = demiurge.TextField(selector='td.puntosactual')

    pts = demiurge.TextField(selector='td.puntosdescenso')
    p = demiurge.TextField(selector='td.jugadosdescenso')

    class Meta:
        selector = 'tr.linea'
        encoding = 'utf-8'


class Relegation(demiurge.Item):
    rows = demiurge.RelatedItem(RelegationRow)

    class Meta:
        selector = 'div.descenso table.table'
        encoding = 'utf-8'
        base_url = BASE_URL + 'descenso.html'


# API methods

def get_standings():
    """Return tournament standings."""
    standings = Standings.one()
    return standings.rows


def get_relegation():
    """Return tournament relegation table."""
    relegation = Relegation.one()
    return relegation.rows


def get_round(n=None):
    """Return round n (or current if n is None)."""
    round_n = None
    fixture = Round.all()
    for r in fixture:
        if ((n is None and r.is_current) or
                (n is not None and r.title == 'Fecha %s' % n)):
            round_n = r
            break
    return round_n


def get_matches_in_progress():
    """Return matches in progress."""
    fixture = Round.all()
    matches = [m for m in itertools.chain(*(r.matches for r in fixture))
               if m.in_progress]
    return matches


def get_matches_for_team(team):
    """Return matches for given team."""
    fixture = Round.all()
    matches = [m for m in itertools.chain(*(r.matches for r in fixture))
               if m.home == team or m.away == team]
    return matches
