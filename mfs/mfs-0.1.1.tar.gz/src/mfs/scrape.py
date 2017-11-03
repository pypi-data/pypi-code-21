import bs4
import requests
import urllib.parse as urlp
import aiohttp
import asyncio
import tqdm
import datetime
# import dateutil.parser

_KAROPKA = 'http://karopka.ru'

def _n(src):
    if src.startswith('//'):
        src = 'http:' + src
    return src


def _sluggify(text):
    if not text:
        return ''
    return ''.join([c for c in text if c.isalpha() or c.isdigit() or c in [' ', '.', '_', '-']]).rstrip()


def download_images(dl):
    # avoid to many requests(coroutines) the same time.
    # limit them by setting semaphores (simultaneous requests)
    _sema = asyncio.Semaphore(10)

    async def wait_with_progressbar(coros):
        for f in tqdm.tqdm(asyncio.as_completed(coros), total=len(coros)):
            await f

    async def download_file(url, fn):
        try:
            async with _sema, aiohttp.ClientSession() as session:
                resolved_url = await resolve_image_link(url)
                if resolved_url:
                    async with session.get(resolved_url) as resp:
                        if resp.status == 200:
                            with open(fn, 'wb') as f:
                                # print('Downloaded file {}'.format(fn))
                                f.write(await resp.read())
        except Exception as e:
            print('Download of {} failed. {}'.format(url, e))



    ioloop = asyncio.get_event_loop()
    tasks = [download_file(url, fn) for url, fn in dl]
    # wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_with_progressbar(tasks))
    # do not close the loop here - it will be closed at program exit
    return


async def resolve_image_link(url):
    """
    Resolves provided link to an image upload site to direct image link
    :param url:
    :param fn:
    :return: None if location not supported, or direct download link
    """

    # if url or hostname is empty - nothing to do
    if not url:
        return None

    # if link points to an image, just return it back
    if url.split('.')[-1] in ['jpg', 'jpeg', 'png', 'gif', 'tif', 'pdf', 'doc', 'docx', 'zip']:
        return url

    o = urlp.urlparse(url)
    hn = o.hostname
    if not hn:
        return None
    # if the link is merely to main page, then there is likely nothing to do as well
    if len(o.path) < 3:
        return None

    # keep only last two parts of the hostname. eg www.radikal.ru => radikal.ru; radikal.ru => radikal.ru
    hn = '.'.join(hn.split('.')[-2:])

    # bypass sites
    if hn in ['httpbin.org', 'karopka.ru', 'wrk.ru',]:
        return url

    # although following sites do contain images, we are not interested in them
    if hn in ['smayliki.ru', 'nick-name.ru', 'suveniri-knigi.ru', 'narod.ru', 'aceboard.net']:
        return None

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                text = await resp.text()
            else:
                print('{} returned {}'.format(url, resp.status))

    if hn in ['postimg.org', 'postimage.org']:
        return _resolve_postimg(text)
    if hn == 'vfl.ru':
        return _resolve_vfl(text)
    if hn == 'radikal.ru':
        return _resolve_radikal(text)
    if hn == 'keep4u.ru':
        return _resolve_keep4u(text)
    if hn == 'fastpic.ru':
        return _resolve_fastpic(text)

    print('{} is not supported or not an image site link'.format(url))
    return None


def _resolve_postimg(text):
    soup = bs4.BeautifulSoup(text, 'html.parser')
    src = soup.find(id='main-image').get('src')
    return src


def _resolve_vfl(text):
    soup = bs4.BeautifulSoup(text, 'html.parser')
    e = soup.find(id='f_image')
    if not e:
        return None

    return _n(e.find('img').get('src'))


def _resolve_radikal(text):
    soup = bs4.BeautifulSoup(text, 'html.parser')
    e = soup.find('div', class_='mainBlock')
    if not e:
        return None

    return _n(e.find('img').get('src'))


