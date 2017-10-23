import asyncio
import requests
from bs4 import BeautifulSoup
from douban_rating.rating import Rating

query_urls = {
    'book': 'https://book.douban.com/j/subject_suggest?q={query}',
    'movie': 'https://movie.douban.com/j/subject_suggest?q={query}'
}


def query(query_type, title):
    query_url = query_urls.get(query_type)
    response = requests.get(query_url.format(query=title))
    items = response.json()

    return query_items(items)


def query_items(items):
    futures = [query_item(item) for item in items]
    event_loop = asyncio.get_event_loop()

    done_futures, _ = event_loop.run_until_complete(asyncio.wait(futures))

    return [future.result() for future in done_futures]


async def query_item(item):
    event_loop = asyncio.get_event_loop()
    future = event_loop.run_in_executor(None, requests.get, item.get('url'))
    response = await future
    beautiful_soup = BeautifulSoup(response.text, 'html.parser')
    rating = beautiful_soup.select_one('.rating_num').text

    return Rating(item.get('title'), rating)
