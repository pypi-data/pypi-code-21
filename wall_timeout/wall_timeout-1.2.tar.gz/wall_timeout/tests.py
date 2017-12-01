import time

from wall_timeout import timeout, TIMEOUT_EXCEPTION


@timeout(2.5)
def test():
    time.sleep(seconds)
    return 'Function completed after ' + str(seconds) + ' seconds.'


if __name__ == '__main__':
    for seconds in range(1, 5):
        try:
            print('*' * 40)
            print(test())
        except TIMEOUT_EXCEPTION as e:
            print(e)
