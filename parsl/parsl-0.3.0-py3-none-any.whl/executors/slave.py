#!/usr/bin/env python3

import time
from zmq_plumbing import ZmQueue as Q


if __name__ == "__main__" :

    print("Slave")
    print("Listening on 5558")
    print("Sending results on 5557")

    q = Q("tcp://localhost:5558", "tcp://localhost:5557")

    start = time.time()
    for i in range(0,10000):
        data = q.get()
        x = q.put(data + '11111')
        print(x)

    end = time.time()
    print("Total time : ", end-start)