def _resolve_keep4u(text):
    soup = bs4.BeautifulSoup(text, 'html.parser')
    e = soup.find(id='image-viewer')
    if not e:
        return None

    return _n(e.find('img').get('src'))

def _resolve_fastpic(text):
    soup = bs4.BeautifulSoup(text, 'html.parser')
    e = soup.find(id='picContainer')
    if not e:
        return None

    return _n(e.find('img').get('src'))


def karopka_model_overview(url, dest):
    """
    Scrape karopka model overview. URL is in the form of http://karopka.ru/community/user/<user_id>/?MODEL=<model_id>
    :param url:
    :param dest:
    :return:
    """
    r = requests.get(url=url)
    r.raise_for_status()
    soup = bs4.BeautifulSoup(r.text, 'html.parser')

    # with open('d:/!/k.html', mode='w', encoding='utf-8') as f:
    #     f.write(soup.prettify(), )

    fotorama = soup.find('div', class_='fotorama')
    imgs = fotorama.find_all('img')

    # prepare the list of images to download. Original (not rescaled) images apparently stored in data-full attribute
    dl = []
    for i, img in enumerate(imgs, 1):
        dl.append((_KAROPKA + img.get('data-full'), '{}/{:04d}.jpg'.format(dest, i)))

    print('Found {} images'.format(len(dl)))
    download_images(dl)
    return dl


def karopka_forum(url, dest, follow=True):
    """
    Scrape karopka forum. URL starts from http://karopka.ru/forum/
    :param url:
    :param dest:
    :return:
    """

    def _karopka_forum(url, dest, follow=True):
        # list of images to download
        dl = []

        r = requests.get(url=url)
        r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        # with open('d:/!/k.html', mode='w', encoding='utf-8') as f:
        #     f.write(soup.prettify(), )

        posts = soup.find_all('table', class_='forum-post-table')
        print('Found {} posts on page {}'.format(len(posts), url))

        # going through posts
        for post in posts:
            # finding the post number and converting it to int
            postnr = post.find('div', class_='forum-post-number').get_text()
            postnr = int(postnr.strip().replace('#', ''))

            # 1st supported image format, when image is directly attached to the post
            # In this case every image is wrapped into construction like
            # <div class='forum-attach>
            #   <img ../>
            #   ..
            #       <a href='link to download image'/>
            #  .. </div>
            # while it's tempting to download image directly, it's not a good idea since image may be of reduced size
            # and it's best to use download link to get the image
            attachments = post.find_all('div', class_='forum-attach')
            for i, attachment in enumerate(attachments, 1):
                # print('Attachment #{}'.format(i))
                a = attachment.find('a', class_='forum-file')
                url = _KAROPKA + a.get('href')
                fn = a.find('span').get_text()
                fn = '{}/karopka{:04d}-a{:02d}-{}'.format(dest, postnr, i, fn)
                dl.append((url, fn))

            # 2nd class are the images uploaded to image sharing sites, like vfl.ru
            links = post.find('div', class_='forum-post-text').find_all('a')
            for i, link in enumerate(links, 1):
                # within the link there shall be an image, otherwise this is just a normal link
                if link.find('img'):
                    url = link.get('href')
                    if url:
                        fn = '{}/karopka{:04d}-l{:02d}.jpg'.format(dest, postnr, i)
                        dl.append((url, fn))

        print('Found {} potential image links'.format(len(dl)))

        if follow:
            print('Checking if next page is available ... ')
            next_page = soup.find('a', class_='forum-page-next')
            if next_page:
                dl += _karopka_forum(_KAROPKA + next_page.get('href'), dest)

        return dl

    dl = _karopka_forum(url=url, dest=dest, follow=follow)
    download_images(dl)
    return dl


