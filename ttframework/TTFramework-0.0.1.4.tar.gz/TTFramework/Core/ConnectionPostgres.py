import sqlalchemy as sqla
import sqlalchemy.orm as sqlorm
from sqlalchemy.ext.declarative import declarative_base as sqla_declarative_base


class PostgresConnection(object):
    session = None
    base = None
    connection = None
    def __init__(self,userName=None,passwd=None,serverIp=None,port=None,dbname=None,isEcho=False,poolCount=20):
        self.base = sqla_declarative_base()

        #engine = sqla.create_engine ('postgresql://postgres:postgres@10.200.163.233:5432/myTest', echo=True,pool_size=10)
        # if userName:
        engineStr = ('postgresql://' + userName + ':' + passwd + '@' + serverIp + ':' + str(port) + '/' + dbname)
        self.engine = sqla.create_engine(engineStr, echo=isEcho, pool_size=poolCount)
        # else:
        #     engineStr = ('postgresql://' +
        #                                   configer.Database['username'] +
        #                                   ':' +
        #                                   configer.Database['password'] +
        #                                   '@' +
        #                                   configer.Database['serverip'] +
        #                                   ':' +
        #                                   configer.Database['port'] +
        #                                   '/' +
        #                                   configer.Database['dbname'])
        #     self.engine = sqla.create_engine(engineStr,
        #                                  echo=str(configer.Database['isecho']).lower() == 'true',
        #                                  pool_size=int(configer.Database['poolcount']))
        self.base.metadata.bind = self.engine
        self.session = sqlorm.scoped_session(sqlorm.sessionmaker(bind=self.engine))

