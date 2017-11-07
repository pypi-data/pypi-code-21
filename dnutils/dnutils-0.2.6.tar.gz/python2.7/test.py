# -*- coding: utf-8 -*-

import time
import traceback
from multiprocessing.pool import Pool

import colored
import numpy as np

from dnutils import out, stop, trace, getlogger, ProgressBar, StatusMsg, bf, loggers, newlogger, logs, edict, ifnone, \
    ifnot, allnone, allnot, first, sleep, waitabout, __version__ as version

import unittest

from dnutils.logs import expose, inspect, exposure
from dnutils.stats import Gaussian, stopwatch, print_stopwatches, get_stopwatch
from dnutils.tools import LinearScale

loggers({
    'default': newlogger(logs.console),
    'results': newlogger(logs.console, logs.FileHandler('dnutils-test.log'))
})


def wait():
    time.sleep(1)

bfctnames = {
    'out': colored.stylize('out()', colored.attr('bold')),
    'stop': colored.stylize('stop()', colored.attr('bold')),
    'trace': colored.stylize('trace()', colored.attr('bold'))
}


class EDictTest(unittest.TestCase):

    def test_xpath(self):
        d = edict({'a': [{'b': {'c': 'hello'}}, {'b': {'c': 'world'}}]}, recursive=1)
        msg = 'xpath query with indexing'
        self.assertEqual(d.xpath('a/[0]/b/c'), 'hello', msg)
        self.assertEqual(d.xpath('a/[1]/b/c'), 'world', msg)
        self.assertTrue(type(d.xpath('a')) is list, msg)
        self.assertTrue(type(d.xpath('a/[0]')) is edict)
        d = edict()
        d.set_xpath('a/b/c', 'hello, world!', force=True)
        assert d.xpath('a/b/d') is None
        assert d.xpath('a/b/c') == 'hello, world!'

    def test_default(self):
        d = edict(default=list)
        d['a'].append('first item')
        self.assertEqual(d['a'][0], 'first item')
        self.assertTrue(d.xpath('a/[1]') is None)

    def test_getset(self):
        d = edict()
        d['a'] = 1
        d['b'] = 2
        with self.assertRaises(KeyError):
            d['c']
        self.assertIsNone(d.get('c'))
        self.assertEqual(d.get('c', 3), 3)
        self.assertDictEqual(d, {'a': 1, 'b': 2})

    def test_projection(self):
        d = edict({'one': 1, 'two': 2})
        d_ = edict(d)
        self.assertDictEqual(d.project('one'), {'one': 1})
        self.assertDictEqual(d, d_)


class ConditionalTest(unittest.TestCase):

    def test_ifnone(self):
        self.assertEqual(ifnone(None, 'hello'), 'hello')
        self.assertEqual(ifnone('hello', None), 'hello')
        self.assertEqual(ifnone(None, 1, transform=str), 1)
        self.assertEqual(ifnone(1, 1, transform=str), '1')
        self.assertEqual(ifnone(0, 1, transform=str), '0')

    def test_ifnot(self):
        self.assertEqual(ifnot(None, 'hello'), 'hello')
        self.assertEqual(ifnot('hello', None), 'hello')
        self.assertEqual(ifnot('', None), None)
        self.assertEqual(ifnot(None, 1, transform=str), 1)
        self.assertEqual(ifnot(1, 1, transform=str), '1')
        self.assertEqual(ifnot(0, 1, transform=str), 1)

    def test_allnone(self):
        self.assertTrue(allnone([None, None, None]))
        self.assertFalse(allnone([0, 0, 0]))
        self.assertFalse(allnone([None, None, 1]))
        self.assertFalse(allnone([None, None, 0]))

    def test_allnot(self):
        self.assertTrue(allnot([None, None, None]))
        self.assertTrue(allnot([0, 0, 0]))
        self.assertFalse(allnot([None, None, 1]))
        self.assertTrue(allnot([None, None, 0]))


class GaussianTest(unittest.TestCase):

    def test_multivariate(self):
        mean = [5., 4.]
        cov = [[1., -0.3], [-0.3, 1.]]
        data = np.random.multivariate_normal(np.array(mean), np.array(cov), size=50000)
        gauss = Gaussian()
        for d in data:
            gauss.update(d)
        for e1, e2 in zip(gauss.mean, mean):
            self.assertAlmostEqual(e1, e2, 1, 'means differ too much:\n%s\n!=\n%s' % (mean, gauss.mean))
        for e1, e2 in zip(np.nditer(np.array(gauss.cov)), np.nditer(np.array(cov))):
            self.assertAlmostEqual(round(e1, 1), e2, 1, 'covariances differ too much: %s != %s' % (cov, gauss.cov))

    def test_univariate(self):
        mu, sigma = 0.5, 0.1
        data = np.random.normal(mu, sigma, 1000)
        g = Gaussian(data=data)
        self.assertAlmostEqual(mu, float(g.mean), 1)
        self.assertAlmostEqual(sigma, np.sqrt(float(g.cov)), 1)


