import queue
import threading


class Thread(threading.Thread):
    data = None
    function = None
    processed = None

    def __init__(self, data, function):
        super(Thread, self).__init__()

        self.data = data
        self.function = function

    def run(self):
        self.processed = self.function(self.data)

    def get(self):
        return self.processed


def queue_worker(q, process, processed_data):
    while True:
        task = q.get()
        if task is None:
            break
        processed_data.append(process(task))
        q.task_done()


def async_process(data, function, workers=None, background=False):
    threads = []
    processed_data = []

    if workers is None:
        for item in data:
            t = Thread(item, function)
            threads.append(t)
            t.start()
        if not background:
            for t in threads:
                t.join()
                processed_data.append(t.get())
    else:
        q = queue.Queue()

        for i in range(workers):
            t = threading.Thread(target=queue_worker, args=(q, function, processed_data))
            t.start()
            threads.append(t)

        for item in data:
            q.put(item)

        for t in range(workers):
            q.put(None)

        for t in threads:
            t.join()
    return processed_data
