import socket
import json
import cPickle
import tempfile
import docker
import time
import re


MAX_TRY = 20


class FunPod(object):
    """ Functional pod that is called on-demand """
    def __init__(self, name, start_pod=True, **kwargs):
        self.name = name
        self.kwargs = kwargs
        self.docker_client = docker.from_env()
        self.container = None
        self._ip = '0.0.0.0'
        self._port = 9998
        self.connector = FunPodConnector(funpod=self)
        if start_pod:
            self.spinup()

    @property
    def port(self):
        return self._port

    @property
    def ip(self):
        return self._ip

    @port.setter
    def port(self, val):
        self._port = val

    @ip.setter
    def ip(self, val):
        self._ip = val

    def build(self, func):
        """TODO: build image given handle function """
        pass

    def find_siblings(self):
        list_sib = [c for c in self.docker_client.containers.list()
                    if c.attrs['Config']['Image'] == self.name]
        if self.container:
            list_sib = [c for c in list_sib if c.id != self.container.id]
        return list_sib

    def spinup(self):
        n = 0
        success = False
        while True:
            try:
                self.container = self.docker_client.containers.run(
                    self.name,
                    environment={'PYTHONUNBUFFERED': 1},
                    detach=True,
                    ports={str(self._port): str(self.connector.port)},
                    **self.kwargs
                )
                success = True
                print 'connected to pod {} at port {}'.format(
                    self.name, self.connector.port)
                break
            except docker.errors.APIError:
                # try a different port
                self.connector.port -= 1
                n += 1
                if n > MAX_TRY:
                    break
        if not success:
            raise Exception('Spinning up funpod {} not successful'.
                            format(self.name))
        print 'Funpod {} is spun up, port: {}'.format(
            self.name, self.connector.port)

        running = False
        t0 = time.time()
        while not running:
            #  procs = self.container.top()['Processes']
            #  running = map(lambda x: re.search('funpod', x[-1]), procs)[-1]
            running = re.search('listening...', self.container.logs())
            time.sleep(0.1)
        print 'Handle function running, time elapsed', time.time() - t0
        time.sleep(0.2)
        return self.connector.port

    def handle(self, func):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self._ip, self._port))
        self.sock.listen(1)
        print('listening...')

        conn, addr = self.sock.accept()
        print('handle request received')
        buf = self.connector.recv(conn=conn)

        kwargs = json.loads(buf)
        gen = func(**kwargs)
        for i in gen:
            try:
                conn, addr = self.sock.accept()
                conn.send(str(i))
                conn.shutdown(socket.SHUT_WR)
            finally:
                conn.close()

        try:
            conn, addr = self.sock.accept()
            conn.send('EOF')
            conn.shutdown(socket.SHUT_WR)
        finally:
            conn.close()

    def handle_file(self, func):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self._ip, self._port))
        self.sock.listen(1)

        conn, addr = self.sock.accept()
        print('handle request received')
        f = self.connector.recv_file(conn=conn)

        gen = func(f)
        for i in gen:
            try:
                conn, addr = self.sock.accept()
                conn.send(str(i))
                conn.shutdown(socket.SHUT_WR)
            finally:
                conn.close()

        try:
            conn, addr = self.sock.accept()
            conn.send('EOF')
            conn.shutdown(socket.SHUT_WR)
        finally:
            conn.close()

    def kill(self, c=None):
        if not c:
            c = self.container
        if c:
            try:
                print 'killing', c.name, '... (current status:', c.status, ')'
                c.kill()
            except Exception as e:
                print e

    def kill_all(self, force=False):
        if not force:
            raise Exception('to execute kill_all, explicitly force by'
                            'passing arg: > kill_all(force=True)')
        self.kill(self.container)
        for c in self.find_siblings():
            self.kill(c)


