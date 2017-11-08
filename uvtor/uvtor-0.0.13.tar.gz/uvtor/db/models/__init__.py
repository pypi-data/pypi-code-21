from uvtor.conf import settings
from playhouse import postgres_ext
from playhouse import pool
import peewee_async
import datetime


database = peewee_async.PooledPostgresqlDatabase(
    settings.DB_DATABASE, user=settings.DB_USER,
    host=settings.DB_HOST,
    password=settings.DB_PASSWORD,
    min_connections=settings.DB_CONN_POOL_MIN_SIZE,
    max_connections=settings.DB_CONN_POOL_MAX_SIZE)

pg_db = pool.PooledPostgresqlExtDatabase(
    settings.DB_DATABASE, user=settings.DB_USER,
    host=settings.DB_HOST,
    password=settings.DB_PASSWORD,
    min_connections=settings.DB_CONN_POOL_MIN_SIZE,
    max_connections=settings.DB_CONN_POOL_MAX_SIZE
    )

manager = peewee_async.Manager(database)


class BaseModel(postgres_ext.Model):

    created = postgres_ext.DateTimeTZField(
        verbose_name='添加时间',
        default=datetime.datetime.now,
        null=False)
    modified = postgres_ext.DateTimeTZField(
        verbose_name='更新时间',
        default=datetime.datetime.now,
        null=False)

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        database = database
