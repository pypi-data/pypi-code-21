# -*- coding: utf-8 -*-

import re
import time
import urllib.request

from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from metrovlc import buildparser


def metrosaldo(bono):
    """ return saldo and zona from metrovalencia.es """

    # titulo = None
    bonoinfo = {'bono': bono}

    urlapi = 'http://www.metrovalencia.es/tools_consulta_tsc.php?tsc='

    # try:
    url = '{_urlapi}{_bono}'.format(_urlapi=urlapi, _bono=bono)
    r = urllib.request.urlopen(url)
    enc = r.info().get_content_charset('utf-8')
    data = r.read()
    html = data.decode(enc)

    # tipo de titulo
    f = re.findall('Título: (.*)<br>', html)
    if f:
        # titulo = f[0]
        bonoinfo['titulo'] = f[0]

    # saldo
    f = re.findall('Saldo.*: (.*) <', html)
    if f:
        if '€' in str(f[0]):
            bonoinfo['moneda'] = 'Euros'
        else:
            bonoinfo['moneda'] = None

        # el saldo viene algo sucio
        s = str(f[0]).replace('€', '')
        s = s.replace(' ', '')
        s = s.replace(',', '.')

        bonoinfo['saldo'] = float(s)

    return bonoinfo


def get_estaciones():
    """ recupera todas las estaciones """

    estaciones = list()
    url = 'http://www.metrovalencia.es/tools_horarios.php'
    r = urllib.request.urlopen(url)
    enc = r.info().get_content_charset('utf-8')
    data = r.read()
    html = data.decode(enc)

    for f in re.findall('<option value="(\d*)">(.+?(?=<))', html):
        e = [int(f[0]), f[1]]
        estaciones.append(e)

    return estaciones


def _id_estacion(estacion):
    """ recuperamos el id de una estación """

    for e in get_estaciones():
        if SequenceMatcher(None, e[1], estacion).ratio() > 0.65:
            return e[0]

    return None


# http://www.metrovalencia.es/horarios.php
# ?origen=14&hini=00%3A00&hfin=23%3A59
# &destino=24&fecha=30%2F09%2F2014&calcular=1
# def metrohorarios(origen, destino):
def metrohorarios(origen, destino, fecha=None, hini='00:00', hfin='23:59'):
    """ Obtiene los horarios desde origen a destino, luego ya veré como le
    meto la fecha """

    # verificamos tanto el origen como el destino
    origen_id = _id_estacion(origen)
    destino_id = _id_estacion(destino)

    # Si alguna de las dos es None, salimos
    if not origen_id or not destino_id:
        return None

    urlapi = 'http://www.metrovalencia.es/horarios.php'
    apiparam = '?origen=%s&hini=%s&hfin=%s&destino=%s&fecha=%s&calcular=1'

    # Recuperamos la fecha y hora de la consulta
    if not fecha:
        fecha = time.strftime('%d%%2F%m%%2F%Y')
    else:
        fecha = fecha.replace('/', '%2F')
    hini = hini.replace(':', '%3A')
    hfin = hfin.replace(':', '%3A')

    # completamos los parámetros
    param = apiparam % (origen_id, hini, hfin, destino_id, fecha)

    url = urlapi + param
    # print url

    # 1. Obtenemos los números asociados al origen y destino, ya que existe una
    # relacion entre un nombre de estación y un entero.
    #
    # IDEAS: Dos soluciones, a) tenemos en el script un diccionario que nos
    # devuelve a partir del nombre un entero. b) recuperamos de la web un
    # destino vacío para recuperar luego la relación de nombre-número.
    #
    # PERO: la segunda solución serían dos llamadas, y esto no mola, pero en la
    # primera opción, si hay una reordenación de los nombre-número entonces no
    # funcionará.
    #
    # ¿SOLUCIÓN?: Algo mixto, tener el diccionario, y cuando recuperamos la web
    # aseguramos que esté bien, en otro caso, con la información ya recuperada
    # podemos volver a llamar. En el mejor de los casos es una llamada, en el
    # peor son dos. Pero siempre devolvemos el dato correctamente.

    # 2. Recuperamos

    r = urllib.request.urlopen(url)
    enc = r.info().get_content_charset('utf-8')
    data = r.read()
    html = data.decode(enc)

    soup = BeautifulSoup(html, "html.parser")
    # print soup.body.find('div', attrs={'class': 'consulta'}).text
    consulta = soup.body.find('div', attrs={'class': 'consulta'})

    # guardamos aquí todos los cambios que queremos
    reemplazos = [['<td>', ''],
                  ['</td>', ' | '],
                  ['<tr>', ''],
                  ['</tr>', '\n'],
                  ['---', '-----'],
                  ['</li>', '\n'],
                  ['Trenes con destino', ', Trenes con destino'],
                  ['Hora de salida', ', Hora de salida\n'],
                  ['Imprimir la consulta', ''],
                  ['Paso ', '\nPaso '],
                  ['td>', ' | ']]

    for reemplazo in reemplazos:
        consulta = str(consulta).replace(reemplazo[0], reemplazo[1])

    text = BeautifulSoup(consulta, "html.parser").get_text()

    return text


def main():

    """Run the command-line interface."""
    parser = buildparser.build_parser()
    options = parser.parse_args()

    if options.bono:
        # Para metrovalencia, únicamente son importantes los 10 primeros
        # dígitos, cosa bastante marciana
        bono = options.bono[0:10]
        info = metrosaldo(bono)
        if options.solosaldo:
            print('{}'.format(info['saldo']))
        else:
            strformat = 'Bono:{}, Título:{}, saldo:{} {}'
            print(strformat.format(bono, info['titulo'], info['saldo'],
                                   info['moneda']))

    if options.horario:
        origen = options.horario[0]
        destino = options.horario[1]
        horarios = metrohorarios(origen, destino, options.fecha)
        if horarios:
            print(horarios)
        else:
            print('No encuentro horarios: {} -> {}'.format(origen, destino))

    if options.estaciones:
        print('Estaciones disponibles:')
        for estacion in get_estaciones():
            print(estacion[1])


if __name__ == '__main__':
    main()
