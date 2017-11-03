"""
Set of tests
"""

import os
import pytest
import filecmp

import src.mfs.scrape as scrape
import mfs.cli as cli

REFDATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


def _refdata(fn):
    with open('./data/{}'.format(fn), encoding='utf8') as f:
        return f.read()


def test_resolve_postimg():
    url = scrape._resolve_postimg(_refdata('postimage.org.html'))
    assert url == 'https://s30.postimg.org/h38irt6r5/f618c175869a.jpg', \
        'Resolved postimg.org image link does not match'


def test_postimg(tmpdir):
    fn = tmpdir.strpath + '/aaa.jpg'
    scrape.download_images([('http://www.postimg.org/image/n467ovtd9/', fn)])
    assert len(os.listdir(tmpdir.strpath)) == 1, 'One images shall be downloaded'
    assert filecmp.cmp('./data/postimg.org.jpg', fn, shallow=False), 'Downloaded image does not match the reference one'


def test_resolve_vfl():
    url = scrape._resolve_vfl(_refdata('vfl.ru.html'))
    assert url == 'http://images.vfl.ru/ii/1504336251/b2203fcd/18453338.jpg', \
        'Resolved vfl.ru image link does not match'


def test_vfl(tmpdir):
    fn = tmpdir.strpath + '/aaa.jpg'
    scrape.download_images([('http://vfl.ru/fotos/b2203fcd18453338.html', fn)])
    assert len(os.listdir(tmpdir.strpath)) == 1, 'One images shall be downloaded'
    assert filecmp.cmp('./data/vfl.ru.jpg', fn, shallow=False), 'Downloaded image does not match the reference one'


def test_resolve_radikal():
    url = scrape._resolve_radikal(_refdata('radikal.ru.html'))
    assert url == 'http://s39.radikal.ru/i084/1106/a9/e1fca250702b.jpg', \
        'Resolved radikal.ru image link does not match'


def test_radikal(tmpdir):
    fn = tmpdir.strpath + '/aaa.jpg'
    scrape.download_images([('http://radikal.ru/F/s39.radikal.ru/i084/1106/a9/e1fca250702b.jpg.html', fn)])
    assert len(os.listdir(tmpdir.strpath)) == 1, 'One images shall be downloaded'
    assert filecmp.cmp('./data/radikal.ru.jpg', fn, shallow=False), 'Downloaded image does not match the reference one'


def test_radikal_direct_link(tmpdir):
    fn = tmpdir.strpath + '/aaa.jpg'
    scrape.download_images([('http://s39.radikal.ru/i084/1106/a9/e1fca250702b.jpg', fn)])
    assert len(os.listdir(tmpdir.strpath)) == 1, 'One images shall be downloaded'
    assert filecmp.cmp('./data/radikal.ru.jpg', fn, shallow=False), 'Downloaded image does not match the reference one'


def test_radikal_dead_link(tmpdir):
    fn = tmpdir.strpath + '/aaa.jpg'
    scrape.download_images([('http://radikal.ru/F/i038.radikal.ru/1102/a4/823b89d487dd.jpg.html', fn)])
    assert len(os.listdir(tmpdir.strpath)) == 0, 'No images shall be downloaded'


def test_resolve_keep4u():
    url = scrape._resolve_keep4u(_refdata('keep4u.ru.html'))
    assert url == 'http://static2.keep4u.ru/2011/05/13/486422e15f82de157a64237a9627892e.jpg', \
        'Resolved radikal.ru image link does not match'


def test_keep4u(tmpdir):
    fn = tmpdir.strpath + '/aaa.jpg'
    scrape.download_images([('http://keep4u.ru/full/486422e15f82de157a64237a9627892e.html', fn)])
    assert len(os.listdir(tmpdir.strpath)) == 1, 'One images shall be downloaded'
    assert filecmp.cmp('./data/keep4u.ru.jpg', fn, shallow=False), 'Downloaded image does not match the reference one'