class FunPodConnector(object):

    def __init__(self, name=None, funpod=None,
                 ip='0.0.0.0', port=9998):
        if name and funpod:
            raise Exception('Args name and funpod cannot coexist')
        elif not name and not funpod:
            raise Exception('Please pass arg name or funpod')
        self.funpod = funpod
        if funpod:
            self.name = funpod.name
        else:
            self.name = name
        self._ip = ip
        self._port = port

    @property
    def port(self):
        return self._port

    @property
    def ip(self):
        return self._ip

    @port.setter
    def port(self, val):
        self._port = val

    @ip.setter
    def ip(self, val):
        self._ip = val

    def send(self, data_send):
        n = 0
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self._ip, self._port))
                #  self.sock.sendall(json.dumps(data_send).encode('utf-8'))
                self.sock.sendall(data_send)
                self.sock.shutdown(socket.SHUT_WR)
                buf = ''
                data = True
                while data:
                    data = self.sock.recv(20480)
                    buf += data
                    #  return json.loads(unicode(buf, 'utf-8'))
            except Exception as e:
                n += 1
                if n > MAX_TRY:
                    raise Exception('Maxmum try reached')
                time.sleep(0.5)
                print 'caught', e, ', trying again...', n
            else:
                break
            finally:
                self.sock.close()

    def recv(self, conn=None):
        n = 0
        while True:
            try:
                if not conn:
                    self.sock = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.connect((self._ip, self._port))
                    #  self.sock.sendall(json.dumps(data_send).encode('utf-8'))
                    conn = self.sock

                buf = ''
                data = True
                while data:
                    data = conn.recv(20480)
                    buf += data
                return buf

            except Exception as e:
                n += 1
                if n > MAX_TRY:
                    raise Exception('Maxmum try reached')
                print 'caught', e, ', trying again...', n

            finally:
                conn.close()

    def recv_file(self, conn=None):
        try:
            if not conn:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self._ip, self._port))
                #  self.sock.sendall(json.dumps(data_send).encode('utf-8'))
                conn = self.sock

            f = tempfile.TemporaryFile()
            data = True
            while data:
                data = conn.recv(20480)
                f.write(data)
            f.seek(0)
            return f

        finally:
            conn.close()

    def start_or_restart_pod(self):
        if not self.funpod:
            self.funpod = FunPod(self.name)
        if self.funpod.container in self.funpod.docker_client.containers.list():
            print "Funpod is already up, try restarting ..."
            self.funpod.container.restart()
        else:
            self.funpod.spinup()
        time.sleep(0.25)
        print self.funpod.container.exec_run('echo "funpod ready"')

    def client_generator(self, serializer=None, start_pod=False,
                         fileobj=False, **kwargs):
        """
        client generator calls FunPod and return a generator
        Args:
        -----
        serializer: (opt.) serializer that has dumps/loads functions.
                    default cPickle
        fileobj: file object. buffer will be transferred to function args
        **kwargs: non-file type args to pass to function

        Returns:
        --------
        result: generator. a python generator which items can be retrieved by
                results.next() or all at once list(results)
        """
        if not serializer:
            serializer = cPickle

        if fileobj and kwargs:
            raise Exception('client generator does not accept both: '
                            'only either fileobj or kwargs')
            #  kwargs['fileobj'] = fileobj.read()
        try:
            if start_pod:
                self.start_or_restart_pod()
            #  else:
            #      time.sleep(0.5)
            if not fileobj:
                self.send(json.dumps(kwargs))
                print('kwargs {} sent'.format(kwargs))
            else:
                self.send(fileobj.read())
                print('fileobj sent')
            while True:
                recv = self.recv()
                if recv == 'EOF':
                    break
                yield serializer.loads(recv)
        except Exception as e:
            print e.__dict__
            print recv
            raise e
        finally:
            #  if start_pod:
            self.funpod.kill()


def main_test():
    def makelist(n):
        for i in xrange(int(n)):
            yield i

    pod = FunPod('test')
    pod.handle(makelist)


if __name__ == '__main__':
    main_test()
