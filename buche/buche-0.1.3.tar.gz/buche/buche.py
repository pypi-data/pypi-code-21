
import asyncio
import json
import re
from threading import Thread
from .event import EventDispatcher
from .repr import id_registry


class BucheMessage:
    def __init__(self, d):
        self.__dict__.update(d)

    def __hrepr__(self, H, hrepr):
        return hrepr.stdrepr_object('BucheMessage', self.__dict__.items())


class BucheSeq:
    def __init__(self, objects):
        self.objects = list(objects)

    @classmethod
    def __hrepr_resources__(cls, H):
        return H.style('''
        .multi-print { display: flex; align-items: center; }
        .multi-print > * { margin-right: 10px; }
        ''')

    def __hrepr__(self, H, hrepr):
        return H.div['multi-print'](*map(hrepr, self.objects))


class BucheDict:
    def __init__(self, keys):
        if hasattr(keys, 'items'):
            self.keys = keys.items()
        else:
            self.keys = keys

    def __hrepr__(self, H, hrepr):
        return hrepr.stdrepr_object(None, self.keys)


class MasterBuche:
    def __init__(self, hrepr, write):
        self.hrepr = hrepr
        self.write = write
        self.resources = set()

    def require(self, *plugins):
        for p in plugins:
            if '/' in p or '.' in p:
                self.send(command='require', path='/', pluginPath=p)
            else:
                self.send(command='require', path='/', pluginName=p)

    def send(self, d={}, **params):
        message = {**d, **params}
        if 'path' not in message:
            raise ValueError(f'Must specify path for message: {message}')
        if 'command' not in message:
            raise ValueError(f'Must specify command for message: {message}')
        self.write(json.dumps(message))

    def show(self, obj, hrepr_params={}, **params):
        x = self.hrepr(obj, **hrepr_params)
        for res in self.hrepr.resources - self.resources:
            self.send(
                command = 'resource',
                path = '/',
                type = 'direct',
                contents = str(res)
            )
            self.resources.add(res)
        params.setdefault('command', 'log')
        self.send(format='html',
                  contents=str(x),
                  **params)


class Buche:
    def __init__(self, master, path, type=None, params=None, opened=False):
        self.master = master
        self.path = path
        self.type = type
        self.params = params or {}
        self.opened = opened
        self.subchannels = {}

    def _open(self):
        if self.type is not None:
            self.master.send(command='open', path=self.path,
                             type=self.type, **self.params)
        self.opened = True

    def configure(self, type=None, **params):
        if self.opened:
            raise Exception('Cannot configure a buche channel after it has'
                            'been opened.')
        if type:
            self.type = type
        self.params.update(params)
        return self

    def require(self, *plugins):
        self.master.require(*plugins)

    def send(self, path=None, **params):
        if not self.opened:
            self._open()
        if path is None:
            path = self.path
        elif path.startswith('/'):
            pass
        else:
            path = self.join_path(path)
        self.master.send(path=path, **params)

    def log(self, contents, format='text', **params):
        self.send(command='log', format=format,
                  contents=contents, **params)

    def pre(self, contents, **params):
        self.log(contents, format = 'pre', **params)

    def html(self, contents, **params):
        self.log(contents, format = 'html', **params)

    def markdown(self, contents, **params):
        self.log(contents, format = 'markdown', **params)

    def open(self, name, type, params, force=False):
        if name == '/' and self.path == '/':
            self.configure(type, params)
            if force:
                self._open()
            return self
        if not self.opened:
            self._open()
        if name.startswith('/'):
            if self.path == '/':
                name = name.lstrip('/')
            else:
                raise ValueError('Channel name for open() cannot start with /'
                                 ' unless called on the root channel.')
        parts = re.split('/+', name, 1)
        if len(parts) == 1:
            if name in self.subchannels:
                return self.subchannels[name]
            else:
                ch = Buche(self.master, self.join_path(name), type, params)
                if force:
                    ch._open()
                self.subchannels[name] = ch
                return ch
        else:
            name, rest = parts
            return self.open(name, 'tabs', {}).open(rest, type, params, force)

    def __getattr__(self, attr):
        if attr.startswith('log_'):
            command = attr[4:]
            def _log(contents=None, **params):
                self.send(command=command, contents=contents, **params)
            return _log
        elif attr.startswith('open_'):
            chtype = attr[5:]
            def _open(name, **params):
                return self.open(name, chtype, params)
            return _open
        elif attr.startswith('ch_'):
            chname = attr[3:]
            return self[chname]
        else:
            raise AttributeError(f"'Buche' object has no attribute '{attr}'")

    def join_path(self, p):
        return f'{self.path.rstrip("/")}/{p.strip("/")}'

    def __getitem__(self, item):
        descr = item.split('::')
        if len(descr) == 1:
            type = None
            name, = descr
        else:
            name, type = descr
        return self.open(name, type, {})

    def show(self, obj, hrepr_params={}, **params):
        if not self.opened:
            self._open()
        self.master.show(obj, hrepr_params=hrepr_params,
                         path=self.path, **params)

    def dict(self, **keys):
        self.show(BucheDict(keys))

    def __call__(self, *objs, **hrepr_params):
        if len(objs) == 1:
            o, = objs
        else:
            o = BucheSeq(objs)
        self.show(o, hrepr_params)


class Reader(EventDispatcher):
    def __init__(self, source):
        super().__init__()
        self.ev_loop = asyncio.get_event_loop()
        self.source = source
        self.thread = Thread(target=self.loop)
        self.futures = []

    def read(self):
        line = self.source.readline()
        return self.parse(line)

    def parse(self, line):
        d = json.loads(line)
        if 'objId' in d and 'obj' not in d:
            d['obj'] = id_registry.resolve(int(d['objId']))
        message = BucheMessage(d)
        self.emit(d.get('command', 'UNDEFINED'), message)
        # Provide the message to all the coroutines waiting for one
        futs, self.futures = self.futures, []
        for fut in futs:
            self.ev_loop.call_soon_threadsafe(fut.set_result, message)
        return message

    def __iter__(self):
        for line in self.source:
            yield self.parse(line)

    def loop(self):
        for _ in self:
            pass

    def start(self):
        self.thread.start()

    def read_async(self):
        fut = asyncio.Future()
        self.futures.append(fut)
        return fut