class StopWatchTest(unittest.TestCase):

    def test_watch(self):
        mean = .2
        std = .05
        times = np.random.normal(mean, std, 100)
        for t in times:
            with stopwatch('/test'):
                sleep(t)
        print_stopwatches()
        w = get_stopwatch('/test')
        self.assertAlmostEqual(w.avg, mean, 1, 'means differ too much:\n%s\n!=\n%s' % (w.avg, mean))
        self.assertAlmostEqual(w.std, std, 1, 'stddevs differ too much:\n%s\n!=\n%s' % (w.std, std))


class IteratorTest(unittest.TestCase):

    def test_first(self):
        self.assertEqual(first([0, 1, 2]), 0)
        self.assertEqual(first(None), None)
        self.assertEqual(first([]), None)

        def gen():
            for i in range(3):
                yield i
        self.assertEqual(first(gen()), 0)
        self.assertEqual(first(gen(), str, 'no elements'), '0')
        self.assertEqual(first([], str, 'no elements'), 'no elements')


class ScaleTest(unittest.TestCase):

    def test_linearscale(self):
        scale = LinearScale([0, 100], [0, 1])
        self.assertEqual(scale(50), .5)
        with self.assertRaises(ValueError):
            scale(-50)
            scale(150)
        scale.strict = False
        self.assertEqual(scale(-50), -.5)
        self.assertEqual(scale(150), 1.5)


def exposure_proc(*_):
    for _ in range(10):
        # use the exposure as a file lock
        try:
            with exposure('/vars/myexposure'):
                n = inspect(expose('/vars/myexposure'))
                waitabout(.1)
                expose('/vars/myexposure', n + 1)
                waitabout(.1)
                assert n + 1 == inspect(expose('/vars/myexposure'))
        except:
            traceback.print_exc()


class ExposureTest(unittest.TestCase):

    def test_expose_inspect(self):
        expose('/vars/myexposure', 'a', 'b', 'c')
        self.assertEqual(inspect('/vars/myexposure'), ['a', 'b', 'c'])
        expose('/vars/myexposure2', 2)
        self.assertEqual(inspect('/vars/myexposure2'), 2)
        self.assertIsNone(inspect('/var/myexposure'))
        expose('/vars/myexposure', 0)
        pool = Pool(4)
        pool.map(exposure_proc, [[] for _ in range(4)])
        pool.close()
        pool.join()


if __name__ == '__main__':
    unittest.main()

    logger = getlogger('results', logs.DEBUG)
    logger.info('Initialized. Running all tests...')
    wait()
    logger.info('Testing log levels...')
    logger.debug('this is the debug level')
    logger.info('this is the info level')
    logger.warning('this is the warning level')
    logger.error('this is the error level')
    logger.critical('this is the critical level')

    logger.critical('wait a second...')
    wait()
    logger.debug('This debug message spreads over\nmultiple lines and should be\naligned with appropriate indentation.')
    wait()

    logger.level = logs.ERROR
    logger.info('If you see this message, something went wrong with the log levels.')
    logger.level = logs.DEBUG

    logger.info('Testing the debug functions.')
    wait()
    out('the %s function always prints the code location where it is called so it can be found again later swiftly.' %
        bfctnames['out'])
    wait()
    out('it', 'also', 'accepts', 'multiple', 'arguments', 'which', 'are', 'being', 'concatenated')
    stop('the %s function is equivalent to %s except for it stops until you hit return:' % (bfctnames['stop'],
                                                                                            bfctnames['out']))

    trace('the %s function gives you a stack trace of the current position' % bfctnames['trace'])

    logger.info('testing the', bf('ProgressBar'), 'and', bf('StatusMsg'), '...')
    bar = ProgressBar(steps=10, color='deep_sky_blue_4c')
    for i in range(11):
        bar.update(value=i/10., label='step %d' % (i+1))
        time.sleep(.5)
    bar.finish()

    logger.info('testing the', bf(StatusMsg), '(you should see 5 "OK" and 5 "ERROR" messages)')
    wait()
    for i in range(20):
        bar = StatusMsg('this is a Linux-style status bar (%.2d)...' % (i+1))
        bar.status = StatusMsg.OK
        wait()
        bar.finish()
