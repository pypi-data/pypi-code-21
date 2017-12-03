import cProfile
import pstats
import StringIO
from random_words import RandomWords

from iceman.configuration import Configuration
from iceman.interceptor import Interceptor

def profile():
    strategies = Configuration().CRYPTO_STRATEGIES
    words = RandomWords().random_words(count=5449)

    for strategy in strategies:
        print strategy
        pr = cProfile.Profile()
        pr.enable()
        config = Configuration()
        config.cipher_suite = config.initialize_cipher_suite(strategy)

        for word in words:
            enc = config.cipher_suite.encrypt(str(word))
            config.cipher_suite.decrypt(enc)

        pr.disable()
        s = StringIO.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print
        print strategy
        print
        print s.getvalue()

if __name__ == '__main__':
    profile()
