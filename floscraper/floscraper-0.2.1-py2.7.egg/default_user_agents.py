# -*- coding: UTF-8 -*-
"""
Module of default web browser user agents
"""

__author__ = "the01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2015-17, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.1"
__date__ = "2017-10-06"
# Created: 2014-09-21 04:29

# preconfigured user agents
default_user_agents = {
    'browser': {
        'keith': "Mozilla/5.0 (compatible; KeithScraper/0.1)",
        'firefox_v28': "Mozilla/5.0 ({}; rv:28.0) Gecko/20100101 Firefox/28.0",
        'firefox_v36': "Mozilla/5.0 ({}; rv:36.0) Gecko/20100101 Firefox/36.0",
        'firefox_v38': "Mozilla/5.0 ({}; rv:38.0) Gecko/20100101 Firefox/38.0",
        'firefox_v43': "Mozilla/5.0 ({}; rv:43.0) Gecko/20100101 Firefox/43.0",

        'chrome_v33':
            "Mozilla/5.0 ({}) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/33.0.1750.152 Safari/537.36",
        'chrome_v41':
            "Mozilla/5.0 ({}) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/41.0.2228.0 Safari/537.36",
        'chrome_v47':
            "Mozilla/5.0 ({}) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/47.0.2526.0 Safari/537.36",

        'safari_v7_0_2':
            "Mozilla/5.0 ({}) AppleWebKit/537.74.9 "
            "(KHTML, like Gecko) Version/7.0.2 Safari/537.74.9",
        'safari_v7_0_3':
            "Mozilla/5.0 ({}) AppleWebKit/537.75.14 (KHTML, like Gecko) "
            "Version/7.0.3 Safari/7046A194A",

        'opera_v20':
            "Mozilla/5.0 ({}) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/33.0.1750.154 Safari/537.36 OPR/20.0.1387.82",

        'googlebot_v2_1':
            "Mozilla/5.0 (compatible; Googlebot/2.1; "
            "+http://www.google.com/bot.html)",
        'archive.org_bot':
            "Mozilla/5.0 (compatible; archive.org_bot "
            "+http://www.archive.org/details/archive.org_bot)"
    },
    'os': {
        'linux_x86_64': "X11; Linux x86_64",
        'linux_i686': "X11; U; Linux; i686; en-US",

        'win_10': "Windows NT 10.0",
        'win_8_b64': "Windows NT 6.2; Win64; x64",
        'win_8': "Windows NT 6.2",
        'win_7': "Windows NT 6.1",
        'win_vista': "Windows NT 6.0",
        'win_xp': "Windows NT 5.1",

        'osx_10_11': "Macintosh; Intel Mac OS X 10_11",
        'osx_10_10': "Macintosh; Intel Mac OS X 10_10",
        'osx_10_9_3': "Macintosh; Intel Mac OS X 10_9_3",
        'osx_10_9': "Macintosh; Intel Mac OS X 10_9",
        'osx_10_8_2': "Macintosh; Intel Mac OS X 10_8_2",
        'osx_10_8': "Macintosh; Intel Mac OS X 10_8",

        'ipad_9_0': "iPad; CPU OS 9_0 like Mac OS X",
        'ipad_8_0': "iPad; CPU OS 8_0 like Mac OS X",
        'ipad_7_0_2': "iPad; CPU OS 7_0_2 like Mac OS X",
        'ipad_7_0': "iPad; CPU OS 7_0 like Mac OS X",
        'iphone_9_0': "iPhone; CPU iPhone OS 9_0 like Mac OS X",
        'iphone_8_0': "iPhone; CPU iPhone OS 8_0 like Mac OS X",
        'iphone_7_0': "iPhone; CPU iPhone OS 7_0 like Mac OS X"
    }
}