def test_resolve_fastpic():
    url = scrape._resolve_fastpic(_refdata('fastpic.ru.html'))
    assert url == 'http://i17.fastpic.ru/big/2011/0305/83/8677004de70d4ac9f4d4fe84f8f34983.jpg', \
        'Resolved fastpic.ru image link does not match'


def test_fastpic(tmpdir):
    fn = tmpdir.strpath + '/aaa.jpg'
    scrape.download_images([('http://fastpic.ru/view/17/2011/0305/8677004de70d4ac9f4d4fe84f8f34983.jpg.html', fn)])
    assert len(os.listdir(tmpdir.strpath)) == 1, 'One images shall be downloaded'
    assert filecmp.cmp('./data/fastpic.ru.jpg', fn, shallow=False), 'Downloaded image does not match the reference one'


@pytest.fixture
def mock_image_download(monkeypatch):
    # mock image download part and return immediately the number of files requested to download
    def mocked_return(dl):
        return len(dl)

    monkeypatch.setattr(scrape, 'download_images', mocked_return)


def test_karopka_model_overview(mock_image_download, tmpdir):
    dl = scrape.karopka_model_overview('http://karopka.ru/community/user/22051/?MODEL=464829', tmpdir)
    assert len(dl) == 10, 'Wrong number of files'


def test_karopka_forum_only_attachemnts(mock_image_download, tmpdir):
    # monkeypatch.setattr('mfs.scrape.download_images', image_download_mock)
    dl = scrape.karopka_forum('http://karopka.ru/forum/messages/forum232/topic8294/message199483/#message199483',
                              tmpdir)
    assert len(dl) == 13, 'Wrong number of links'


def test_karopka_forum_with_external_links(mock_image_download, tmpdir):
    dl = scrape.karopka_forum('http://karopka.ru/forum/forum263/topic15798/?PAGEN_1=30', tmpdir, follow=False)
    assert len(dl) == 13, 'Wrong number of links'

    dl = scrape.karopka_forum('http://karopka.ru/forum/forum263/topic15798/?PAGEN_1=29', tmpdir, follow=True)
    assert len(dl) >= 35, 'Wrong number of links'


def test_navsource(tmpdir, mock_image_download):
    dl = scrape.navsource('http://www.navsource.narod.ru/photos/02/020/index.html', tmpdir)
    assert len(dl) == 56, 'Wrong number of links'


def test_airbase(mock_image_download, tmpdir):
    dl = scrape.airbase_forum('http://forums.airbase.ru/2014/09/t67904--krejser-varyag-vremen-ryav.html', tmpdir,
                              follow=False)
    assert len(dl) == 23, 'Wrong number of links'

    # another one for 3rd class of links
    dl = scrape.airbase_forum('http://forums.airbase.ru/2009/07/t67904_3--krejser-varyag-vremen-ryav.html', tmpdir,
                              follow=False)
    assert len(dl) == 6, 'Wrong number of links'

    dl = scrape.airbase_forum('http://forums.airbase.ru/2014/09/t67904--krejser-varyag-vremen-ryav.html', tmpdir,
                              follow=True)
    assert len(dl) >= 253, 'Wrong number of links'


def test_download_images(tmpdir):
    nfiles = 20
    dl = [('http://httpbin.org/image/jpeg', '{}/{:02d}.jpg'.format(tmpdir, i)) for i in range(nfiles)]
    scrape.download_images(dl)
    assert len(os.listdir(tmpdir.strpath)) == nfiles, 'Wrong number of files'


def test_download_images_bad_links(tmpdir):
    # no site
    dl = [(
          'http://www.suveniri-knigi.ru/index.php?nach=1&kol=1&book2=CHertezi_korabley_CHertez_kreysera_I_ranga_Varyag_masshta&book22=&kcena=220&kkorzina=3521',
          '{}/aaa.jpg'.format(tmpdir))]
    scrape.download_images(dl)
    assert len(os.listdir(tmpdir.strpath)) == 0, 'No files shall be downloaded and no exception'



