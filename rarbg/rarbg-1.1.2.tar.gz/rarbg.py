''' rarbg api → rss
    https://torrentapi.org/apidocs_v2.txt '''

import asyncio

from datetime import datetime, timedelta
from email.utils import formatdate
from urllib.parse import parse_qs

from aiohttp import ClientSession, web
from dateutil import parser
from humanize import naturalsize
from jinja2 import Template
import click

API_ENDPOINT = 'https://torrentapi.org/pubapi_v2.php'
API_RATE_LIMIT = 2  # seconds/request
TOKEN_LIFESPAN = timedelta(minutes=15)

TEMPLATE = Template('''\
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
    <channel>
        <title>{{title}}</title>
        <link>https://torrentapi.org/apidocs_v2.txt</link>
        <ttl>15</ttl>
        {% for entry in entries %}
        <item>
            <title>{{entry.title}} ({{entry.hsize}})</title>
            <description/>
            <guid>{{entry.hash}}</guid>
            <pubDate>{{entry.pubdate}}</pubDate>
            <enclosure
                url="{{entry.download | e}}"
                length="{{entry.size}}"
                type="application/x-bittorrent" />
        </item>
        {% endfor %}
    </channel>
</rss>''')

app = web.Application()
app.token = None
app.token_got = datetime.now()
app.counter = 0
app.lock = asyncio.Lock()


def pretty(data: dict):
    return ', '.join(['='.join(pair) for pair in data.items()])


async def fetch_json(*args, **kwds):
    resp = await app.s.get(*args, **kwds)
    return await resp.json()


async def refresh_token():
    token_expired = datetime.now() > app.token_got + TOKEN_LIFESPAN
    if not app.token or token_expired:
        data = await fetch_json(API_ENDPOINT, params={'get_token': 'get_token'})
        app.token = data['token']
        app.token_got = datetime.now()
        click.secho('refresh token - {}'.format(app.token), fg='yellow')


async def api(params):
    app.counter += 1
    request_id = app.counter
    query_text = pretty(params)
    click.secho('[{}] {}'.format(request_id, query_text), fg='cyan')

    async with app.lock:
        await refresh_token()
        params.update(token=app.token, format='json_extended')
        data = await fetch_json(API_ENDPOINT, params=params)
        await asyncio.sleep(API_RATE_LIMIT)

    error, results = data.get('error'), data.get('torrent_results')

    if error:
        click.secho('[{}] {}'.format(request_id, error), fg='red')
        if 'get_token' in error:
            await refresh_token()
        else:
            return web.HTTPServiceUnavailable(text=error)

    for i in results:
        i.update(
            pubdate=formatdate(parser.parse(i['pubdate']).timestamp()),
            hsize=naturalsize(i['size'], gnu=True),
            hash=parse_qs(i['download'])['magnet:?xt'][0].split(':')[-1],
        )

    click.secho('[{}] {} results'.format(request_id, len(results)), fg='green')

    result = TEMPLATE.render(title='rarbg', entries=results)
    return web.Response(text=result, content_type='text/xml')


async def rarbg_rss(request):
    params = dict(request.GET)
    if 'string' in request.match_info:
        params.update(mode='search', search_string=request.match_info['string'])
    if 'imdb' in request.match_info:
        params.update(mode='search', search_imdb=request.match_info['imdb'])
    if 'tvdb' in request.match_info:
        params.update(mode='search', search_tvdb=request.match_info['tvdb'])
    return await api(params)


async def on_shutdown(app):
    app.s.close()


app.router.add_route('GET', '/', rarbg_rss)
app.router.add_route('GET', '/search/{string}', rarbg_rss)
app.router.add_route('GET', '/imdb/{imdb}', rarbg_rss)
app.router.add_route('GET', '/tvdb/{tvdb}', rarbg_rss)
app.on_shutdown.append(on_shutdown)


@click.command()
@click.option('-p', '--port', default=4444, type=int)
@click.option('-h', '--host', default='0.0.0.0')
def main(port, host):
    loop = asyncio.get_event_loop()
    app.s = ClientSession(loop=loop)
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()
