#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys


def main():
    if '--total' in sys.argv:
        total = sys.argv[sys.argv.index('--total')+1]
    else:
        total = None

    if '--pb' in sys.argv and total is not None:
        from pyprogress import ThreadedProgressBar
        c = ThreadedProgressBar(int(total), timecount=True, completionprediction=True, colored=True)
    else:
        from pyprogress import Counter
        c = Counter(total=total)
    c.start()

    while True:
        try:
            line = sys.stdin.readline()
            if len(line) > 0:
                c.inc()
            else:
                break
        except KeyboardInterrupt:
            break

    if '--pb' in sys.argv and total is not None:
        c.finish()
    else:
        c.stop()
    c.join()

    sys.stdout.write("\n")
    sys.stdout.flush()

if __name__ == '__main__':
    main()
