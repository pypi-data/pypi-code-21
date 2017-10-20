import datetime
import dateutil.parser


def init_db(conn):
    with conn:
        conn.executescript('''
          create table metric (
            id integer primary key autoincrement,
            name varchar(255)
          );

          create table point (
            id integer primary key autoincrement,
            metric_id int,
            value varchar(255),
            created datetime
          );
        ''')


def get_points(conn, metric):
    c = conn.cursor()
    c.execute('select id from metric where name = (?)', [metric])
    row = c.fetchone()
    if not row:
        return []
    metric_id = row[0]
    return c.execute('select created, value from point where metric_id = (?)'
                     'order by created',
                     [metric_id]).fetchall()


def set_point(conn, metric, value, dt):
    c = conn.cursor()
    c.execute('select id from metric where name = (?)', [metric])
    row = c.fetchone()
    if not row:
        c.execute('insert into metric values (null, ?)', [metric])
        metric_id = c.lastrowid
    else:
        metric_id = row[0]
    if dt:
        dt = dateutil.parser.parse(dt)
    else:
        dt = datetime.datetime.now()
    c.execute('insert into point values (null, ?, ?, ?)',
              [metric_id, value, dt])
    conn.commit()
