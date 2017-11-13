#!/usr/bin/env python3

import time
from zmq_plumbing import ZmQueue as Q


if __name__ == "__main__" :

    print("Master")
    print("Starting the queues")
    q = Q("tcp://localhost:5557", "tcp://localhost:5557")

    start = time.time()
    for i in range(0,10000):
        q.put(b'Hello')
        x = q.get()
        print(x)

    end = time.time()
    print("Total time : ", end-start)

