#! /usr/bin/python

import sys
from pyprogress import *

if __name__ == '__main__':
    import random
    import signal

    def sigint_handler(signal, frame):
        try:
            tpb
        except NameError:
            pass
        else:
            tpb.finish()
            tpb.join()
            del tpb
        try:
            tdpb
        except NameError:
            pass
        else:
            tdpb.finish()
            tdpb.join()
            del tdpb
        try:
            s
        except NameError:
            pass
        else:
            s.stop()
            s.join()
            del s
        try:
            c
        except NameError:
            pass
        else:
            c.stop()
            c.join()
            del c
        sys.exit()
    signal.signal(signal.SIGINT, sigint_handler)

    # SINGLE PROGRESS BAR
    if len(sys.argv) == 1 or '--pb' in sys.argv:
        firstsize = 10
        pb = ProgressBar(firstsize, name="ProgressBar", timecount=False, completionprediction=True, colored=True)
        pb.begin()

        for x in range(firstsize):
            pb.inc()
            time.sleep(random.random()*2)
        pb.end()

    # DOUBLE PROGRESS BAR
    if len(sys.argv) == 1 or '--dpb' in sys.argv:
        firstsize = 10
        secondsize = random.randint(5, 15)
        pb = DoubleProgressBar(firstsize, secondsize, name="DoubleProgressBar", totalcount=True, timecount=True, completionprediction=True, colored=True)
        pb.begin()

        for x in range(firstsize):
            pb.inc()
            pb.reset2()
            pb.total2(secondsize)
            for y in range(secondsize):
                pb.inc2()
                time.sleep(random.random())
            secondsize = random.randint(5, 15)
        pb.end()

    # THREADED PROGRESS BAR
    if len(sys.argv) == 1 or '--tpb' in sys.argv:
        firstsize = 10
        tpb = ThreadedProgressBar(firstsize, name="ThreadedProgressBar", timecount=True, completionprediction=True, colored=True)
        tpb.start()

        for x in range(firstsize):
            tpb.inc()
            time.sleep(random.random()*2)

        tpb.finish()
        tpb.join()
        del tpb

    # THREADED DOUBLE PROGRESS BAR
    if len(sys.argv) == 1 or '--tdpb' in sys.argv:
        firstsize = 5
        secondsize = random.randint(3, 5)
        tdpb = ThreadedDoubleProgressBar(firstsize, secondsize, name="ThreadedDoubleProgressBar", totalcount=True, timecount=True, completionprediction=True, colored=True)
        tdpb.start()

        for x in range(firstsize):
            tdpb.inc()
            tdpb.reset2()
            tdpb.total2(secondsize)
            for y in range(secondsize):
                tdpb.inc2()
                time.sleep(random.random())
            secondsize = random.randint(3, 5)
        tdpb.finish()
        tdpb.join()
        del tdpb

    # SPINNER
    if len(sys.argv) == 1 or '--sp' in sys.argv:
        sys.stdout.write("\nSpinner ")

        s = Spinner()
        s.start()
        time.sleep(5)
        s.stop()
        s.join()

    # SPINNER IN CONTEXT
    if len(sys.argv) == 1 or '--sp' in sys.argv:
        sys.stdout.write("\nContext Spinner ")

        with Spinner():
            time.sleep(5)

    # COUNTER
    if len(sys.argv) == 1 or '--cnt' in sys.argv:
        sys.stdout.write("\nCounter ")

        c = Counter(total=20)
        c.start()
        for x in range(20):
            c.inc()
            time.sleep(random.random())
        c.stop()
        c.join()

    # COUNTER IN CONTEXT
    if len(sys.argv) == 1 or '--cnt' in sys.argv:
        sys.stdout.write("\nContext Counter ")

        with Counter(total=20) as c:
            for x in range(20):
                c.inc()
                time.sleep(random.random())