def navsource(url, dest):
    """
    Scrape photos from http://www.navsource.narod.ru/ source
    Args:
        url:
        dest:

    Returns:

    """
    dl = []
    urlparts = url.split('/')

    r = requests.get(url=url)
    r.raise_for_status()
    soup = bs4.BeautifulSoup(r.text, 'html.parser')

    for row in soup.find_all('tr'):
        # while there are many tables numbering is going through tables - use it
        tds = row.find_all('td')
        if len(tds) < 4:
            continue

        i = int(tds[0].text.strip().replace('.', ''))

        urlparts[-1] = tds[1].find('a').get('href')
        src = '/'.join(urlparts)
        des = _sluggify(tds[3].text.replace('(подробнее)', '').strip())

        dl.append((src, '{}/navsource-{:04d} - {}.jpg'.format(dest, i, des)))

    print('Found {} images'.format(len(dl)))
    download_images(dl)
    return dl


def airbase_forum(url, dest, follow=True):
    """
    Scrape airbase.ru forum. URL starts from http://forums.airbase.ru
    :param url:
    :param dest:
    :return:
    """

    def _airbase_forum(url, dest, follow=True):
        # list of images to download
        dl = []

        r = requests.get(url=url)
        r.raise_for_status()
        # force encoding into utf-8 as sometimes airbase comes back in 'ISO-8859-1'
        r.encoding = 'utf-8'
        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        posts = soup.find_all('div', class_='post')
        print('Found {} posts on page {}'.format(len(posts), url))

        # going through posts
        for post in posts:
            # finding the post date (there is no post number on airbase)
            e = post.find('div', class_='to-left')
            # posts with non present to-left is advertisement
            if not e:
                continue

            postnr = e.find('a').text
            # post date is in form: "#12.07.2009 12:33" - normalize to allow good sorting order
            dt = datetime.datetime.strptime(postnr.strip().replace('#', ''), '%d.%m.%Y %H:%M')
            # dt = dateutil.parser.parse(postnr.strip().replace('#', ''))
            postnr = dt.strftime('airbase%Y-%m-%d-%H%M')
            # print(postnr)

            # 1st supported image format, when image is directly attached to the post
            attachments = post.find_all('div', class_='attach-desc')
            for i, attachment in enumerate(attachments, 1):
                # print('Attachment #{}'.format(i))
                # there are two links in each attachment - first gives the image second description
                a = attachment.find('a')
                src = _n(a.get('href'))
                # description looks like rubbish for russian text - encoding issues ....
                des = _sluggify(a.get('title'))
                fn = '{}/{}-a{:02d}-{}'.format(dest, postnr, i, des)
                dl.append((src, fn))

            # 2nd class are the images uploaded to image sharing sites, like vfl.ru
            links = post.find_all('div', class_='rs_box_nd')
            for i, link in enumerate(links, 1):
                # within the link there shall be an image, otherwise this is just a normal link
                if link.find('img'):
                    # sometimes bloody airbase will miss the a as well
                    if link.find('a'):
                        src = link.find('a').get('href')
                        if src:
                            fn = '{}/{}-l{:02d}.jpg'.format(dest, postnr, i)
                            dl.append((src, fn))

            # 3rd class are the images uploaded to image sharing sites, like vfl.ru
            links = post.find_all('div', class_='rs_box')
            for i, link in enumerate(links, 1):
                # within the link there shall be an image, otherwise this is just a normal link
                if link.find('img'):
                    # sometimes bloody airbase will miss the a as well
                    if link.find('a'):
                        src = link.find('a').get('href')
                        if src:
                            fn = '{}/{}-l{:02d}.jpg'.format(dest, postnr, i)
                            dl.append((src, fn))

        print('Found {} potential image links'.format(len(dl)))

        if follow:
            print('Checking if next page is available ... ')
            next_page = soup.find('a', class_='current_page').find_next('a')
            if next_page:
                src = next_page.get('href')
                if src:
                    dl += _airbase_forum(_n(src), dest, follow)

        return dl

    dl = _airbase_forum(url=url, dest=dest, follow=follow)
    download_images(dl)
    return dl
