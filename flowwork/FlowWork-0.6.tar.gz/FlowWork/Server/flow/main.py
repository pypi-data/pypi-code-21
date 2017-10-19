
#!/usr/bin/python
## write by qingluan 
# just a run file 

import tornado.ioloop
from tornado.ioloop import IOLoop
from setting import  appication, port
from qlib.io import GeneratorApi


def main():
    args = GeneratorApi({
        'port':"set port ",
        })
    if args.port:
        port = int(args.port)
    appication.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
    